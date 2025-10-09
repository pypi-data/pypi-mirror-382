"""
HLA-Compass CLI for module development
"""

import copy
import os
import sys
import json
import shutil
import subprocess
import uuid
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import importlib
import importlib.util

import click
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
)
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.panel import Panel
from rich.table import Table
import logging

from . import __version__
from .testing import ModuleTester
from .auth import Auth
from .config import Config
from .signing import ModuleSigner
from .mcp import build_mcp_descriptor
from .client import APIClient

try:  # pragma: no cover - Python <3.8 compatibility
    import importlib.metadata as importlib_metadata
except Exception:  # pragma: no cover
    import importlib_metadata  # type: ignore


OPTIONAL_DEP_GROUPS = {
    "wizard": {
        "modules": ["questionary", "jinja2"],
        "extra": "wizard",
        "description": "Module wizard (interactive scaffolding)",
    },
    "devserver": {
        "modules": ["watchdog", "aiohttp"],
        "extra": "devserver",
        "description": "Hot-reload dev server",
    },
    "data": {
        "modules": ["pandas", "xlsxwriter"],
        "extra": "data",
        "description": "Data exports (CSV/Excel)",
    },
    "ml": {
        "modules": ["scikit-learn", "torch", "transformers"],
        "extra": "ml",
        "description": "ML inference helpers",
    },
}

console = Console()


VERBOSE_MODE = False
_VERBOSE_INITIALIZED = False


def _deprecated_compute_option(
    _ctx: click.Context, _param: click.Option, value: Optional[str]
) -> None:
    """Warn when the legacy --compute flag is used."""

    if value is None:
        return

    if value and value.lower() != "docker":
        console.print(
            "[yellow]⚠️ The `--compute` option is no longer supported; modules now "
            "always build for Docker runtimes. Ignoring requested compute type "
            f"'{value}'.[/yellow]"
        )
    else:
        console.print(
            "[yellow]⚠️ The `--compute` option is deprecated; Docker is the "
            "default runtime and no extra flag is required.[/yellow]"
        )


def _enable_verbose(ctx: Optional[click.Context] = None):
    """Turn on verbose logging globally and remember the state."""
    global VERBOSE_MODE, _VERBOSE_INITIALIZED
    VERBOSE_MODE = True
    if ctx is not None:
        ctx.ensure_object(dict)
        ctx.obj["verbose"] = True

    if not _VERBOSE_INITIALIZED:
        logging.basicConfig(level=logging.DEBUG)
        _VERBOSE_INITIALIZED = True
        console.log("Verbose mode enabled")

    logging.getLogger().setLevel(logging.DEBUG)


def _ensure_verbose(ctx: Optional[click.Context] = None):
    """Apply verbose mode when previously enabled on the parent context."""
    if ctx is None:
        return
    ctx.ensure_object(dict)
    if ctx.obj.get("verbose"):
        _enable_verbose(ctx)


def _handle_command_verbose(ctx: click.Context, _param: click.Option, value: bool):
    if value:
        _enable_verbose(ctx)
    return value


def _parse_image_reference(image: str) -> tuple[str | None, str | None]:
    """Return (repository, tag) tuple from an OCI image reference."""

    if not image:
        return None, None

    reference = image.split("@", 1)[0]
    last_segment = reference.rsplit("/", 1)[-1]
    if ":" in last_segment:
        repo_candidate, tag_candidate = reference.rsplit(":", 1)
        if "/" in tag_candidate:
            return reference, None
        return repo_candidate, tag_candidate
    return reference, None


def verbose_option(command):
    """Decorator to add --verbose flag to commands."""
    return click.option(
        "--verbose",
        is_flag=True,
        expose_value=False,
        is_eager=True,
        help="Enable verbose logging output for troubleshooting",
        callback=_handle_command_verbose,
    )(command)


def load_sdk_config() -> Optional[Dict[str, Any]]:
    """Load SDK configuration from config file"""
    try:
        config_path = Config.get_config_path()
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)
    except Exception:
        pass
    return None


@click.group()
@click.option(
    "--verbose",
    is_flag=True,
    help="Enable verbose logging output for troubleshooting",
)
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx: click.Context, verbose: bool):
    """HLA-Compass SDK - Module development tools"""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = bool(verbose)
    if verbose:
        _enable_verbose(ctx)
    else:
        logging.getLogger().setLevel(logging.INFO)


@cli.group()
def auth():
    """Authentication and credential management
    
    Manage your HLA-Compass platform credentials for publishing modules.
    """
    pass


@auth.command("login")
@click.option("--env", 
              type=click.Choice(["dev", "staging", "prod"]), 
              default="dev",
              help="Target environment")
@click.option("--email", 
              prompt="Email", 
              help="Your email address")
@click.option("--password", 
              prompt=True, 
              hide_input=True,
              help="Your password")
def auth_login(env: str, email: str, password: str):
    """Login to HLA-Compass platform
    
    Authenticate with the platform and store credentials securely.
    Required before publishing modules.
    
    Example:
        hla-compass auth login --env dev
    """
    console = Console()
    
    try:
        auth_client = Auth()
        auth_client.login(email=email, password=password, environment=env)
        
        console.print(f"[green]✓[/green] Successfully logged in to {env} environment")
        console.print(f"[dim]Email: {email}[/dim]")
        console.print(f"[dim]Credentials stored in: {Config.get_credentials_path()}[/dim]")
        
    except Exception as e:
        console.print(f"[red]✗ Login failed:[/red] {e}")
        raise click.Abort()


@auth.command("logout")
def auth_logout():
    """Logout and clear stored credentials
    
    Remove all stored authentication tokens from your system.
    
    Example:
        hla-compass auth logout
    """
    console = Console()
    
    try:
        auth_client = Auth()
        auth_client.logout()
        console.print("[green]✓[/green] Successfully logged out")
        console.print("[dim]All credentials have been cleared[/dim]")
        
    except Exception as e:
        console.print(f"[yellow]Warning:[/yellow] {e}")


@auth.command("status")
def auth_status():
    """Show current authentication status
    
    Display information about your current login status and credentials.
    
    Example:
        hla-compass auth status
    """
    console = Console()
    
    try:
        auth_client = Auth()
        is_authed = auth_client.is_authenticated()
        
        table = Table(title="Authentication Status")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green" if is_authed else "red")
        
        table.add_row("Authenticated", "Yes" if is_authed else "No")
        table.add_row("Environment", Config.get_environment())
        table.add_row("API Endpoint", Config.get_api_endpoint())
        table.add_row("Credentials Path", str(Config.get_credentials_path()))
        
        if is_authed:
            table.add_row("Token Status", "Valid")
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


@cli.command()
@verbose_option
@click.option("--json", "output_json", is_flag=True, help="Emit diagnostics as JSON")
def doctor(output_json: bool):
    """Run environment diagnostics and suggest next steps."""
    results = _run_doctor_checks()

    if output_json:
        console.print(json.dumps(results, indent=2, default=str))
        return

    _render_doctor_results(results)


def _run_doctor_checks() -> Dict[str, Any]:
    auth = Auth()
    config_dir = Config.get_config_dir()
    env = Config.get_environment()
    api = Config.get_api_endpoint()

    rate_limit_settings = Config.get_rate_limit_settings()
    rate_limit_env = {
        "HLA_RATE_LIMIT_MAX_REQUESTS": os.getenv("HLA_RATE_LIMIT_MAX_REQUESTS"),
        "HLA_RATE_LIMIT_TIME_WINDOW": os.getenv("HLA_RATE_LIMIT_TIME_WINDOW"),
    }

    auth_status = {
        "authenticated": auth.is_authenticated(),
        "credentials_path": str(Config.get_credentials_path()),
        "config_dir": str(config_dir),
    }

    tooling = {
        "docker": _command_available(["docker", "version"]),
        "node": _command_available(["node", "--version"]),
        "npm": _command_available(["npm", "--version"]),
    }

    optional_deps: List[Dict[str, Any]] = []
    for group, data in OPTIONAL_DEP_GROUPS.items():
        modules_info = []
        available = True
        for module_name in data["modules"]:
            status = _inspect_dependency(module_name)
            modules_info.append(status)
            if not status["available"]:
                available = False
        optional_deps.append(
            {
                "group": group,
                "description": data["description"],
                "extra": data["extra"],
                "available": available,
                "modules": modules_info,
            }
        )

    next_steps: List[str] = []
    if not auth_status["authenticated"]:
        next_steps.append("Run 'hla-compass auth login' to authenticate with the platform.")

    if not tooling["docker"]["available"]:
        next_steps.append("Install and start Docker to build and run module containers.")

    for dep in optional_deps:
        if not dep["available"]:
            next_steps.append(
                f"Install missing {dep['description']} dependencies with: pip install 'hla-compass[{dep['extra']}]'"
            )

    if not any(rate_limit_env.values()):
        next_steps.append(
            "Set HLA_RATE_LIMIT_MAX_REQUESTS / HLA_RATE_LIMIT_TIME_WINDOW to tune client throughput (optional)."
        )

    return {
        "environment": {
            "sdk_version": __version__,
            "environment": env,
            "api_endpoint": api,
        },
        "auth": auth_status,
        "rate_limits": {
            "env": rate_limit_env,
            "effective": rate_limit_settings,
        },
        "tooling": tooling,
        "optional_dependencies": optional_deps,
        "next_steps": next_steps,
    }




def _command_available(cmd: List[str]) -> Dict[str, Any]:
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        available = result.returncode == 0
        version = result.stdout.strip() or result.stderr.strip()
        return {"available": available, "output": version}
    except FileNotFoundError:
        return {"available": False, "output": "not installed"}

def _inspect_dependency(module_name: str) -> Dict[str, Any]:
    spec = importlib.util.find_spec(module_name)
    available = spec is not None
    version = None
    if available:
        try:
            version = importlib_metadata.version(module_name)
        except importlib_metadata.PackageNotFoundError:
            version = "unknown"
    return {
        "module": module_name,
        "available": available,
        "version": version,
    }


def _render_doctor_results(results: Dict[str, Any]) -> None:
    env = results["environment"]
    auth = results["auth"]
    rate_limits = results["rate_limits"]
    deps = results["optional_dependencies"]
    next_steps = results.get("next_steps", [])

    console.print(
        Panel.fit(
            f"[bold]Environment[/bold]\n"
            f"SDK Version: [cyan]{env['sdk_version']}[/cyan]\n"
            f"Environment: [cyan]{env['environment']}[/cyan]\n"
            f"API Endpoint: [cyan]{env['api_endpoint']}[/cyan]",
            title="hla-compass doctor",
            border_style="bright_cyan",
        )
    )

    auth_msg = (
        "Authenticated ✅" if auth["authenticated"] else "Not authenticated ❌"
    )
    console.print(
        Panel.fit(
            f"[bold]Authentication[/bold]\n"
            f"Status: {auth_msg}\n"
            f"Config dir: {auth['config_dir']}\n"
            f"Credentials file: {auth['credentials_path']}",
            border_style="green" if auth["authenticated"] else "red",
        )
    )

    rate_table = Table(title="Rate Limit Settings", show_header=True, header_style="bold")
    rate_table.add_column("Variable")
    rate_table.add_column("Value")
    for key, value in rate_limits["env"].items():
        rate_table.add_row(key, str(value) if value else "<not set>")
    rate_table.add_row(
        "effective.max_requests",
        str(rate_limits["effective"].get("max_requests", "default")),
    )
    rate_table.add_row(
        "effective.time_window",
        str(rate_limits["effective"].get("time_window", "default")),
    )
    console.print(rate_table)

    tooling = results["tooling"]
    tooling_table = Table(title="Tooling", show_header=True, header_style="bold")
    tooling_table.add_column("Tool")
    tooling_table.add_column("Status")
    tooling_table.add_column("Details")
    for name, info in tooling.items():
        status = "✅" if info["available"] else "⚠️"
        details = info.get("output") or ""
        tooling_table.add_row(name, status, details)
    console.print(tooling_table)

    dep_table = Table(title="Optional Dependencies", show_header=True, header_style="bold")
    dep_table.add_column("Group")
    dep_table.add_column("Status")
    dep_table.add_column("Modules")
    dep_table.add_column("Install Hint")

    for dep in deps:
        status = "✅" if dep["available"] else "⚠️"
        modules = ", ".join(
            f"{m['module']}({m['version']})" if m["available"] else f"{m['module']} (missing)"
            for m in dep["modules"]
        )
        hint = "—" if dep["available"] else f"pip install 'hla-compass[{dep['extra']}]'"
        dep_table.add_row(dep["description"], status, modules, hint)

    console.print(dep_table)

    if next_steps:
        console.print("\n[bold]Next steps:[/bold]")
        for step in next_steps:
            console.print(f"  • {step}")
    else:
        console.print("\n[bold green]All checks passed. You're ready to build![/bold green]")


ALITHEA_BANNER = """
        [bold bright_magenta]█████╗[/bold bright_magenta] [bold bright_cyan]██╗[/bold bright_cyan]     [bold bright_green]██╗[/bold bright_green][bold bright_yellow]████████╗[/bold bright_yellow][bold bright_red]██╗  ██╗[/bold bright_red][bold bright_magenta]███████╗[/bold bright_magenta] [bold bright_cyan]█████╗[/bold bright_cyan]
       [bold bright_magenta]██╔══██╗[/bold bright_magenta][bold bright_cyan]██║[/bold bright_cyan]     [bold bright_green]██║[/bold bright_green][bold bright_yellow]╚══██╔══╝[/bold bright_yellow][bold bright_red]██║  ██║[/bold bright_red][bold bright_magenta]██╔════╝[/bold bright_magenta][bold bright_cyan]██╔══██╗[/bold bright_cyan]
       [bold bright_magenta]███████║[/bold bright_magenta][bold bright_cyan]██║[/bold bright_cyan]     [bold bright_green]██║[/bold bright_green][bold bright_yellow]   ██║[/bold bright_yellow]   [bold bright_red]███████║[/bold bright_red][bold bright_magenta]█████╗[/bold bright_magenta]  [bold bright_cyan]███████║[/bold bright_cyan]
       [bold bright_magenta]██╔══██║[/bold bright_magenta][bold bright_cyan]██║[/bold bright_cyan]     [bold bright_green]██║[/bold bright_green][bold bright_yellow]   ██║[/bold bright_yellow]   [bold bright_red]██╔══██║[/bold bright_red][bold bright_magenta]██╔══╝[/bold bright_magenta]  [bold bright_cyan]██╔══██║[/bold bright_cyan]
       [bold bright_magenta]██║  ██║[/bold bright_magenta][bold bright_cyan]███████╗[/bold bright_cyan][bold bright_green]██║[/bold bright_green][bold bright_yellow]   ██║[/bold bright_yellow]   [bold bright_red]██║  ██║[/bold bright_red][bold bright_magenta]███████╗[/bold bright_magenta][bold bright_cyan]██║  ██║[/bold bright_cyan]
       [bold bright_magenta]╚═╝  ╚═╝[/bold bright_magenta][bold bright_cyan]╚══════╝[/bold bright_cyan][bold bright_green]╚═╝[/bold bright_green][bold bright_yellow]   ╚═╝[/bold bright_yellow]   [bold bright_red]╚═╝  ╚═╝[/bold bright_red][bold bright_magenta]╚══════╝[/bold bright_magenta][bold bright_cyan]╚═╝  ╚═╝[/bold bright_cyan]

                  [bold bright_white]🧬  B I O I N F O R M A T I C S  🧬[/bold bright_white]
"""


def show_banner():
    """Display the Alithea banner with helpful context"""
    console.print(ALITHEA_BANNER)
    env = Config.get_environment()
    api = Config.get_api_endpoint()

    # Color-coded environment indicator
    env_color = {"dev": "green", "staging": "yellow", "prod": "red"}.get(env, "cyan")

    info = (
        f"[bold bright_white]HLA-Compass Platform SDK[/bold bright_white]\n"
        f"[dim white]Version[/dim white] [bold bright_cyan]{__version__}[/bold bright_cyan]   "
        f"[dim white]Environment[/dim white] [bold {env_color}]{env.upper()}[/bold {env_color}]\n"
        f"[dim white]API Endpoint[/dim white] [bright_blue]{api}[/bright_blue]\n"
        f"[bright_magenta]✨[/bright_magenta] [italic]Immuno-Peptidomics • Module Development • AI-Powered Analysis[/italic] [bright_magenta]✨[/bright_magenta]"
    )
    console.print(
        Panel.fit(
            info,
            title="[bold bright_cyan]🔬 Alithea Bio[/bold bright_cyan]",
            subtitle="[bright_blue]https://alithea.bio[/bright_blue]",
            border_style="bright_cyan",
            padding=(1, 2),
        )
    )


@cli.command()
@verbose_option
@click.option("--force", is_flag=True, help="Overwrite existing configuration and keys")
@click.option(
    "--env",
    type=click.Choice(["dev", "staging", "prod"]),
    default="dev",
    help="Default environment",
)
@click.option(
    "--api-endpoint", help="Custom API endpoint (overrides environment default)"
)
@click.option("--organization", help="Your organization name")
@click.option("--author-name", help="Your name for module authorship")
@click.option("--author-email", help="Your email for module authorship")
@click.pass_context
def configure(
    ctx: click.Context,
    force: bool,
    env: str,
    api_endpoint: str | None,
    organization: str | None,
    author_name: str | None,
    author_email: str | None,
):
    """Set up initial SDK configuration and generate RSA keypair for signing"""
    _ensure_verbose(ctx)
    console.print("[bold blue]HLA-Compass SDK Configuration[/bold blue]\n")

    # Get configuration directory
    config_path = Config.get_config_path()

    # Check if configuration already exists
    if config_path.exists() and not force:
        console.print(f"[yellow]Configuration already exists at {config_path}[/yellow]")
        if not Confirm.ask("Do you want to update the existing configuration?"):
            console.print("Configuration cancelled.")
            return
        force = True

    try:
        # Initialize module signer
        signer = ModuleSigner()

        # Check for existing keys
        keys_exist = (
            signer.private_key_path.exists() and signer.public_key_path.exists()
        )

        if keys_exist and not force:
            console.print(
                f"[yellow]RSA keypair already exists at {signer.keys_dir}[/yellow]"
            )
            regenerate_keys = Confirm.ask("Do you want to regenerate the RSA keypair?")
        else:
            regenerate_keys = True

        # Generate or regenerate keys if needed
        if regenerate_keys:
            console.print("🔐 Generating RSA keypair for module signing...")
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(
                    "Generating 4096-bit RSA keypair...", total=None
                )

                try:
                    private_path, public_path = signer.generate_keys(force=force)
                    progress.update(task, description="Keys generated successfully!")
                    console.print(f"  ✓ Private key: {private_path}")
                    console.print(f"  ✓ Public key: {public_path}")
                    console.print(
                        f"  ✓ Key fingerprint: {signer.get_key_fingerprint()}"
                    )
                except Exception as e:
                    console.print(f"[red]Error generating keys: {e}[/red]")
                    sys.exit(1)
        else:
            console.print(f"✓ Using existing RSA keypair at {signer.keys_dir}")
            console.print(f"  Key fingerprint: {signer.get_key_fingerprint()}")

        # Collect configuration parameters
        console.print("\n[bold]Configuration Setup[/bold]")

        # Use provided values or prompt for input
        if not api_endpoint:
            api_endpoint = Config.API_ENDPOINTS.get(env)

        if not organization:
            organization = Prompt.ask(
                "Organization name",
                default=os.environ.get("HLA_AUTHOR_ORG", "Independent"),
            )

        if not author_name:
            author_name = Prompt.ask(
                "Your name (for module authorship)",
                default=os.environ.get(
                    "HLA_AUTHOR_NAME", os.environ.get("USER", "Developer")
                ),
            )

        if not author_email:
            author_email = Prompt.ask(
                "Your email (for module authorship)",
                default=os.environ.get(
                    "HLA_AUTHOR_EMAIL",
                    f"{author_name.lower().replace(' ', '.')}@example.com",
                ),
            )

        # Create configuration
        config_data = {
            "version": "1.0",
            "environment": env,
            "api_endpoint": api_endpoint,
            "organization": organization,
            "author": {"name": author_name, "email": author_email},
            "signing": {
                "algorithm": signer.ALGORITHM,
                "hash_algorithm": signer.HASH_ALGORITHM,
                "key_fingerprint": signer.get_key_fingerprint(),
                "private_key_path": str(signer.private_key_path),
                "public_key_path": str(signer.public_key_path),
            },
        }

        # Add timestamp
        import datetime

        config_data["created_at"] = datetime.datetime.now().isoformat()

        # Save configuration
        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=2)

        console.print(f"\n[green]✓ Configuration saved to {config_path}[/green]\n")

        # Display configuration summary
        config_table = Table(title="SDK Configuration Summary")
        config_table.add_column("Setting", style="cyan")
        config_table.add_column("Value", style="white")

        config_table.add_row("Environment", env)
        config_table.add_row("API Endpoint", api_endpoint)
        config_table.add_row("Organization", organization)
        config_table.add_row("Author", f"{author_name} <{author_email}>")
        config_table.add_row("Keys Directory", str(signer.keys_dir))
        config_table.add_row(
            "Signing Algorithm", f"{signer.ALGORITHM} with {signer.HASH_ALGORITHM}"
        )

        console.print(config_table)

        console.print("\n[bold]Next Steps:[/bold]")
        console.print("• Create a module: [cyan]hla-compass init my-module[/cyan]")
        console.print("• Build and sign: [cyan]hla-compass build[/cyan]")
        console.print("• Publish to platform: [cyan]hla-compass publish[/cyan]")

    except Exception as e:
        console.print(f"[red]Configuration failed: {e}[/red]")
        sys.exit(1)


@cli.command()
@verbose_option
@click.argument("name", required=False)
@click.option(
    "--template",
    type=click.Choice(["ui", "no-ui"]),
    default="no-ui",
    help="Module template: 'ui' for modules with user interface, 'no-ui' for backend-only (default: no-ui)"
)
@click.option(
    "--interactive", "-i",
    is_flag=True,
    help="Use interactive wizard to create module with custom configuration"
)
@click.option(
    "--compute",
    hidden=True,
    callback=_deprecated_compute_option,
    expose_value=False,
)
@click.option("--no-banner", is_flag=True, help="Skip the Alithea banner display")
@click.option(
    "--yes", is_flag=True, help="Assume yes for all prompts (non-interactive mode)"
)
@click.pass_context
def init(
    ctx: click.Context,
    name: str | None,
    template: str,
    interactive: bool,
    no_banner: bool,
    yes: bool,
):
    """Create a new HLA-Compass module

    Examples:
        hla-compass init my-module # Backend-only module (no UI)
        hla-compass init my-module --template ui # Module with user interface
        hla-compass init --interactive                # Interactive wizard (recommended)
        hla-compass init my-module -i # Interactive wizard with name
    """
    _ensure_verbose(ctx)

    # Show the beautiful Alithea banner only during module creation
    if not no_banner:
        show_banner()
    
    # Use an interactive wizard if requested
    if interactive:
        try:
            from .wizard import run_wizard
            from .generators import CodeGenerator
        except ModuleNotFoundError as exc:
            if exc.name in {"questionary", "jinja2"}:
                console.print(
                    "[red]Interactive wizard dependencies are not installed.[/red] "
                    "Install them with `[bold]pip install 'hla-compass[wizard]'[/bold]` "
                    "or `pip install questionary jinja2` and re-run `hla-compass init -i`."
                )
                return
            raise
        
        console.print("[bold cyan]🎯 Starting Interactive Module Wizard[/bold cyan]\n")
        
        # Run the wizard
        config = run_wizard()
        if not config:
            console.print("[yellow]Module creation cancelled[/yellow]")
            return
        
        # Use the provided name if given, otherwise use wizard name
        if name:
            config['name'] = name
        module_name = config['name']
        
        # Create module directory
        module_dir = Path(module_name)
        if module_dir.exists() and not yes:
            if not Confirm.ask(f"Directory '{module_name}' already exists. Continue?"):
                return
        
        # Generate module from wizard configuration
        generator = CodeGenerator()
        success = generator.generate_module(config, module_dir)
        
        if success:
            console.print(Panel.fit(
                f"[green]✓ Module '{module_name}' created successfully![/green]\n\n"
                f"[bold]Generated from wizard configuration:[/bold]\n"
                f"• Type: {'UI Module' if config.get('has_ui') else 'Backend Module'}\n"
                f"• Inputs: {len(config.get('inputs', {}))} parameters\n"
                f"• Outputs: {len(config.get('outputs', {}))} fields\n"
                f"• Dependencies: {len(config.get('dependencies', []))} packages\n\n"
                f"[bold]Next steps:[/bold]\n"
                f"1. cd {module_name}\n"
                f"2. pip install -r backend/requirements.txt\n"
                f"3. hla-compass dev  # Start hot-reload server\n\n"
                f"[dim]The wizard has generated working code based on your specifications.\n"
                f"Edit backend/main.py to customize the processing logic.[/dim]",
                title="Module Created with Wizard",
                border_style="green",
                width=100
            ))
        else:
            console.print("[red]Failed to generate module from wizard configuration[/red]")
        return
    
    # Standard template-based creation (non-interactive)
    if not name:
        console.print("[red]Module name is required when not using --interactive[/red]")
        console.print("Usage: hla-compass init MODULE_NAME")
        console.print("   Or: hla-compass init --interactive")
        return

    # Determine a module type from the template
    module_type = "with-ui" if template == "ui" else "no-ui"
    
    # Map template names to actual template directories
    template_dir_name = f"{template}-template"

    console.print(
        f"[bold green]🧬 Creating HLA-Compass Module: [white]{name}[/white] 🧬[/bold green]"
    )
    console.print(
        f"[dim]Template: {template} • Type: {module_type} • Runtime: Docker container[/dim]\n"
    )

    # Check if the directory already exists
    module_dir = Path(name)
    if module_dir.exists():
        if not yes and not Confirm.ask(f"Directory '{name}' already exists. Continue?"):
            return

    # Find template directory
    pkg_templates_dir = Path(__file__).parent / "templates" / template_dir_name
    
    if not pkg_templates_dir.exists():
        console.print(f"[red]Template '{template}' not found[/red]")
        console.print("[yellow]Available templates:[/yellow]")
        console.print("  • no-ui - Backend-only module without user interface")
        console.print("  • ui    - Module with React/TypeScript user interface")
        return
    
    template_dir = pkg_templates_dir

    # Copy template
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Copying template files...", total=None)

        shutil.copytree(template_dir, module_dir, dirs_exist_ok=True)

        progress.update(task, description="Updating manifest...")

        # Update manifest.json
        manifest_path = module_dir / "manifest.json"
        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        manifest["name"] = name
        manifest["type"] = module_type
        manifest["computeType"] = "docker"

        # Load author information from SDK config, then environment, then defaults
        sdk_config = load_sdk_config()
        author_info = sdk_config.get("author", {}) if sdk_config else {}

        manifest["author"]["name"] = (
            author_info.get("name") or
            os.environ.get("HLA_AUTHOR_NAME") or
            os.environ.get("USER", "Unknown")
        )
        manifest["author"]["email"] = author_info.get("email") or os.environ.get(
            "HLA_AUTHOR_EMAIL", "developer@example.com"
        )
        manifest["author"]["organization"] = (
            sdk_config.get("organization") if sdk_config else None
        ) or os.environ.get("HLA_AUTHOR_ORG", "Independent")
        manifest["description"] = os.environ.get(
            "HLA_MODULE_DESC", f"HLA-Compass module: {name}"
        )

        # Show what was set
        console.print(f"  Author: {manifest['author']['name']}")
        console.print(f"  Email: {manifest['author']['email']}")
        console.print(f"  Organization: {manifest['author']['organization']}")

        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        # Remove the frontend directory if no-ui
        if module_type == "no-ui":
            frontend_dir = module_dir / "frontend"
            if frontend_dir.exists():
                shutil.rmtree(frontend_dir)

        # Create a virtual environment only if not already in one
        if hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        ):
            progress.update(
                task, description="Skipping venv (already in virtual environment)..."
            )
        else:
            progress.update(task, description="Creating virtual environment...")
            result = subprocess.run(
                [sys.executable, "-m", "venv", str(module_dir / "venv")],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                console.print(
                    f"[red]Failed to create virtual environment.[/red]\n"
                    f"stdout: {result.stdout or '<<empty>>'}"
                )
                if result.stderr:
                    console.print(f"[red]stderr:[/red] {result.stderr}")
                console.print(
                    "[yellow]Resolve the venv issue (ensure 'venv' module is available) and rerun 'hla-compass init'.[/yellow]"
                )
                sys.exit(result.returncode)

        progress.update(task, description="Module created!", completed=True)

    # Display a comprehensive success message with full workflow
    ui_specific = ""
    if module_type == "with-ui":
        ui_specific = (
            f"• Edit frontend/index.tsx for UI components\n"
            f"• Install frontend deps: cd frontend && npm install\n"
        )
    
    console.print(
        Panel.fit(
            f"[green]✓ Module '{name}' created successfully![/green]\n\n"
            f"[bold]Template Type:[/bold] {template.upper()} ({'With UI' if module_type == 'with-ui' else 'Backend-only'})\n\n"
            f"[bold]Quick Start:[/bold]\n"
            f"1. cd {name}\n"
            f"2. pip install -r backend/requirements.txt  # Install Python dependencies\n"
            f"3. hla-compass test                         # Test locally\n\n"
            f"[bold]Development:[/bold]\n"
            f"• Edit backend/main.py to implement your logic\n"
            f"{ui_specific}"
            f"• Add test data to examples/sample_input.json\n"
            f"• Test: hla-compass test --input examples/sample_input.json\n\n"
            f"[bold]Deployment:[/bold]\n"
            f"• Configure: hla-compass configure\n"
            f"• Build: hla-compass build\n"
            f"• Publish: hla-compass publish --env dev\n\n"
            f"[bold]Documentation:[/bold]\n"
            f"• Templates guide: sdk/python/hla_compass/templates/README.md\n"
            f"• SDK docs: https://docs.alithea.bio",
            title=f"Module Created - {'UI' if module_type == 'with-ui' else 'No-UI'} Template",
            width=100,
        )
    )


@cli.command()
@verbose_option
@click.option("--manifest", default="manifest.json", help="Path to manifest.json")
@click.option(
    "--json", "output_json", is_flag=True, help="Output as JSON for automation"
)
@click.pass_context
def validate(ctx: click.Context, manifest: str, output_json: bool):
    """Validate manifest.json schema and module structure (schema-only, no execution).
    
    This command checks:
    - Required fields in manifest.json (name, version, type, etc.)
    - File structure (backend/main.py, frontend/ for with-ui modules)
    - JSON syntax and basic types
    
    It does NOT:
    - Execute your module code
    - Check runtime dependencies or imports
    - Run tests or verify behavior
    
    Progressive validation ladder:
        hla-compass validate                 # schema-only; no Docker
        hla-compass test                     # run locally (fast)
        hla-compass test --docker            # containerized test (parity)
        hla-compass dev                      # interactive container development
    
    For runtime verification, use 'test' (fast local) or 'dev' (container parity).
    """
    _ensure_verbose(ctx)

    if not output_json:
        console.print("[bold]Validating module...[/bold]")

    errors = []
    warnings = []

    # Check manifest exists
    manifest_path = Path(manifest)
    if not manifest_path.exists():
        if output_json:
            result = {
                "valid": False,
                "errors": ["manifest.json not found"],
                "warnings": [],
            }
            print(json.dumps(result))
        else:
            console.print("[red]✗ manifest.json not found[/red]")
        sys.exit(1)

    # Load and validate manifest
    try:
        with open(manifest_path, "r") as f:
            manifest_data = json.load(f)
    except json.JSONDecodeError as e:
        if output_json:
            result = {
                "valid": False,
                "errors": [f"Invalid JSON in manifest.json: {e}"],
                "warnings": [],
            }
            print(json.dumps(result))
        else:
            console.print(f"[red]✗ Invalid JSON in manifest.json: {e}[/red]")
        sys.exit(1)

    # Required fields
    required_fields = [
        "name",
        "version",
        "type",
        "computeType",
        "author",
        "inputs",
        "outputs",
    ]
    for field in required_fields:
        if field not in manifest_data:
            errors.append(f"Missing required field: {field}")

    # Check backend structure
    module_dir = manifest_path.parent
    backend_dir = module_dir / "backend"

    if not backend_dir.exists():
        errors.append("backend/ directory not found")
    else:
        if not (backend_dir / "main.py").exists():
            errors.append("backend/main.py not found")
        if not (backend_dir / "requirements.txt").exists():
            warnings.append("backend/requirements.txt not found")

    # Check frontend for with-ui modules
    if manifest_data.get("type") == "with-ui":
        frontend_dir = module_dir / "frontend"
        if not frontend_dir.exists():
            errors.append("frontend/ directory required for with-ui modules")
        elif not (frontend_dir / "index.tsx").exists():
            errors.append("frontend/index.tsx not found")

    # Display results
    if output_json:
        result = {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["valid"] else 1)
    else:
        if errors:
            console.print("[red]✗ Validation failed with errors:[/red]")
            for error in errors:
                console.print(f"  • {error}")
            console.print(
                "\n[yellow]Fix the errors above, then run 'hla-compass validate' again[/yellow]"
            )
            sys.exit(1)
        else:
            console.print("[green]✓ Module structure valid[/green]")
            if warnings:
                console.print("\n[yellow]Warnings:[/yellow]")
                for warning in warnings:
                    console.print(f"  • {warning}")
            console.print("\n[bold]Ready for next steps:[/bold]")
            console.print("  • Test: hla-compass test")
            console.print("  • Build: hla-compass build")
            console.print("  • Publish: hla-compass publish --env dev")
            console.print("  • Register existing image: hla-compass publish --no-build --image-ref <image> --env dev")
            sys.exit(0)




def _sanitize_tag_component(value: str, fallback: str) -> str:
    normalized = []
    for char in value.lower():
        if char.isalnum() or char in {"-", "_", "."}:
            normalized.append(char)
        else:
            normalized.append("-")
    slug = "".join(normalized).strip("-.")
    return slug or fallback


def _default_image_tag(manifest: Dict[str, Any]) -> str:
    name = manifest.get("name") or "module"
    version = manifest.get("version") or datetime.now(UTC).strftime("%Y%m%d%H%M")
    return f"{_sanitize_tag_component(name, 'module')}:{_sanitize_tag_component(version, 'latest')}"


def _compose_registry_tag(base_tag: str, registry: str | None) -> tuple[str, str | None]:
    if not registry:
        return base_tag, None

    registry = registry.rstrip("/")
    if "//" in base_tag:
        return base_tag, base_tag
    repo = base_tag.split(":", 1)[0]
    if "/" in repo:
        return base_tag, base_tag
    return base_tag, f"{registry}/{base_tag}"


def _docker_image_metadata(image_ref: str) -> Dict[str, Any]:
    try:
        result = subprocess.run(
            [
                "docker",
                "image",
                "inspect",
                image_ref,
                "--format",
                "{{json .}}",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        return {}

    payload = result.stdout.strip()
    if not payload:
        return {}

    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return {}


def _write_dist_manifest(manifest: Dict[str, Any], dist_dir: Path) -> Path:
    manifest_path = dist_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest_path


@cli.command()
@verbose_option
@click.option("--tag", help="Docker image tag to build (defaults to <name>:<version>)")
@click.option(
    "--registry",
    help="Registry prefix used when tagging/pushing (e.g. 1234567890.dkr.ecr.us-east-1.amazonaws.com/modules)",
)
@click.option("--push", is_flag=True, help="Push the built image after docker build")
@click.option(
    "--platform",
    multiple=True,
    help="Optional target platform(s) passed to docker build --platform",
)
@click.option("--no-cache", is_flag=True, help="Disable Docker build cache")
@click.option(
    "--no-sign",
    is_flag=True,
    help="Deprecated; builds no longer sign images. Use 'hla-compass publish' to sign.",
)
@click.pass_context
def build(
    ctx: click.Context,
    tag: str | None,
    registry: str | None,
    push: bool,
    platform: tuple[str, ...],
    no_cache: bool,
    no_sign: bool,
):
    """Build a container image for the current module
    
    Creates a Docker image containing your module code. Does NOT sign or register.
    Use 'hla-compass publish' after building to sign and register with platform.
    
    Workflow:
        hla-compass build --tag my-module:1.0.0
        hla-compass publish --env dev --image-ref my-module:1.0.0
    
    Example:
        hla-compass build --tag my-module:1.0.0 --push
    """

    _ensure_verbose(ctx)
    _ensure_docker_available()

    if no_sign:
        console.print(
            "[yellow]`--no-sign` is no longer required; images are unsigned during build. Signing happens in `hla-compass publish`.[/yellow]"
        )

    missing_devserver = [
        pkg
        for pkg in OPTIONAL_DEP_GROUPS["devserver"]["modules"]
        if importlib.util.find_spec(pkg) is None
    ]
    if missing_devserver:
        console.print(
            "[yellow]Hot-reload dev server extras missing ({}). Install with `pip install 'hla-compass[devserver]'` to enable file watching and proxy helpers.[/yellow]".format(
                ", ".join(sorted(missing_devserver))
            )
        )

    manifest_path = Path("manifest.json")
    if not manifest_path.exists():
        console.print("[red]manifest.json not found. Run this command from your module directory.")
        sys.exit(1)

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        console.print(f"[red]Invalid manifest.json: {exc}[/red]")
        sys.exit(1)

    working_manifest = copy.deepcopy(manifest)
    image_tag = tag or _default_image_tag(working_manifest)
    local_tag, registry_tag = _compose_registry_tag(image_tag, registry)

    dist_dir = Path("dist")
    dist_dir.mkdir(parents=True, exist_ok=True)
    _write_container_serve_script(dist_dir)
    mcp_dir = dist_dir / "mcp"

    descriptor_path = build_mcp_descriptor(working_manifest, mcp_dir)
    dockerfile_path = dist_dir / "Dockerfile.hla"
    dockerfile_path.write_text(
        _generate_dockerfile_content(working_manifest, descriptor_path),
        encoding="utf-8",
    )

    execution = working_manifest.setdefault("execution", {})
    execution.setdefault(
        "entrypoint",
        execution.get("entrypoint")
        or working_manifest.get("entrypoint")
        or "backend.main:Module",
    )
    execution.setdefault("supports", ["interactive", "async", "workflow"])
    execution.setdefault("defaultMode", "interactive")
    execution["image"] = registry_tag or local_tag

    manifest_artifact = _write_dist_manifest(working_manifest, dist_dir)

    console.print("[cyan]Building Docker image...[/cyan]")
    build_cmd = ["docker", "build"]
    if platform:
        build_cmd.extend(["--platform", ",".join(platform)])
    if no_cache:
        build_cmd.append("--no-cache")
    build_cmd.extend(["-f", str(dockerfile_path), "-t", local_tag, "."])

    result = subprocess.run(build_cmd)
    if result.returncode != 0:
        console.print("[red]Docker build failed[/red]")
        sys.exit(result.returncode)

    published_tag = local_tag
    if registry_tag and registry_tag != local_tag:
        tag_cmd = ["docker", "tag", local_tag, registry_tag]
        tag_result = subprocess.run(tag_cmd)
        if tag_result.returncode != 0:
            console.print("[red]Failed to tag image for registry push[/red]")
            sys.exit(tag_result.returncode)
        published_tag = registry_tag

    pushed = False
    if push:
        console.print(f"[cyan]Pushing image {published_tag}...[/cyan]")
        push_result = subprocess.run(["docker", "push", published_tag])
        if push_result.returncode != 0:
            console.print("[red]Docker push failed[/red]")
            sys.exit(push_result.returncode)
        pushed = True

    image_meta = _docker_image_metadata(published_tag)
    digest = None
    if image_meta:
        repo_digests = image_meta.get("RepoDigests") or []
        digest = repo_digests[0] if repo_digests else image_meta.get("Id")

    build_report = {
        "image_tag": local_tag,
        "published_tag": published_tag,
        "pushed": pushed,
        "descriptor": str(descriptor_path),
        "manifest": str(manifest_artifact),
        "digest": digest,
        "timestamp": _utc_now_iso(),
    }
    (dist_dir / "build.json").write_text(json.dumps(build_report, indent=2), encoding="utf-8")

    summary = Table(title="Build Summary")
    summary.add_column("Item", style="cyan")
    summary.add_column("Value", overflow="fold")
    summary.add_row("Image", published_tag)
    summary.add_row("Local Tag", local_tag)
    summary.add_row("Descriptor", str(descriptor_path))
    summary.add_row("Manifest", str(manifest_artifact))
    summary.add_row("Pushed", "Yes" if pushed else "No")
    if digest:
        summary.add_row("Digest", digest)

    console.print(summary)

    return {
        "manifest": working_manifest,
        "manifest_path": manifest_artifact,
        "descriptor_path": descriptor_path,
        "image_tag": local_tag,
        "published_tag": published_tag,
        "pushed": pushed,
        "digest": digest,
    }


@cli.command()
@verbose_option
@click.option("--mode", type=click.Choice(["interactive", "async", "workflow"]), default="interactive", help="Execution mode to simulate")
@click.option("--image-tag", help="Custom image tag to run (defaults to {name}:dev)")
@click.option("--payload", type=click.Path(path_type=Path), help="Path to payload JSON file (defaults to generated manifest defaults)")
@click.pass_context
def dev(ctx: click.Context, mode: str, image_tag: str | None, payload: Path | None):
    """Run the module in Docker with live mounts for rapid iteration.
    
    This command provides the authoritative parity check before publishing.
    It builds a container image and runs your module with mounted manifest
    and backend code, allowing you to edit files and press Enter to re-run.
    
    The container matches the production runtime environment (Python 3.11 base,
    backend/requirements.txt installed). Use this for final validation before
    running 'hla-compass publish'.
    
    Environment variables are passed through (HLA_ACCESS_TOKEN, AWS credentials, etc.)
    and you can add extra overrides via HLA_COMPASS_DEV_ENV="KEY=value,KEY2=value2".
    """

    _ensure_verbose(ctx)
    _ensure_docker_available()

    manifest_path = Path("manifest.json")
    if not manifest_path.exists():
        console.print("[red]manifest.json not found. Run this command from your module directory.")
        sys.exit(1)

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        console.print(f"[red]Invalid manifest.json: {exc}[/red]")
        sys.exit(1)

    module_name = manifest.get("name", "unknown")
    default_tag = f"{module_name}:dev"

    build_result = ctx.invoke(
        build,
        tag=image_tag or default_tag,
        registry=None,
        push=False,
        platform=(),
        no_cache=False,
    )

    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)

    payload_path = payload or dist_dir / "dev-input.json"
    if payload is None:
        payload_data = _build_default_payload(manifest)
        payload_path.write_text(json.dumps(payload_data, indent=2), encoding="utf-8")

    context_path = dist_dir / "dev-context.json"
    context_payload = {
        "job_id": "dev-job",
        "user_id": "dev-user",
        "organization_id": "dev-org",
        "mode": mode,
        "tier": "foundational",
        "execution_time": _utc_now_iso(),
    }
    context_path.write_text(json.dumps(context_payload, indent=2), encoding="utf-8")

    output_dir = dist_dir / "dev-output"
    output_dir.mkdir(exist_ok=True)

    console.print(
        Panel.fit(
            "Development run configuration",
            border_style="bright_blue",
            title="hla-compass dev",
        )
    )
    console.print(f"Payload: [cyan]{payload_path}[/cyan]")
    console.print(f"Mode: [cyan]{mode}[/cyan]")
    console.print("Edit the payload file and press Enter to re-run. Press Ctrl+C to exit.\n")

    image = (build_result or {}).get("image_tag") or image_tag or default_tag

    try:
        while True:
            rc = _run_module_container(image, manifest_path, payload_path, context_path, output_dir)
            output_file = output_dir / "output.json"
            summary_file = output_dir / "summary.json"
            if output_file.exists():
                console.print("\n[bold green]Execution output:[/bold green]")
                console.print(output_file.read_text())
            if summary_file.exists():
                console.print("\n[bold]Summary:[/bold]")
                console.print(summary_file.read_text())
            if rc != 0 and not output_file.exists():
                console.print("[red]Container run failed and produced no output.json[/red]")
                console.print("[yellow]Tip:[/yellow] Ensure your manifest 'execution.entrypoint' points to an existing class, e.g., 'backend.main:YourClass'.")
            input("\nPress Enter to re-run (Ctrl+C to exit)...")
    except KeyboardInterrupt:
        console.print("\nExiting dev loop.")


@cli.command()
@verbose_option
@click.option("--port", type=int, default=8080, help="Host port to expose the UI (container listens on 8080)")
@click.option("--image-tag", help="Custom image tag to run (defaults to {name}:dev)")
@click.pass_context
def serve(ctx: click.Context, port: int, image_tag: str | None):
    """Serve the module UI + local API from Docker (production-like)

    - Builds the image with the compiled UI bundle
    - Runs an HTTP server inside the container serving / (UI) and /api/execute
    - No host code mounts; uses the baked container image for parity
    """
    _ensure_verbose(ctx)
    _ensure_docker_available()

    manifest_path = Path("manifest.json")
    if not manifest_path.exists():
        console.print("[red]manifest.json not found. Run this command from your module directory.")
        sys.exit(1)

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        console.print(f"[red]Invalid manifest.json: {exc}[/red]")
        sys.exit(1)

    module_name = manifest.get("name", "unknown")
    default_tag = f"{module_name}:dev"

    # Ensure container-serve helper is present before building
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)
    _write_container_serve_script(dist_dir)

    # Build image (UI included if present)
    build_result = ctx.invoke(
        build,
        tag=image_tag or default_tag,
        registry=None,
        push=False,
        platform=(),
        no_cache=False,
    )

    image = (build_result or {}).get("image_tag") or image_tag or default_tag

    # Prepare docker run command; do not mount backend for parity
    cmd = [
        "docker",
        "run",
        "--rm",
        "-p",
        f"{port}:8080",
    ]

    # Pass through selected env vars (auth etc.) if present
    passthrough_env = [
        "HLA_API_KEY",
        "HLA_ACCESS_TOKEN",
        "HLA_COMPASS_ENV",
        "HLA_ENV",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_SESSION_TOKEN",
        "AWS_PROFILE",
        "AWS_REGION",
    ]
    for env_name in passthrough_env:
        value = os.getenv(env_name)
        if value:
            cmd.extend(["-e", f"{env_name}={value}"])

    # Override entrypoint to run the HTTP server
    cmd.extend(["--entrypoint", "python", image, "/app/container-serve.py"])

    if VERBOSE_MODE:
        import shlex
        secret_env = {
            "HLA_ACCESS_TOKEN",
            "HLA_API_KEY",
            "AWS_SECRET_ACCESS_KEY",
            "AWS_SESSION_TOKEN",
        }
        redacted_cmd: list[str] = []
        i = 0
        while i < len(cmd):
            part = cmd[i]
            if part == "-e" and i + 1 < len(cmd):
                kv = cmd[i + 1]
                if "=" in kv:
                    k, _ = kv.split("=", 1)
                    if k in secret_env:
                        redacted_cmd.extend(["-e", f"{k}=***"])
                        i += 2
                        continue
            redacted_cmd.append(part)
            i += 1
        console.log("docker run command:", " ".join(shlex.quote(p) for p in redacted_cmd))

    result = subprocess.run(cmd)
    if result.returncode != 0:
        console.print("[red]Serve container exited with error[/red]")
        sys.exit(result.returncode)



@cli.command()
@verbose_option
@click.option("--input", "input_path", type=click.Path(path_type=Path), help="Path to JSON payload (defaults to manifest/sample input)")
@click.option("--output", "output_path", type=click.Path(path_type=Path), help="Write test result to JSON file")
@click.option("--json", "json_output", is_flag=True, help="Print result as pretty JSON")
@click.option("--docker", "use_docker", is_flag=True, help="Run test in Docker container (slower, but matches production runtime)")
@click.pass_context
def test(ctx: click.Context, input_path: Path | None, output_path: Path | None, json_output: bool, use_docker: bool):
    """Execute the module for testing.
    
    By default, runs locally via Python ModuleTester (fast inner loop).
    Use --docker for a containerized test that matches production parity.
    
    Examples:
        hla-compass test --input examples/sample_input.json           # fast, Python-local
        hla-compass test --docker --input examples/sample_input.json  # containerized parity test
    
    For final validation before publishing, use 'hla-compass dev' which provides
    live mounts and a re-run loop in the container environment.
    """

    _ensure_verbose(ctx)

    manifest_path = Path("manifest.json")
    if not manifest_path.exists():
        console.print("[red]manifest.json not found. Run this command from your module directory.[/red]")
        sys.exit(1)

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        console.print(f"[red]Invalid manifest.json: {exc}[/red]")
        sys.exit(1)

    if input_path is not None:
        if not input_path.exists():
            console.print(f"[red]Input file not found: {input_path}[/red]")
            sys.exit(1)
        try:
            payload_data = json.loads(input_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            console.print(f"[red]Failed to parse input JSON: {exc}[/red]")
            sys.exit(1)
    else:
        payload_data = _build_default_payload(manifest)

    context_payload = {
        "job_id": "test-job" if use_docker else "local-test",
        "user_id": "test-user" if use_docker else "local",
        "organization_id": "test-org" if use_docker else "local",
        "mode": "interactive",
        "tier": "foundational",
        "execution_time": _utc_now_iso(),
    }

    module_path = Path("backend/main.py")
    if not module_path.exists():
        console.print("[red]backend/main.py not found. Generated templates always include this file; ensure you are in the module root.[/red]")
        sys.exit(1)

    # Docker mode: run containerized test for production parity
    if use_docker:
        _ensure_docker_available()
        
        module_name = manifest.get("name", "unknown")
        test_tag = f"{module_name}:test"
        
        # Build the container image
        build_result = ctx.invoke(
            build,
            tag=test_tag,
            registry=None,
            push=False,
            platform=(),
            no_cache=False,
        )
        
        # Prepare test artifacts
        dist_dir = Path("dist")
        dist_dir.mkdir(exist_ok=True)
        
        payload_path = dist_dir / "test-input.json"
        payload_path.write_text(json.dumps(payload_data, indent=2), encoding="utf-8")
        
        context_path = dist_dir / "test-context.json"
        context_path.write_text(json.dumps(context_payload, indent=2), encoding="utf-8")
        
        output_dir = dist_dir / "test-output"
        output_dir.mkdir(exist_ok=True)
        
        # Run the container
        image = (build_result or {}).get("image_tag") or test_tag
        console.print(f"[cyan]Running containerized test with {image}...[/cyan]")
        rc = _run_module_container(image, manifest_path, payload_path, context_path, output_dir)
        
        # Read results from container output
        output_file = output_dir / "output.json"
        summary_file = output_dir / "summary.json"
        
        if output_file.exists():
            result = json.loads(output_file.read_text(encoding="utf-8"))
        else:
            console.print("[red]Container did not produce output.json[/red]")
            if rc != 0:
                console.print("[yellow]Tip:[/yellow] Check your manifest 'execution.entrypoint' (e.g., 'backend.main:YourClass') and review container logs with --verbose.")
            sys.exit(1)
        
        # Write to requested output path if specified
        if output_path is not None:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
            console.print(f"[green]Result written to {output_path}[/green]")
        
        # Display results
        if json_output:
            console.print(json.dumps(result, indent=2))
        else:
            status = result.get("status", "unknown")
            console.print(
                Panel.fit(
                    json.dumps(result, indent=2),
                    title=f"Module Test Result ({status}) - Docker",
                    border_style="green" if status == "success" else "red",
                )
            )
            if summary_file.exists():
                console.print("\n[bold]Summary:[/bold]")
                console.print(summary_file.read_text())
    
    # Local mode: fast Python-local testing with drift warnings
    else:
        # Display drift warnings
        console.print("\n[yellow]⚠ Running in local Python mode (fast, but may differ from production)[/yellow]")
        console.print(f"[yellow]  • Local Python: {sys.version.split()[0]}[/yellow]")
        console.print(f"[yellow]  • Container uses: Python 3.11[/yellow]")
        
        requirements_file = Path("backend/requirements.txt")
        if requirements_file.exists():
            console.print(f"[yellow]  • Container installs backend/requirements.txt; local imports may differ[/yellow]")
        
        console.print("[yellow]  • Use --docker for containerized parity testing[/yellow]")
        console.print("[yellow]  • Use 'hla-compass dev' for interactive container development[/yellow]\n")
        
        tester = ModuleTester()

        try:
            result = tester.test_local(str(module_path), payload_data, context=context_payload)
        except Exception as exc:  # pragma: no cover - interactive failure path
            console.print(f"[red]Module test failed: {exc}[/red]")
            if VERBOSE_MODE:
                import traceback

                console.print(traceback.format_exc())
            sys.exit(1)

        if output_path is not None:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
            console.print(f"[green]Result written to {output_path}[/green]")

        if json_output:
            console.print(json.dumps(result, indent=2))
        else:
            status = result.get("status", "unknown")
            console.print(
                Panel.fit(
                    json.dumps(result, indent=2),
                    title=f"Module Test Result ({status}) - Local",
                    border_style="green" if status == "success" else "red",
                )
            )



def _ensure_docker_available() -> None:
    try:
        subprocess.run(
            ["docker", "version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except FileNotFoundError:
        console.print("[red]Docker CLI not found. Install Docker to continue.[/red]")
        sys.exit(1)
    except subprocess.CalledProcessError as exc:
        console.print("[red]Docker is not available:[/red]")
        console.print(exc.stderr)
        sys.exit(exc.returncode)


def _generate_dockerfile_content(manifest: Dict[str, Any], descriptor_path: Path) -> str:
    entrypoint = _resolve_entrypoint(manifest)
    try:
        descriptor_rel = descriptor_path.resolve().relative_to(Path.cwd())
    except ValueError:
        descriptor_rel = descriptor_path.resolve()

    frontend_dir = Path("frontend")
    has_frontend = (frontend_dir / "package.json").exists()
    frontend_lock = (frontend_dir / "package-lock.json").exists()
    frontend_yarn = (frontend_dir / "yarn.lock").exists()

    lines: list[str] = ["# syntax=docker/dockerfile:1"]

    if has_frontend:
        lines.extend(
            [
                "FROM node:20-alpine AS ui",
                "WORKDIR /ui",
                "COPY frontend/package*.json ./",
            ]
        )
        if frontend_yarn:
            lines.append("COPY frontend/yarn.lock ./")
        install_cmd = "npm ci --legacy-peer-deps" if frontend_lock else "npm install --legacy-peer-deps"
        lines.extend(
            [
                f"RUN {install_cmd}",
                "COPY frontend/ ./",
                "RUN npm run build",
            ]
        )

    lines.extend(
        [
            "FROM python:3.11-slim AS runtime",
            "ENV PYTHONDONTWRITEBYTECODE=1",
            "ENV PYTHONUNBUFFERED=1",
            "WORKDIR /app",
            "RUN pip install --no-cache-dir hla-compass",
            "COPY manifest.json /app/manifest.json",
            f"COPY {descriptor_rel.as_posix()} /app/mcp/tool.json",
        ]
    )

    backend_requirements = Path("backend/requirements.txt")
    if backend_requirements.exists():
        req_hash = "$(sha256sum backend/requirements.txt | cut -d' ' -f1)"
        lines.extend(
            [
                "ARG REQUIREMENTS_HASH=" + req_hash,
                "RUN --mount=type=cache,target=/root/.cache/pip pip install --no-cache-dir hla-compass",
                "COPY backend/requirements.txt /tmp/backend-requirements.txt",
                "RUN --mount=type=cache,target=/root/.cache/pip pip install --no-cache-dir -r /tmp/backend-requirements.txt",
            ]
        )
    else:
        lines.append("RUN --mount=type=cache,target=/root/.cache/pip pip install --no-cache-dir hla-compass")

    if Path("backend").exists():
        lines.append("COPY backend/ /app/backend/")
    else:
        lines.append("RUN mkdir -p /app/backend")

    if has_frontend:
        lines.extend(
            [
                "RUN mkdir -p /app/ui",
                "COPY --from=ui /ui/dist /app/ui/dist",
            ]
        )

    # Ensure Python can import the module package from /app and include dev serve helper
    lines.extend(
        [
            "ENV PYTHONPATH=/app",
            f"ENV HLA_COMPASS_MODULE={entrypoint}",
            # Serve mode uses this script as the container HTTP server
            "COPY dist/container-serve.py /app/container-serve.py",
            "EXPOSE 8080",
            'ENTRYPOINT ["module-runner"]',
        ]
    )

    return "\n".join(lines) + "\n"


def _resolve_entrypoint(manifest: Dict[str, Any]) -> str:
    execution = manifest.get("execution", {})
    entry = execution.get("entrypoint") or manifest.get("entrypoint")
    return entry or "backend.main:Module"


def _run_module_container(
    image_tag: str,
    manifest_path: Path,
    payload_path: Path,
    context_path: Path,
    output_dir: Path,
) -> int:
    if output_dir.exists():
        for artifact in output_dir.iterdir():
            if artifact.is_file():
                artifact.unlink()

    cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{payload_path.resolve()}:/var/input.json:ro",
        "-v",
        f"{context_path.resolve()}:/var/context.json:ro",
        "-v",
        f"{output_dir.resolve()}:/var/dev-out",
        "-v",
        f"{manifest_path.resolve()}:/app/manifest.json:ro",
        "-v",
        f"{(Path.cwd() / 'backend').resolve()}:/app/backend",
        "-e",
        "HLA_COMPASS_OUTPUT=/var/dev-out/output.json",
        "-e",
        "HLA_COMPASS_SUMMARY=/var/dev-out/summary.json",
    ]

    env_overrides: dict[str, str] = {}
    try:
        saved_token = Auth().get_access_token()
    except Exception:  # pragma: no cover - defensive
        saved_token = None
    if saved_token:
        env_overrides["HLA_ACCESS_TOKEN"] = saved_token
    elif os.getenv("HLA_ACCESS_TOKEN"):
        env_overrides["HLA_ACCESS_TOKEN"] = os.environ["HLA_ACCESS_TOKEN"]

    if os.getenv("HLA_API_KEY") and "HLA_API_KEY" not in env_overrides:
        env_overrides["HLA_API_KEY"] = os.environ["HLA_API_KEY"]

    current_env = Config.get_environment()
    env_overrides.setdefault("HLA_COMPASS_ENV", current_env)
    env_overrides.setdefault("HLA_ENV", current_env)

    for key, value in env_overrides.items():
        cmd.extend(["-e", f"{key}={value}"])

    passthrough_env = [
        "HLA_API_KEY",
        "HLA_ACCESS_TOKEN",
        "HLA_COMPASS_ENV",
        "HLA_ENV",
        "HLA_RATE_LIMIT_MAX_REQUESTS",
        "HLA_RATE_LIMIT_TIME_WINDOW",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_SESSION_TOKEN",
        "AWS_PROFILE",
        "AWS_REGION",
    ]
    for env_name in passthrough_env:
        value = os.getenv(env_name)
        if value and env_name not in env_overrides:
            cmd.extend(["-e", f"{env_name}={value}"])

    extra_env = os.getenv("HLA_COMPASS_DEV_ENV")
    if extra_env:
        for pair in extra_env.split(","):
            if "=" in pair:
                key, val = pair.split("=", 1)
                key = key.strip()
                if key:
                    cmd.extend(["-e", f"{key}={val}"])

    cmd.append(image_tag)

    if VERBOSE_MODE:
        import shlex
        # Redact sensitive environment values in the printed docker command
        secret_env = {
            "HLA_ACCESS_TOKEN",
            "HLA_API_KEY",
            "AWS_SECRET_ACCESS_KEY",
            "AWS_SESSION_TOKEN",
        }
        redacted_cmd: list[str] = []
        i = 0
        while i < len(cmd):
            part = cmd[i]
            if part == "-e" and i + 1 < len(cmd):
                kv = cmd[i + 1]
                if "=" in kv:
                    k, v = kv.split("=", 1)
                    if k in secret_env:
                        redacted_cmd.extend(["-e", f"{k}=***"])
                        i += 2
                        continue
            redacted_cmd.append(part)
            i += 1

        console.log(
            "docker run command:",
            " ".join(shlex.quote(part) for part in redacted_cmd),
        )

    result = subprocess.run(cmd)

    # Don't abort immediately on non-zero exit. The container writes error
    # details to output.json; let callers surface those for better DX.
    if result.returncode != 0 and VERBOSE_MODE:
        console.print("[red]Container run failed (non-zero exit)[/red]")

    return result.returncode


def _write_container_serve_script(dist_dir: Path) -> Path:
    """Write a lightweight HTTP server used by 'hla-compass serve' into dist.

    The script runs inside the container and serves:
    - Static UI from /app/ui/dist
    - POST /api/execute to run the module
    - GET /api/status for basic info
    """
    dist_dir.mkdir(parents=True, exist_ok=True)
    script_path = dist_dir / "container-serve.py"
    script = r'''#!/usr/bin/env python3
import os
import json
import importlib
from pathlib import Path
from aiohttp import web

MODULE_ENTRY = os.getenv("HLA_COMPASS_MODULE", "backend.main:Module")
MANIFEST_PATH = Path("/app/manifest.json")

def _resolve_module(entry: str):
    if ":" not in entry:
        raise RuntimeError("HLA_COMPASS_MODULE must be '<module_path>:<Class>'")
    mod, cls = entry.split(":", 1)
    m = importlib.import_module(mod)
    C = getattr(m, cls)
    return C()

def _load_manifest():
    try:
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _locate_ui_dist() -> Path | None:
    candidates = [
        Path("/app/ui/dist"),
        Path("/app/ui/build"),
        Path("/app/frontend/dist"),
        Path("/app/frontend/build"),
    ]
    for p in candidates:
        if p.exists() and any((p / name).exists() for name in ("bundle.js", "index.html")):
            return p
    return None

async def handle_execute(request: web.Request) -> web.Response:
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    input_data = payload.get("input", {}) if isinstance(payload, dict) else {}
    context = {
        "job_id": "serve-dev",
        "user_id": "dev-user",
        "organization_id": "dev-org",
        "mode": "interactive",
        "tier": "foundational",
    }
    try:
        module = request.app["module"]
        result = module.run(input_data, context)
        return web.json_response(result)
    except Exception as e:
        return web.json_response({
            "status": "error",
            "error": {"type": type(e).__name__, "message": str(e)}
        }, status=500)

async def handle_status(request: web.Request) -> web.Response:
    manifest = request.app.get("manifest", {})
    ui_root = request.app.get("ui_root")
    return web.json_response({
        "name": manifest.get("name"),
        "version": manifest.get("version"),
        "type": manifest.get("type"),
        "ui": bool(ui_root),
        "ui_root": str(ui_root) if ui_root else None,
        "entrypoint": os.getenv("HLA_COMPASS_MODULE"),
    })

def _ui_wrapper_html() -> str:
    return f"""
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>HLA-Compass Module UI</title>
  <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\" />
  <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin />
  <link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap\" rel=\"stylesheet\" />
  <link rel=\"stylesheet\" href=\"https://unpkg.com/antd@5/dist/reset.css\" />
  <style>
    html, body, #root {{ height: 100%; margin: 0; }}
    body {{ font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif; }}
  </style>
  <script crossorigin src=\"https://unpkg.com/react@18/umd/react.development.js\"></script>
  <script crossorigin src=\"https://unpkg.com/react-dom@18/umd/react-dom.development.js\"></script>
  <script src=\"https://unpkg.com/dayjs@1/dayjs.min.js\"></script>
  <script src=\"https://unpkg.com/dayjs@1/plugin/customParseFormat.js\"></script>
  <script src=\"https://unpkg.com/dayjs@1/plugin/advancedFormat.js\"></script>
  <script src=\"https://unpkg.com/dayjs@1/plugin/weekday.js\"></script>
  <script src=\"https://unpkg.com/dayjs@1/plugin/localeData.js\"></script>
  <script src=\"https://unpkg.com/dayjs@1/plugin/weekOfYear.js\"></script>
  <script src=\"https://unpkg.com/dayjs@1/plugin/weekYear.js\"></script>
  <script>
    (function() {{
      try {{
        if (window.dayjs) {{
          if (window.dayjs_plugin_customParseFormat) dayjs.extend(window.dayjs_plugin_customParseFormat);
          if (window.dayjs_plugin_advancedFormat) dayjs.extend(window.dayjs_plugin_advancedFormat);
          if (window.dayjs_plugin_weekday) dayjs.extend(window.dayjs_plugin_weekday);
          if (window.dayjs_plugin_localeData) dayjs.extend(window.dayjs_plugin_localeData);
          if (window.dayjs_plugin_weekOfYear) dayjs.extend(window.dayjs_plugin_weekOfYear);
          if (window.dayjs_plugin_weekYear) dayjs.extend(window.dayjs_plugin_weekYear);
        }}
      }} catch (e) {{}}
    }})();
  </script>
  <script src=\"https://unpkg.com/antd@5/dist/antd.min.js\"></script>
  <script src=\"https://unpkg.com/@ant-design/icons@6/dist/index.umd.js\"></script>
</head>
<body>
  <div id=\"root\"></div>
  <script src=\"/bundle.js\"></script>
  <script>
    (function() {{
      async function onExecute(params) {{
        const res = await fetch('/api/execute', {{method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify({{input: params}})}});
        return res.json();
      }}
      function mount() {{
        const Comp = (window.ModuleUI && (window.ModuleUI.default || window.ModuleUI)) || null;
        const el = Comp ? React.createElement(Comp, {{ onExecute }}) : null;
        const root = document.getElementById('root');
        if (!Comp) {{ root.innerHTML = '<pre style=\"padding:16px;color:#b91c1c\">ModuleUI UMD not found. Ensure webpack output.library name is ModuleUI.</pre>'; return; }}
        if (window.ReactDOM && window.ReactDOM.createRoot) {{ ReactDOM.createRoot(root).render(el); }}
        else if (window.ReactDOM && window.ReactDOM.render) {{ ReactDOM.render(el, root); }}
        else {{ root.innerHTML = '<pre style=\"padding:16px;color:#b91c1c\">ReactDOM not available.</pre>'; }}
      }}
      if (document.readyState === 'complete' || document.readyState === 'interactive') {{ setTimeout(mount, 0); }}
      else {{ window.addEventListener('DOMContentLoaded', mount); }}
    }})();
  </script>
</body>
</html>
"""

async def handle_index(request: web.Request) -> web.StreamResponse:
    ui_root = request.app.get("ui_root")
    if not ui_root:
        return web.Response(text="<h1>No UI bundle found</h1>", content_type="text/html")
    return web.Response(text=_ui_wrapper_html(), content_type="text/html")

async def handle_static(request: web.Request) -> web.StreamResponse:
    ui_root = request.app.get("ui_root")
    if not ui_root:
        raise web.HTTPNotFound()
    rel = request.match_info.get("path", "")
    candidate = ui_root / rel
    if candidate.is_file():
        return web.FileResponse(candidate)
    # Fallback: serve wrapper for client-routed paths
    return web.Response(text=_ui_wrapper_html(), content_type="text/html")

def main():
    app = web.Application()
    app["manifest"] = _load_manifest()
    app["module"] = _resolve_module(MODULE_ENTRY)
    app["ui_root"] = _locate_ui_dist()
    app.router.add_post("/api/execute", handle_execute)
    app.router.add_get("/api/status", handle_status)
    app.router.add_get("/", handle_index)
    app.router.add_get("/{path:.*}", handle_static)
    port = int(os.getenv("PORT", "8080"))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
'''
    script_path.write_text(script, encoding="utf-8")
    return script_path


def _manifest_defaults(manifest: Dict[str, Any]) -> Dict[str, Any]:
    inputs = manifest.get("inputs", {})
    defaults: Dict[str, Any] = {}

    if isinstance(inputs, dict):
        if inputs.get("type") == "object" and "properties" in inputs:
            for name, schema in inputs.get("properties", {}).items():
                if isinstance(schema, dict) and "default" in schema:
                    defaults[name] = schema["default"]
        else:
            for name, schema in inputs.items():
                if isinstance(schema, dict) and "default" in schema:
                    defaults[name] = schema["default"]

    return defaults


def _required_input_fields(manifest: Dict[str, Any]) -> set[str]:
    inputs = manifest.get("inputs", {})
    required: set[str] = set()

    if not isinstance(inputs, dict):
        return required

    if inputs.get("type") == "object" and "properties" in inputs:
        for name in inputs.get("required", []) or []:
            if isinstance(name, str):
                required.add(name)
    else:
        for name, schema in inputs.items():
            if isinstance(schema, dict) and schema.get("required"):
                required.add(name)

    return required


def _build_default_payload(manifest: Dict[str, Any]) -> Dict[str, Any]:
    payload_data: Dict[str, Any] = {}

    sample_input_path = Path("examples/sample_input.json")
    if sample_input_path.exists():
        try:
            sample_payload = json.loads(sample_input_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            sample_payload = None
        else:
            if isinstance(sample_payload, dict):
                payload_data.update(sample_payload)

    manifest_defaults = _manifest_defaults(manifest)
    if manifest_defaults:
        payload_data.update(manifest_defaults)

    for field in _required_input_fields(manifest):
        payload_data.setdefault(field, "")

    return payload_data


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")



@cli.command()
@verbose_option
@click.option("--env", 
              required=True,
              type=click.Choice(["dev", "staging", "prod"]),
              help="Target environment (dev/staging/prod)")
@click.option("--image-ref", "--image", "image_ref",
              required=True,
              help="External image reference accessible to the control plane (e.g., ghcr.io/org/module:1.0.0)")
@click.option("--visibility",
              type=click.Choice(["private", "org", "public"], case_sensitive=False),
              default="private",
              show_default=True,
              help="Visibility for the published module")
@click.option("--org-id",
              help="Organization ID (required when visibility=org)")
@click.option("--dry-run", is_flag=True, help="Resolve digest and show what would be sent without contacting the API")
@click.option("--no-sign",
              is_flag=True,
              help="Skip signing (dev only; rejected in staging/prod)")
@click.pass_context
def publish(
    ctx: click.Context,
    env: str,
    image_ref: str,
    visibility: str,
    org_id: Optional[str],
    dry_run: bool,
    no_sign: bool,
):
    """Publish a container image through the async intake pipeline.

    This command:
    1. Loads and validates `manifest.json`
    2. Signs the manifest (unless `--no-sign` in dev)
    3. Submits `/v1/modules/publish` with `imageRef`, `manifest`, and visibility metadata

    Prerequisites:
    - Push the image to a registry reachable from the platform (e.g., GHCR)
    - Run `hla-compass configure` to generate signing keys
    - Run `hla-compass auth login --env <env>` to authenticate

    Workflow:
        hla-compass build --tag ghcr.io/org/my-module:1.0.0 --push
        hla-compass auth login --env dev
        hla-compass publish --env dev --image-ref ghcr.io/org/my-module:1.0.0

    Example:
        hla-compass publish --env dev --image-ref ghcr.io/org/my-module:1.0.0 --visibility org --org-id 1234
    """
    console = Console()
    _ensure_verbose(ctx)

    visibility = (visibility or "private").lower()
    if visibility == "org" and not org_id:
        console.print("[red]✗ --org-id is required when visibility=org[/red]")
        raise click.Abort()

    if visibility != "org" and org_id:
        console.print("[yellow]⚠[/yellow] Ignoring --org-id because visibility is not 'org'")
        org_id = None

    # Disallow --no-sign outside dev
    if no_sign and env in ("staging", "prod"):
        console.print("[red]✗ --no-sign is only allowed for dev[/red]")
        raise click.Abort()

    # Step 1: Validate authentication
    auth = Auth()
    if not auth.is_authenticated():
        console.print("[red]✗ Not authenticated[/red]")
        console.print(f"Run: [cyan]hla-compass auth login --env {env}[/cyan]")
        raise click.Abort()

    # Step 2: Load manifest.json
    manifest_path = Path("manifest.json")
    if not manifest_path.exists():
        console.print("[red]✗ manifest.json not found[/red]")
        raise click.Abort()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    execution = manifest.setdefault("execution", {})
    # Ensure we don't ship stale image metadata – the intake pipeline sets these
    execution.pop("image", None)
    execution.pop("imageDigest", None)

    image_digest: Optional[str] = None
    digest_note: Optional[str] = None
    try:
        result = subprocess.run(
            ["docker", "image", "inspect", image_ref, "--format", "{{json .RepoDigests}}"],
            capture_output=True,
            text=True,
            check=True,
        )
        repo_digests = json.loads(result.stdout.strip() or "[]")
        image_digest = repo_digests[0] if repo_digests else None
        if not image_digest:
            alt = subprocess.run(
                ["docker", "image", "inspect", image_ref, "--format", "{{.Id}}"],
                capture_output=True,
                text=True,
                check=True,
            )
            image_digest = alt.stdout.strip() or None
    except FileNotFoundError:
        digest_note = "Docker CLI not available; skipping local digest preview"
    except subprocess.CalledProcessError:
        digest_note = "Image not present locally; digest will be resolved by the platform"

    if dry_run:
        name = manifest.get("name") or "module"
        version = manifest.get("version") or "latest"
        ui_path = f"modules/{name}/{version}/bundle.js"
        preview = {
            "env": env,
            "imageRef": image_ref,
            "visibility": visibility,
            "orgId": org_id,
            "manifest_name": name,
            "manifest_version": version,
            "predicted_ui_cdn_path": ui_path,
        }
        if image_digest:
            preview["resolved_digest"] = image_digest
        console.print(Panel.fit(json.dumps(preview, indent=2), title="Publish Dry Run", border_style="cyan"))
        if digest_note:
            console.print(f"[yellow]Note:[/yellow] {digest_note}")
        console.print(Panel.fit("Dry run complete. No API calls were made.", border_style="dim"))
        return

    # Step 3: Sign the manifest (unless allowed no-sign)
    if not no_sign:
        console.print("[dim]Signing module manifest...[/dim]")
        try:
            signer = ModuleSigner()
            signature = signer.sign_manifest(manifest)
            manifest["signature"] = signature
            manifest["publicKey"] = signer.get_public_key_string()
            manifest["signatureAlgorithm"] = signer.ALGORITHM
            manifest["hashAlgorithm"] = signer.HASH_ALGORITHM
            manifest["keyFingerprint"] = signer.get_key_fingerprint()
            console.print("[green]✓[/green] Manifest signed successfully")
        except Exception as e:
            console.print(f"[red]✗ Signing failed:[/red] {e}")
            console.print("[yellow]Tip:[/yellow] Run [cyan]hla-compass configure[/cyan] to generate signing keys")
            raise click.Abort()
    else:
        console.print("[yellow]⚠[/yellow] Skipping signature (--no-sign enabled)")

    # Step 4: Register with platform
    console.print(f"[dim]Submitting publish request to {env}...[/dim]")

    client = APIClient()
    try:
        payload = {
            "imageRef": image_ref,
            "manifest": manifest,
            "visibility": visibility,
        }
        if visibility == "org" and org_id:
            payload["orgId"] = org_id

        idempotency_key = str(uuid.uuid4())
        response = client.register_container_module(
            payload,
            idempotency_key=idempotency_key,
        )

        console.print(f"[green]✓[/green] Publish request accepted (HTTP 202)")
        console.print(f"[dim]Idempotency-Key:[/dim] {idempotency_key}")
        console.print(f"[dim]Image Ref:[/dim] {image_ref}")
        console.print(f"[dim]Module ID: {response.get('moduleId') or response.get('module_id') or response.get('id')}[/dim]")
        console.print(f"[dim]Version: {manifest.get('version')}[/dim]")
        if response.get("image"):
            console.print(f"[dim]Intake image:[/dim] {response.get('image')}")
        if response.get("uiUrl"):
            console.print(f"[dim]UI URL:[/dim] {response.get('uiUrl')}")
        if response.get("status"):
            console.print(f"[dim]Status:[/dim] {response.get('status')}")
        if digest_note and not image_digest:
            console.print(f"[yellow]Note:[/yellow] {digest_note}")

    except Exception as e:
        console.print(f"[red]✗ Publication failed:[/red] {e}")
        raise click.Abort()



@cli.command()
@verbose_option
@click.option(
    "--env",
    type=click.Choice(["dev", "staging", "prod"]),
    default="dev",
    help="Environment to list from",
)
@click.pass_context
def list(ctx: click.Context, env: str):
    """List deployed modules"""
    from .auth import Auth
    _ensure_verbose(ctx)

    console.print(f"[bold blue]Available Modules ({env})[/bold blue]\n")

    # Check authentication
    auth = Auth()
    if not auth.is_authenticated():
        console.print(
            "[red]Error: Not authenticated. Please run 'hla-compass auth login' first[/red]"
        )
        sys.exit(1)

    # Initialize API client
    client = APIClient()

    try:
        modules = client.list_modules()

        if not modules:
            console.print("[yellow]No modules found[/yellow]")
            console.print("Publish a module with: hla-compass publish --env <env> --image-ref <registry>/<module>:<version>")
            return

        # Display modules in a table

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Module ID", style="dim")
        table.add_column("Name")
        table.add_column("Version")
        table.add_column("Runtime")
        table.add_column("Status")

        for module in modules:
            table.add_row(
                module.get("id", "N/A"),
                module.get("name", "N/A"),
                module.get("version", "N/A"),
                module.get("compute_type", "docker"),
                module.get("status", "active"),
            )

        console.print(table)
        console.print(f"\nTotal: {len(modules)} module(s)")

    except Exception as e:
        console.print(f"[red]Error listing modules: {e}[/red]")
        sys.exit(1)


@cli.command()
@verbose_option
@click.option("--provider", type=click.Choice(["ghcr", "ecr"]), required=True, help="Container registry provider")
@click.option("--username", help="Username for ghcr (defaults to $GITHUB_USER)")
@click.option("--token", help="Token/password for ghcr (defaults to $GHCR_TOKEN)")
@click.option("--region", default=os.getenv("AWS_REGION", "eu-central-1"), help="AWS region for ECR login")
@click.pass_context
def registry_login(ctx: click.Context, provider: str, username: str | None, token: str | None, region: str):
    """Helper to login to common registries.

    Examples:
      hla-compass registry-login --provider ghcr --username myuser --token $GHCR_TOKEN
      hla-compass registry-login --provider ecr --region eu-central-1
    """
    _ensure_verbose(ctx)
    if provider == "ghcr":
        user = username or os.getenv("GITHUB_USER") or os.getenv("GH_USER")
        tok = token or os.getenv("GHCR_TOKEN")
        if not user or not tok:
            console.print("[red]For GHCR, provide --username and --token or set GITHUB_USER/GHCR_TOKEN[/red]")
            sys.exit(1)
        proc = subprocess.run(["docker", "login", "ghcr.io", "-u", user, "--password-stdin"], input=tok, text=True)
        sys.exit(proc.returncode)
    else:
        # ECR login uses AWS CLI; assumes 'aws' is configured with a valid profile/session
        try:
            login_cmd = [
                "bash",
                "-lc",
                f"aws ecr get-login-password --region {region} | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query 'Account' --output text).dkr.ecr.{region}.amazonaws.com",
            ]
            proc = subprocess.run(login_cmd)
            sys.exit(proc.returncode)
        except Exception as e:
            console.print(f"[red]ECR login failed: {e}[/red]")
            sys.exit(1)


@cli.command()
@verbose_option
@click.option("--manifest", default="manifest.json", help="Path to manifest.json")
@click.option("--json", "output_json", is_flag=True, help="Output JSON result")
@click.pass_context
def preflight(ctx: click.Context, manifest: str, output_json: bool):
    """Preflight checks before publishing (schema + entrypoint + UI contract).

    - Validates manifest schema presence and required fields
    - Ensures backend/main.py exists and entrypoint is importable
    - For UI modules, warns if webpack config missing UMD 'ModuleUI' export
    """
    _ensure_verbose(ctx)
    errors: list[str] = []
    warnings: list[str] = []

    manifest_path = Path(manifest)
    if not manifest_path.exists():
        errors.append("manifest.json not found")
        _out = {"valid": False, "errors": errors, "warnings": warnings}
        return print(json.dumps(_out)) if output_json else (console.print("[red]✗ manifest.json not found[/red]"), sys.exit(1))

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON: {e}")
        _out = {"valid": False, "errors": errors, "warnings": warnings}
        return print(json.dumps(_out)) if output_json else (console.print(f"[red]✗ Invalid JSON: {e}[/red]"), sys.exit(1))

    # Schema basics
    for field in ("name", "version", "type"):
        if field not in data:
            errors.append(f"Missing required field: {field}")
    exec_obj = data.get("execution") or {}
    entry = exec_obj.get("entrypoint") or data.get("entrypoint")
    if not entry:
        errors.append("Missing execution.entrypoint (e.g., backend.main:UIModule)")

    # Entry import test
    module_dir = manifest_path.parent
    backend_dir = module_dir / "backend"
    if backend_dir.exists() and entry and ":" in entry:
        try:
            mod, cls = entry.split(":", 1)
            sys.path.insert(0, str(module_dir))
            import importlib

            m = importlib.import_module(mod)
            getattr(m, cls)
        except Exception as e:
            warnings.append(f"Entrypoint not importable locally: {e}")
        finally:
            if str(module_dir) in sys.path:
                sys.path.remove(str(module_dir))

    # UI contract hint
    if data.get("type") == "with-ui":
        webpack_cfg = module_dir / "frontend" / "webpack.config.js"
        if not webpack_cfg.exists():
            warnings.append("frontend/webpack.config.js not found (UMD config should export 'ModuleUI')")
        else:
            try:
                text = webpack_cfg.read_text(encoding="utf-8")
                if "name: 'ModuleUI'" not in text and 'name: "ModuleUI"' not in text:
                    warnings.append("Webpack 'output.library.name' not set to 'ModuleUI' (UMD)")
            except Exception:
                warnings.append("Could not read webpack.config.js to verify UMD export")

    valid = len(errors) == 0
    if output_json:
        print(json.dumps({"valid": valid, "errors": errors, "warnings": warnings}, indent=2))
    else:
        if valid:
            console.print("[green]✓ Preflight OK[/green]")
        else:
            console.print("[red]✗ Preflight failed[/red]")
        for e in errors:
            console.print(f"  • [red]{e}[/red]")
        for w in warnings:
            console.print(f"  • [yellow]{w}[/yellow]")
        sys.exit(0 if valid else 1)
def main():
    """Main entry point for CLI"""
    cli()


if __name__ == "__main__":
    main()

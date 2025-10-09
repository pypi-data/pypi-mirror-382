"""
Interactive wizard for HLA-Compass module creation

Guides users through module setup with intelligent questions and code generation.
"""

import re
import shutil
import subprocess
import sys
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

import questionary
from questionary import Style
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .generators import CodeGenerator

console = Console()

# Custom style for the wizard
WIZARD_STYLE = Style([
    ('qmark', 'fg:#667eea bold'),       # Purple question mark
    ('question', 'bold'),                # Bold questions
    ('answer', 'fg:#10b981 bold'),      # Green answers
    ('pointer', 'fg:#667eea bold'),     # Purple pointer
    ('highlighted', 'fg:#667eea bold'), # Purple highlights
    ('selected', 'fg:#10b981'),         # Green selected
    ('separator', 'fg:#6b7280'),        # Gray separator
    ('instruction', 'fg:#6b7280'),      # Gray instructions
    ('text', ''),
    ('disabled', 'fg:#6b7280 italic'),
])


class ModuleWizard:
    """Interactive wizard for module creation"""
    
    def __init__(self):
        self.generator = CodeGenerator()
        self.config = {}
        
    def run(self) -> Dict[str, Any]:
        """Run the interactive wizard and return configuration"""
        
        # Welcome message
        self._show_welcome()
        
        # Step 1: Basic information
        self.config.update(self._ask_basic_info())
        
        # Step 2: Module type
        self.config.update(self._ask_module_type())
        
        # Step 3: Input parameters
        self.config['inputs'] = self._ask_inputs()
        
        # Step 4: Processing type
        self.config.update(self._ask_processing())
        
        # Step 5: Output format
        self.config['outputs'] = self._ask_outputs()
        
        # Step 6: Dependencies
        self.config['dependencies'] = self._ask_dependencies()
        
        # Step 7: Confirm and generate
        if self._confirm_configuration():
            return self.config
        else:
            # Allow editing
            return self._edit_configuration()
    
    def _show_welcome(self):
        """Display welcome message"""
        console.print(Panel.fit(
            "[bold bright_magenta]🧬 HLA-Compass Module Creation Wizard[/bold bright_magenta]\n\n"
            "I'll guide you through creating your module step by step.\n"
            "This wizard will:\n"
            "• Ask about your module's purpose\n"
            "• Define input and output schemas\n"
            "• Generate working code\n"
            "• Create test data\n\n"
            "[dim]Press Ctrl+C at any time to cancel[/dim]",
            title="Welcome",
            border_style="bright_magenta"
        ))
        console.print()
    
    def _ask_basic_info(self) -> Dict[str, Any]:
        """Ask for basic module information"""
        console.print("[bold cyan]📝 Basic Information[/bold cyan]\n")
        
        # Ask name, then validate/normalize to a slug
        while True:
            name = questionary.text(
                "Module name:",
                default="my-module",
                style=WIZARD_STYLE,
                validate=lambda x: len(x) > 0
            ).ask()

            slug = self._slugify(name)
            if slug != name:
                accept = questionary.confirm(
                    f"Use normalized name '{slug}'?",
                    default=True,
                    style=WIZARD_STYLE
                ).ask()
                if accept:
                    name = slug
                elif not self._is_valid_module_name(name):
                    console.print("[yellow]Name must contain only letters, numbers, hyphens, or underscores and start with a letter.[/yellow]")
                    continue

            target = Path(name)
            if target.exists() and any(target.iterdir()):
                choice = questionary.select(
                    f"Directory '{name}' already exists and is not empty. What would you like to do?",
                    choices=[
                        "Choose a different name",
                        "Continue and overwrite (may replace files)",
                        "Cancel"
                    ],
                    style=WIZARD_STYLE
                ).ask()
                if choice == "Choose a different name":
                    continue
                if choice == "Cancel":
                    return None
            break
        
        description = questionary.text(
            "Brief description:",
            default="HLA-Compass analysis module",
            style=WIZARD_STYLE
        ).ask()
        
        author = questionary.text(
            "Your name:",
            default="Developer",
            style=WIZARD_STYLE
        ).ask()
        
        # Validate email format
        default_email = f"{author.lower().replace(' ', '.')}@example.com"
        while True:
            email = questionary.text(
                "Your email:",
                default=default_email,
                style=WIZARD_STYLE
            ).ask()
            if self._is_valid_email(email):
                break
            console.print("[yellow]Please enter a valid email address (e.g., name@domain.com)[/yellow]")
        
        return {
            'name': name,
            'description': description,
            'author': {'name': author, 'email': email}
        }
    
    def _ask_module_type(self) -> Dict[str, Any]:
        """Ask about module type"""
        console.print("\n[bold cyan]🎨 Module Type[/bold cyan]\n")
        
        has_ui = questionary.confirm(
            "Does your module need a user interface?",
            default=False,
            style=WIZARD_STYLE
        ).ask()
        
        result = {'has_ui': has_ui}
        
        if has_ui:
            ui_type = questionary.select(
                "What kind of UI do you need?",
                choices=[
                    "Data table with filters",
                    "Interactive charts and graphs",
                    "Form-based input wizard",
                    "Custom dashboard",
                    "Simple results display"
                ],
                style=WIZARD_STYLE
            ).ask()
            result['ui_type'] = ui_type

            # Environment check for Node/npm
            node_ok, node_ver, npm_ok, npm_ver, notes = self._check_node_tools()
            if not node_ok or not npm_ok:
                console.print("[yellow]⚠️ Node.js and npm not detected. Frontend dev/build will require Node.js (>=18) and npm installed.[/yellow]")
            else:
                console.print(f"[dim]Detected Node.js {node_ver}, npm {npm_ver}[/dim]")
                for w in notes:
                    console.print(f"[yellow]• {w}[/yellow]")
        
        return result
    
    def _ask_inputs(self) -> Dict[str, Any]:
        """Ask about input parameters"""
        console.print("\n[bold cyan]📥 Input Parameters[/bold cyan]\n")
        console.print("[dim]Define what data your module will accept[/dim]\n")
        
        inputs = {}
        
        # Common peptide-related inputs
        use_peptides = questionary.confirm(
            "Will you work with peptide sequences?",
            default=True,
            style=WIZARD_STYLE
        ).ask()
        
        if use_peptides:
            peptide_input = questionary.select(
                "How will peptides be provided?",
                choices=[
                    "List of sequences",
                    "FASTA file",
                    "Database query",
                    "CSV/Excel file"
                ],
                style=WIZARD_STYLE
            ).ask()
            
            if peptide_input == "List of sequences":
                inputs['peptide_sequences'] = {
                    'type': 'array',
                    'description': 'List of peptide sequences',
                    'required': True,
                    'items': {'type': 'string'}
                }
            elif peptide_input == "FASTA file":
                inputs['fasta_file'] = {
                    'type': 'string',
                    'description': 'Path or content of FASTA file',
                    'required': True
                }
            elif peptide_input == "Database query":
                inputs['query'] = {
                    'type': 'object',
                    'description': 'Database query parameters',
                    'required': True
                }
            else:  # CSV/Excel
                inputs['data_file'] = {
                    'type': 'string',
                    'description': 'Path to CSV/Excel file',
                    'required': True
                }
        
        # Ask for additional custom inputs
        while questionary.confirm(
            "Add another input parameter?",
            default=False,
            style=WIZARD_STYLE
        ).ask():
            param_name = questionary.text(
                "Parameter name:",
                style=WIZARD_STYLE
            ).ask()
            
            param_type = questionary.select(
                "Parameter type:",
                choices=['string', 'number', 'boolean', 'array', 'object'],
                style=WIZARD_STYLE
            ).ask()
            
            param_desc = questionary.text(
                "Description:",
                style=WIZARD_STYLE
            ).ask()
            
            param_required = questionary.confirm(
                "Is this required?",
                default=True,
                style=WIZARD_STYLE
            ).ask()
            
            inputs[param_name] = {
                'type': param_type,
                'description': param_desc,
                'required': param_required
            }
            
            if not param_required:
                default_val = questionary.text(
                    f"Default value for {param_name}:",
                    style=WIZARD_STYLE
                ).ask()
                
                # Parse default value based on type
                if param_type == 'number':
                    inputs[param_name]['default'] = float(default_val) if default_val else 0
                elif param_type == 'boolean':
                    inputs[param_name]['default'] = default_val.lower() in ['true', 'yes', '1']
                elif param_type == 'array':
                    inputs[param_name]['default'] = []
                elif param_type == 'object':
                    inputs[param_name]['default'] = {}
                else:
                    inputs[param_name]['default'] = default_val
        
        return inputs
    
    def _ask_processing(self) -> Dict[str, Any]:
        """Ask about processing type"""
        console.print("\n[bold cyan]⚙️ Processing Type[/bold cyan]\n")
        
        processing_type = questionary.select(
            "What kind of processing will your module perform?",
            choices=[
                "Sequence analysis (alignment, motifs, properties)",
                "Statistical analysis (correlation, clustering)",
                "Machine learning (prediction, classification)",
                "Data transformation (filtering, formatting)",
                "Database operations (search, annotation)",
                "Visualization (plots, reports)",
                "Integration (external APIs, tools)",
                "Custom algorithm"
            ],
            style=WIZARD_STYLE
        ).ask()
        
        # Ask for specific features based on type
        features = []
        
        if "Sequence analysis" in processing_type:
            features = questionary.checkbox(
                "Select sequence analysis features:",
                choices=[
                    "Physicochemical properties",
                    "Motif discovery",
                    "Sequence alignment",
                    "Structure prediction",
                    "Immunogenicity scoring"
                ],
                style=WIZARD_STYLE
            ).ask()
        elif "Machine learning" in processing_type:
            features = questionary.checkbox(
                "Select ML features:",
                choices=[
                    "Binary classification",
                    "Multi-class classification",
                    "Regression",
                    "Clustering",
                    "Feature importance"
                ],
                style=WIZARD_STYLE
            ).ask()
        
        return {
            'processing_type': processing_type,
            'features': features
        }
    
    def _ask_outputs(self) -> Dict[str, Any]:
        """Ask about output format"""
        console.print("\n[bold cyan]📤 Output Format[/bold cyan]\n")
        
        output_format = questionary.select(
            "Primary output format:",
            choices=[
                "Structured data (JSON/dict)",
                "Table (CSV/Excel compatible)",
                "Report (formatted text/HTML)",
                "Visualization (charts/plots)",
                "Files (generated files)"
            ],
            style=WIZARD_STYLE
        ).ask()
        
        outputs = {}
        
        if "Structured data" in output_format:
            outputs['results'] = {
                'type': 'array',
                'description': 'Processing results'
            }
            outputs['summary'] = {
                'type': 'object',
                'description': 'Summary statistics'
            }
        elif "Table" in output_format:
            outputs['table'] = {
                'type': 'array',
                'description': 'Tabular results'
            }
            outputs['columns'] = {
                'type': 'array',
                'description': 'Column definitions'
            }
        elif "Report" in output_format:
            outputs['report'] = {
                'type': 'string',
                'description': 'Formatted report'
            }
        elif "Visualization" in output_format:
            outputs['plots'] = {
                'type': 'array',
                'description': 'Generated plots'
            }
        else:  # Files
            outputs['files'] = {
                'type': 'array',
                'description': 'Generated file paths'
            }
        
        # Always include status and metadata
        outputs['status'] = {
            'type': 'string',
            'description': 'Execution status'
        }
        outputs['metadata'] = {
            'type': 'object',
            'description': 'Execution metadata'
        }
        
        return outputs
    
    def _ask_dependencies(self) -> List[str]:
        """Ask about required dependencies"""
        console.print("\n[bold cyan]📦 Dependencies[/bold cyan]\n")
        
        # Common scientific Python packages
        deps = questionary.checkbox(
            "Select required packages:",
            choices=[
                "numpy - Numerical computing",
                "pandas - Data manipulation",
                "scikit-learn - Machine learning",
                "biopython - Bioinformatics tools",
                "matplotlib - Plotting",
                "seaborn - Statistical visualization",
                "scipy - Scientific computing",
                "torch - Deep learning",
                "requests - HTTP requests",
                "xlsxwriter - Excel export"
            ],
            style=WIZARD_STYLE
        ).ask()
        
        # Clean up dependency names
        clean_deps = [dep.split(' - ')[0] for dep in deps]
        
        # Ask for additional custom dependencies
        custom = questionary.text(
            "Additional packages (comma-separated, optional):",
            default="",
            style=WIZARD_STYLE
        ).ask()
        
        if custom:
            clean_deps.extend([d.strip() for d in custom.split(',')])
        
        return clean_deps
    
    def _confirm_configuration(self) -> bool:
        """Show configuration summary and confirm"""
        console.print("\n[bold cyan]📋 Configuration Summary[/bold cyan]\n")
        
        # Create summary table
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Setting", style="bright_white")
        table.add_column("Value", style="bright_green")
        
        table.add_row("Module Name", self.config['name'])
        table.add_row("Description", self.config['description'])
        table.add_row("Type", "UI Module" if self.config.get('has_ui') else "Backend Module")
        table.add_row("Author", f"{self.config['author']['name']} <{self.config['author']['email']}>")
        table.add_row("Inputs", f"{len(self.config.get('inputs', {}))} parameters")
        table.add_row("Outputs", f"{len(self.config.get('outputs', {}))} fields")
        table.add_row("Dependencies", f"{len(self.config.get('dependencies', []))} packages")
        
        console.print(table)
        
        # Run preflight checks
        ok, warnings, errors = self._preflight_checks()
        self._display_preflight(ok, warnings, errors)
        
        if errors:
            proceed = questionary.confirm(
                "Preflight detected errors. Proceed anyway?",
                default=False,
                style=WIZARD_STYLE
            ).ask()
            if not proceed:
                return False
        
        console.print()
        return questionary.confirm(
            "Generate module with this configuration?",
            default=True,
            style=WIZARD_STYLE
        ).ask()
    
    def _edit_configuration(self) -> Dict[str, Any]:
        """Allow editing configuration"""
        while True:
            action = questionary.select(
                "What would you like to change?",
                choices=[
                    "Basic information",
                    "Module type",
                    "Input parameters",
                    "Processing type",
                    "Output format",
                    "Dependencies",
                    "✓ Continue with current configuration",
                    "✗ Cancel"
                ],
                style=WIZARD_STYLE
            ).ask()
            
            if action == "✓ Continue with current configuration":
                return self.config
            elif action == "✗ Cancel":
                return None
            elif action == "Basic information":
                self.config.update(self._ask_basic_info())
            elif action == "Module type":
                self.config.update(self._ask_module_type())
            elif action == "Input parameters":
                self.config['inputs'] = self._ask_inputs()
            elif action == "Processing type":
                self.config.update(self._ask_processing())
            elif action == "Output format":
                self.config['outputs'] = self._ask_outputs()
            elif action == "Dependencies":
                self.config['dependencies'] = self._ask_dependencies()
            
            # Show updated configuration
            self._confirm_configuration()

    # --- Validation helpers and preflight ---
    def _slugify(self, name: str) -> str:
        slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", name.strip())
        if not re.match(r"^[A-Za-z]", slug):
            slug = f"m-{slug}"
        return slug[:64]

    def _is_valid_module_name(self, name: str) -> bool:
        return bool(re.match(r"^[A-Za-z][A-Za-z0-9_-]{1,63}$", name))

    def _is_valid_email(self, email: str) -> bool:
        return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))

    def _check_node_tools(self) -> Tuple[bool, str, bool, str, List[str]]:
        warnings: List[str] = []
        node_ok = False
        npm_ok = False
        node_ver = ""
        npm_ver = ""
        try:
            node_out = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if node_out.returncode == 0:
                node_ver = node_out.stdout.strip().lstrip('v')
                node_ok = True
                try:
                    major = int(node_ver.split(".")[0])
                    if major < 18:
                        warnings.append(f"Node.js {node_ver} detected; version 18+ is recommended.")
                except Exception:
                    pass
        except Exception:
            pass
        try:
            npm_out = subprocess.run(["npm", "--version"], capture_output=True, text=True)
            if npm_out.returncode == 0:
                npm_ver = npm_out.stdout.strip()
                npm_ok = True
        except Exception:
            pass
        return node_ok, node_ver, npm_ok, npm_ver, warnings

    def _preflight_checks(self) -> Tuple[bool, List[str], List[str]]:
        warnings: List[str] = []
        errors: List[str] = []

        # Python version
        py_major, py_minor = sys.version_info[:2]
        if py_major < 3 or (py_major == 3 and py_minor < 8):
            errors.append("Python >= 3.8 required")
        elif py_major == 3 and py_minor < 10:
            warnings.append("Python 3.10+ recommended for best experience")

        # Directory writability
        try:
            test_dir = Path.cwd() / ".wizard_write_test"
            test_dir.mkdir(exist_ok=True)
            (test_dir / "_touch").write_text("ok")
            shutil.rmtree(test_dir)
        except Exception as e:
            errors.append(f"No write permission in current directory: {e}")

        # Module name validity
        name = self.config.get('name', '')
        if not self._is_valid_module_name(name):
            errors.append("Invalid module name format")

        # Email validity
        email = self.config.get('author', {}).get('email', '')
        if not self._is_valid_email(email):
            errors.append("Invalid author email format")

        # Duplicate input names and parameter names format
        inputs = self.config.get('inputs', {})
        if len(inputs) != len(set(inputs.keys())):
            errors.append("Duplicate input parameter names")
        for k in inputs.keys():
            if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", k):
                errors.append(f"Invalid input parameter name: {k}")

        # Dependencies sanity
        deps = self.config.get('dependencies', []) or []
        if len(deps) != len(set(deps)):
            warnings.append("Duplicate dependencies were specified; duplicates will be ignored")

        # UI environment
        if self.config.get('has_ui'):
            node_ok, node_ver, npm_ok, npm_ver, tool_warnings = self._check_node_tools()
            warnings.extend(tool_warnings)
            if not node_ok:
                warnings.append("Node.js not found; frontend dev/build will not work until installed")
            if not npm_ok:
                warnings.append("npm not found; frontend dev/build will not work until installed")

        return (len(errors) == 0), warnings, errors

    def _display_preflight(self, ok: bool, warnings: List[str], errors: List[str]) -> None:
        console.print("\n[bold cyan]🧪 Preflight Checks[/bold cyan]")
        status = "[green]OK[/green]" if ok and not errors else "[red]Issues detected[/red]"
        console.print(f"Status: {status}")
        if warnings:
            console.print("[yellow]Warnings:[/yellow]")
            for w in warnings:
                console.print(f"  • {w}")
        if errors:
            console.print("[red]Errors:[/red]")
            for e in errors:
                console.print(f"  • {e}")


def run_wizard() -> Optional[Dict[str, Any]]:
    """Run the module creation wizard"""
    try:
        wizard = ModuleWizard()
        config = wizard.run()
        
        if config:
            console.print("\n[green]✓ Configuration complete![/green]")
            console.print("[dim]Generating module files...[/dim]\n")
            return config
        else:
            console.print("\n[yellow]Module creation cancelled or needs revision[/yellow]")
            return None
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Wizard interrupted[/yellow]")
        return None
    except Exception as e:
        console.print(f"\n[red]Wizard error: {e}[/red]")
        return None
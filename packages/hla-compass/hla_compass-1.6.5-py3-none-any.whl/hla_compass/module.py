"""
Base module class for HLA-Compass modules
"""

import json
import logging
from abc import ABC, abstractmethod
from collections.abc import Mapping, Sized
from difflib import get_close_matches
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict, List, Optional

try:  # pragma: no cover - optional dependency
    from jsonschema import Draft7Validator
except Exception as exc:  # pragma: no cover - jsonschema is required for validation
    raise ImportError(
        "jsonschema is required for input validation. Install with: pip install 'jsonschema>=4.0'"
    ) from exc

from .auth import Auth, AuthError
from .config import Config
from .types import ExecutionContext, ModuleOutput
from .data import PeptideData, ProteinData, SampleData, HLAData
from .storage import Storage


logger = logging.getLogger(__name__)

MANIFEST_DOCS_URL = "https://docs.alithea.bio/sdk/modules#manifest-inputs"


def _now_utc() -> datetime:
    return datetime.now(UTC)


def _now_utc_iso() -> str:
    return _now_utc().isoformat().replace("+00:00", "Z")


class ModuleError(Exception):
    """Base exception for module errors"""

    pass


class ValidationError(ModuleError):
    """Input validation error"""

    pass


class Module(ABC):
    """
    Base class for HLA-Compass modules.

    All modules should inherit from this class and implement the execute method.
    """

    def __init__(self, manifest_path: Optional[str] = None):
        """
        Initialize module with manifest.

        Args:
            manifest_path: Path to manifest.json file
        """
        self.manifest = self._load_manifest(manifest_path)
        self.name = self.manifest.get("name", "unknown")
        self.version = self.manifest.get("version", "0.0.0")
        self.logger = logging.getLogger(f"hla_compass.module.{self.name}")
        self._metadata_parameter_paths = self._load_metadata_parameter_paths()
        self._helpers_initialized = False

    def _load_manifest(self, manifest_path: Optional[str] = None) -> Dict[str, Any]:
        """Load module manifest from file"""
        if manifest_path is None:
            manifest_path = Path.cwd() / "manifest.json"
        else:
            manifest_path = Path(manifest_path)

        if not manifest_path.exists():
            return {}

        try:
            with open(manifest_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load manifest: {e}")
            return {}

    def run(
        self, input_data: Dict[str, Any], context: ExecutionContext
    ) -> ModuleOutput:
        """
        Main entry point for module execution.

        This method handles:
        1. Input validation
        2. Execution
        3. Error handling
        4. Result formatting

        Args:
            input_data: Module input parameters
            context: Execution context with API clients

        Returns:
            ModuleOutput with results
        """
        start_time = _now_utc()
        safe_parameters: Dict[str, Any] = {}

        try:
            # Log execution start
            self.logger.info(
                "Starting module execution",
                extra={
                    "job_id": context.get("job_id"),
                    "user_id": context.get("user_id"),
                    "organization_id": context.get("organization_id"),
                    "module": self.name,
                    "version": self.version,
                },
            )

            # Validate inputs
            self.logger.debug("Validating inputs")
            validated_input = self.validate_inputs(input_data)
            safe_parameters = self._filter_metadata_parameters(validated_input)

            # Initialize data access helpers
            self._initialize_helpers(context)

            # Execute module logic
            self.logger.debug("Executing module logic")
            results = self.execute(validated_input, context)

            # Format successful output
            output = self._format_output(
                status="success",
                results=results,
                input_data=validated_input,
                start_time=start_time,
                metadata_parameters=safe_parameters,
            )

            duration = (_now_utc() - start_time).total_seconds()
            log_extra = {
                "job_id": context.get("job_id"),
                "duration": duration,
            }

            if isinstance(results, Sized):
                try:
                    log_extra["result_count"] = len(results)
                except TypeError:
                    pass

            self.logger.info(
                "Module execution completed successfully",
                extra=log_extra,
            )

            return output

        except ValidationError as e:
            self.logger.error(f"Validation error: {e}")
            error_params = self._filter_metadata_parameters(input_data)
            return self._format_error(
                e,
                "validation_error",
                input_data,
                start_time,
                metadata_parameters=error_params,
            )

        except ModuleError as e:
            self.logger.error(f"Module error: {e}")
            error_params = safe_parameters or self._filter_metadata_parameters(input_data)
            return self._format_error(
                e,
                "module_error",
                input_data,
                start_time,
                metadata_parameters=error_params,
            )

        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            error_params = safe_parameters or self._filter_metadata_parameters(input_data)
            return self._format_error(
                e,
                "internal_error",
                input_data,
                start_time,
                metadata_parameters=error_params,
            )

    def _initialize_helpers(self, context: ExecutionContext):
        """Initialize data access helpers"""
        import os

        api_client = context.get("api")

        self.peptides: Optional[PeptideData] = None
        self.proteins: Optional[ProteinData] = None
        self.samples: Optional[SampleData] = None
        self.hla: Optional[HLAData] = None
        self.storage: Optional[Storage] = None
        self.has_api_client = False
        self.has_db_client = False
        self.has_storage_client = False

        # If no API client provided, create one for SDK usage
        if not api_client:
            from .client import APIClient

            auth = Auth()
            has_token = auth.is_authenticated()
            has_api_key = bool(Config.get_api_key())

            if not (has_token or has_api_key):
                raise AuthError(
                    "No HLA-Compass API credentials available. "
                    "Set HLA_API_KEY or run 'hla-compass auth login' before executing modules."
                )

            api_client = APIClient()

        # Initialize database client if running in Lambda environment
        db_client = None
        if os.environ.get("DB_CLUSTER_ARN") and os.environ.get(
            "AWS_LAMBDA_FUNCTION_NAME"
        ):
            # We're running in Lambda with database access
            try:
                from .database import ScientificQuery

                db_client = ScientificQuery()
                self.db = db_client  # Direct access to database client
                self.logger.info("Initialized direct database access for module")
            except Exception as e:
                self.logger.warning(f"Could not initialize database client: {e}")
                # Continue without database access

        # Initialize data helpers with both API and database access
        if api_client or db_client:
            self.peptides = PeptideData(api_client, db_client)
            self.proteins = ProteinData(api_client, db_client)
            self.samples = SampleData(api_client, db_client)
            self.hla = HLAData(api_client, db_client)
            self.has_api_client = bool(api_client)
            self.has_db_client = bool(db_client)

        storage_client = context.get("storage")
        if storage_client:
            self.storage = Storage(storage_client)
            self.has_storage_client = True

        self._helpers_initialized = True

    def bootstrap(self) -> Dict[str, Any]:
        """
        Provide a guided overview of available helpers and usage hints.

        Returns a dictionary describing helper availability so modules can
        programmatically inspect capabilities, while also logging human-friendly
        guidance the first time it is invoked.
        """
        info = {
            "module": self.name,
            "version": self.version,
            "helpers": {
                "peptides": bool(getattr(self, "peptides", None)),
                "proteins": bool(getattr(self, "proteins", None)),
                "samples": bool(getattr(self, "samples", None)),
                "hla": bool(getattr(self, "hla", None)),
                "storage": bool(getattr(self, "storage", None)),
            },
            "has_api_client": getattr(self, "has_api_client", False),
            "has_db_client": getattr(self, "has_db_client", False),
            "has_storage_client": getattr(self, "has_storage_client", False),
            "metadata_fields": self._metadata_parameter_paths,
        }

        if not self._helpers_initialized:
            self.logger.warning(
                "Helpers not yet initialized. Call bootstrap after run() or manually invoke _initialize_helpers(context)."
            )
            return info

        friendly_lines = [
            f"Module '{self.name}' bootstrap summary:",
            f"- API client available: {info['has_api_client']}",
            f"- Database client available: {info['has_db_client']}",
            f"- Storage client available: {info['has_storage_client']}",
            "- Data helpers:", 
        ]

        for helper, available in info["helpers"].items():
            usage = "example: self.peptides.search(sequence='SIINFEKL')" if helper == "peptides" else None
            line = f"  • {helper}: {available}"
            if available and usage:
                line += f" ({usage})"
            friendly_lines.append(line)

        if info["metadata_fields"]:
            friendly_lines.append(
                f"- Metadata parameters exposed: {', '.join(info['metadata_fields'])}"
            )
        else:
            friendly_lines.append(
                "- Metadata parameters exposed: none (add metadata.exposedParameters in manifest to whitelist fields)"
            )

        self.logger.info("\n".join(friendly_lines))
        return info

    def validate_inputs(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate input data against manifest schema.

        Supports both JSON Schema format and flat format for backward compatibility.

        Args:
            input_data: Raw input data

        Returns:
            Validated input data

        Raises:
            ValidationError: If validation fails
        """
        # Get input schema from manifest
        input_schema = self.manifest.get("inputs", {})

        # Detect schema format
        if input_schema.get("type") == "object" and "properties" in input_schema:
            return self._validate_json_schema(input_data, input_schema)

        return self._validate_flat_schema(input_data, input_schema)

    def _validate_json_schema(
        self, input_data: Dict[str, Any], schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        validator = Draft7Validator(schema)
        errors = sorted(validator.iter_errors(input_data), key=lambda e: e.path)

        if errors:
            messages = [self._format_schema_error(error, schema) for error in errors]
            messages.append(f"See {MANIFEST_DOCS_URL} for input schema reference")
            raise ValidationError("; ".join(messages))

        # Apply defaults and return a normalized copy
        normalized = dict(input_data)
        for prop, prop_schema in schema.get("properties", {}).items():
            if prop not in normalized and "default" in prop_schema:
                normalized[prop] = prop_schema["default"]
        return normalized

    def _validate_flat_schema(
        self, input_data: Dict[str, Any], schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        properties = {}
        required: List[str] = []

        for field, field_schema in schema.items():
            json_schema: Dict[str, Any] = {
                key: field_schema[key]
                for key in (
                    "type",
                    "enum",
                    "minimum",
                    "maximum",
                    "minItems",
                    "maxItems",
                    "minLength",
                    "maxLength",
                    "pattern",
                )
                if key in field_schema
            }

            if "min" in field_schema:
                json_schema["minimum"] = field_schema["min"]
            if "max" in field_schema:
                json_schema["maximum"] = field_schema["max"]
            if "default" in field_schema:
                json_schema["default"] = field_schema["default"]

            properties[field] = json_schema

            if field_schema.get("required"):
                required.append(field)

        json_schema_wrapper = {
            "type": "object",
            "properties": properties,
            "required": required,
        }

        return self._validate_json_schema(input_data, json_schema_wrapper)

    def _format_schema_error(self, error, schema: Dict[str, Any]) -> str:
        path_parts = list(error.path)
        path = ".".join(str(p) for p in path_parts)
        field = str(path_parts[-1]) if path_parts else None
        properties = schema.get("properties", {})

        if error.validator == "required":
            # message like "'foo' is a required property"
            missing = None
            if error.message.startswith("'"):
                missing = error.message.split("'")[1]
            missing = missing or field or "unknown"
            suggestion = self._suggest_field(missing, properties)
            hint = f"Missing required field '{missing}'"
            if suggestion and suggestion != missing:
                hint += f" (did you mean '{suggestion}'?)"
            return hint

        if error.validator == "type":
            expected = error.schema.get("type")
            actual = type(error.instance).__name__
            target = path or "value"
            return f"{target} must be of type {expected}, got {actual}"

        if error.validator == "enum":
            allowed = ", ".join(map(str, error.schema.get("enum", [])))
            target = path or field or "value"
            return f"{target} must be one of [{allowed}]"

        if error.validator in {"minimum", "maximum"}:
            target = path or field or "value"
            limit = error.schema.get(error.validator)
            comparator = ">=" if error.validator == "minimum" else "<="
            return f"{target} must be {comparator} {limit}"

        if error.validator == "additionalProperties":
            unexpected = None
            if "'" in error.message:
                parts = error.message.split("'")
                if len(parts) >= 2:
                    unexpected = parts[1]
            unexpected = unexpected or field or "property"
            suggestion = self._suggest_field(unexpected, properties)
            hint = f"Unexpected field '{unexpected}'"
            if suggestion and suggestion != unexpected:
                hint += f" (did you mean '{suggestion}'?)"
            return hint

        if error.validator == "pattern":
            target = path or field or "value"
            pattern = error.schema.get("pattern")
            return f"{target} does not match required pattern {pattern}"

        target = path or field or "value"
        return f"{target}: {error.message}"

    def _suggest_field(self, candidate: str, properties: Dict[str, Any]) -> Optional[str]:
        if not candidate or not properties:
            return None
        matches = get_close_matches(candidate, properties.keys(), n=1, cutoff=0.6)
        return matches[0] if matches else None

    @abstractmethod
    def execute(self, input_data: Dict[str, Any], context: ExecutionContext) -> Any:
        """
        Execute module logic.

        This method must be implemented by all modules.

        Args:
            input_data: Validated input parameters
            context: Execution context with API clients

        Returns:
            Module results (format depends on module)
        """
        pass

    def _format_output(
        self,
        status: str,
        results: Any,
        input_data: dict[str, Any],
        start_time: datetime,
        metadata_parameters: dict[str, Any] | None = None,
    ) -> ModuleOutput:
        """Format module output"""
        duration = (_now_utc() - start_time).total_seconds()

        # Generate summary if not provided
        summary = results.get("summary") if isinstance(results, dict) else None
        if summary is None:
            summary = self._generate_summary(results)

        metadata = {
            "module": self.name,
            "version": self.version,
            "execution_time": _now_utc_iso(),
            "duration_seconds": round(duration, 2),
        }

        if metadata_parameters:
            metadata["parameters"] = metadata_parameters

        return {
            "status": status,
            "results": (
                results
                if not isinstance(results, dict)
                else results.get("results", results)
            ),
            "summary": summary,
            "metadata": metadata,
        }

    def _format_error(
        self,
        error: Exception,
        error_type: str,
        input_data: dict[str, Any],
        start_time: datetime,
        metadata_parameters: dict[str, Any] | None = None,
    ) -> ModuleOutput:
        """Format error output"""
        duration = (_now_utc() - start_time).total_seconds()

        metadata = {
            "module": self.name,
            "version": self.version,
            "execution_time": _now_utc_iso(),
            "duration_seconds": round(duration, 2),
        }

        if metadata_parameters:
            metadata["parameters"] = metadata_parameters

        return {
            "status": "error",
            "error": {
                "type": error_type,
                "message": str(error),
                "details": getattr(error, "details", None),
            },
            "metadata": metadata,
        }

    def _load_metadata_parameter_paths(self) -> Optional[List[str]]:
        metadata_cfg = self.manifest.get("metadata", {})
        exposed = metadata_cfg.get("exposedParameters") or metadata_cfg.get(
            "exposed_parameters"
        )

        if exposed is True or exposed == "*":
            return None

        if not exposed:
            return []

        if not isinstance(exposed, list):
            logger.warning("metadata.exposedParameters must be a list of field names")
            return []

        normalized: list[str] = []
        for item in exposed:
            if isinstance(item, str) and item.strip():
                normalized.append(item.strip())
            else:
                logger.warning("Ignoring invalid metadata.exposedParameters entry: %s", item)
        return normalized

    def _filter_metadata_parameters(
        self, parameters: Any
    ) -> dict[str, Any]:
        if parameters is None or not isinstance(parameters, Mapping):
            return {}

        allowed = self._metadata_parameter_paths

        if allowed is None:
            return {k: self._copy_value(v) for k, v in parameters.items()}

        if not allowed:
            return {}

        sanitized: dict[str, Any] = {}
        for path in allowed:
            value, found = self._extract_value(parameters, path)
            if found:
                self._assign_value(sanitized, path, self._copy_value(value))
        return sanitized

    def _extract_value(self, data: Mapping[str, Any], path: str) -> tuple[Any, bool]:
        current: Any = data
        for part in path.split("."):
            if not isinstance(current, Mapping) or part not in current:
                return None, False
            current = current[part]
        return current, True

    def _assign_value(self, target: Dict[str, Any], path: str, value: Any) -> None:
        parts = path.split(".")
        current = target
        for part in parts[:-1]:
            if part not in current or not isinstance(current[part], dict):
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value

    def _copy_value(self, value: Any) -> Any:
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        try:
            return json.loads(json.dumps(value, default=str))
        except (TypeError, ValueError):
            return str(value)

    def _generate_summary(self, results: Any) -> Dict[str, Any]:
        """Generate default summary from results"""
        if isinstance(results, list):
            return {
                "total_results": len(results),
                "execution_time": _now_utc_iso(),
            }
        elif isinstance(results, dict):
            return {
                "total_keys": len(results),
                "execution_time": _now_utc_iso(),
            }
        else:
            return {"execution_time": _now_utc_iso()}

    # Convenience methods

    def success(
        self, results: Any, summary: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Create a success response.

        Args:
            results: Module results
            summary: Optional summary data

        Returns:
            Formatted success response
        """
        output = {"results": results}
        if summary:
            output["summary"] = summary
        return output

    def error(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Raise a module error.

        Args:
            message: Error message
            details: Optional error details
        """
        error = ModuleError(message)
        if details:
            error.details = details
        raise error

    def handle_lambda(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        AWS Lambda handler wrapper

        Args:
            event: Lambda event containing input_data
            context: Lambda context

        Returns:
            Module execution result
        """
        # Extract input data from event
        input_data = event.get("parameters", event.get("input_data", {}))

        # Create execution context
        exec_context = {
            "job_id": event.get(
                "job_id",
                context.request_id if hasattr(context, "request_id") else "local",
            ),
            "user_id": event.get("user_id"),
            "organization_id": event.get("organization_id"),
        }

        # Run module
        return self.run(input_data, exec_context)

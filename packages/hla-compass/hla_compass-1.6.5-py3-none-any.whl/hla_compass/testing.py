"""
Testing utilities for HLA-Compass modules
"""

import logging
import importlib.util
from pathlib import Path
from typing import Any, Callable, Optional, List, Dict
from datetime import datetime, UTC
import sys
import os
import uuid

from .types import ExecutionContext
from .module import Module


logger = logging.getLogger(__name__)


def _now_utc() -> datetime:
    return datetime.now(UTC)


class MockAPI:
    """Mock API client for testing"""

    def __init__(
        self,
        data: Optional[Dict[str, Any]] = None,
        *,
        use_devkit: bool = False,
        use_real_storage: bool = False,
    ):
        """
        Initialize mock API with test data.

        Args:
            data: Dictionary of test data
            use_devkit: Whether to use devkit container for real database access
        """
        self.data = data or self._get_default_data()
        self.call_history = []
        self.use_devkit = use_devkit
        self.use_real_storage = use_real_storage

        if self.use_devkit:
            self._setup_devkit_connection()

    def _setup_devkit_connection(self):
        """Set up connection to devkit container services"""
        try:
            import psycopg2

            self.db_connection = psycopg2.connect(
                host="localhost",
                port=5432,
                database="hla_compass",
                user="postgres",
                password="postgres",
            )
        except ImportError:
            logger.warning(
                "psycopg2 not available - install with: pip install psycopg2-binary"
            )
            self.use_devkit = False
        except Exception as e:
            logger.warning(f"Could not connect to devkit database: {e}")
            self.use_devkit = False

    def _get_default_data(self) -> Dict[str, Any]:
        """Get default test data"""
        return {
            "peptides": [
                {
                    "id": "pep1",
                    "sequence": "MLLSVPLLL",
                    "length": 9,
                    "mass": 969.61,
                    "charge": 0,
                },
                {
                    "id": "pep2",
                    "sequence": "SIINFEKL",
                    "length": 8,
                    "mass": 963.54,
                    "charge": 0,
                },
            ],
            "proteins": [
                {
                    "id": "prot1",
                    "accession": "P12345",
                    "gene_name": "TEST1",
                    "organism": "Homo sapiens",
                    "sequence": "MLLSVPLLLGLLGLVAAD",
                    "length": 18,
                }
            ],
            "samples": [
                {
                    "id": "sample1",
                    "name": "Test Sample 1",
                    "sample_type": "tissue",
                    "tissue": "lung",
                    "disease": "cancer",
                }
            ],
        }

    def _record_call(self, method: str, **kwargs):
        """Record API call for verification"""
        self.call_history.append(
            {"method": method, "kwargs": kwargs, "timestamp": _now_utc()}
        )

    def get_peptides(
        self, filters: Optional[Dict[str, Any]] = None, limit: int = 1000, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Mock get_peptides"""
        self._record_call("get_peptides", filters=filters, limit=limit, offset=offset)

        result = self.data["peptides"]

        # Apply filters
        if filters:
            if "sequence" in filters:
                result = [p for p in result if filters["sequence"] in p["sequence"]]
            if "min_length" in filters:
                result = [p for p in result if p["length"] >= filters["min_length"]]
            if "max_length" in filters:
                result = [p for p in result if p["length"] <= filters["max_length"]]

        # Apply pagination
        return result[offset:offset + limit]

    def get_proteins(
        self, filters: Optional[Dict[str, Any]] = None, limit: int = 1000, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Mock get_proteins"""
        self._record_call("get_proteins", filters=filters, limit=limit, offset=offset)
        return self.data["proteins"][offset:offset + limit]

    def get_samples(
        self, filters: Optional[Dict[str, Any]] = None, limit: int = 1000, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Mock get_samples"""
        self._record_call("get_samples", filters=filters, limit=limit, offset=offset)
        return self.data["samples"][offset:offset + limit]

    def get_peptide(self, peptide_id: str) -> Dict[str, Any]:
        """Mock get_peptide"""
        self._record_call("get_peptide", peptide_id=peptide_id)
        for p in self.data["peptides"]:
            if p["id"] == peptide_id:
                return p
        raise ValueError(f"Peptide {peptide_id} not found")


class MockStorage:
    """Mock storage client for testing"""

    def __init__(self):
        """Initialize mock storage"""
        self.files = {}
        self.call_history = []

    def put_object(
        self,
        key: str,
        body: bytes,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        """Mock put_object"""
        self.call_history.append(
            {
                "method": "put_object",
                "key": key,
                "size": len(body),
                "content_type": content_type,
                "metadata": metadata,
            }
        )

        self.files[key] = {
            "body": body,
            "content_type": content_type,
            "metadata": metadata or {},
            "timestamp": _now_utc(),
        }

        return f"s3://test-bucket/{key}"

    def get_object(self, key: str) -> bytes:
        """Mock get_object"""
        if key in self.files:
            return self.files[key]["body"]
        raise ValueError(f"File {key} not found")

    def list_objects(self, prefix: Optional[str] = None) -> List[Dict[str, Any]]:
        """Mock list_objects"""
        result = []
        for key, data in self.files.items():
            if prefix is None or key.startswith(prefix):
                result.append(
                    {
                        "key": key,
                        "size": len(data["body"]),
                        "last_modified": data["timestamp"],
                    }
                )
        return result


class MockContext:
    """Create mock execution context for testing"""

    @staticmethod
    def _create_storage_client(*, opt_in: bool = False):
        """Create storage client for testing"""
        # Only use real storage when explicitly requested
        if opt_in:
            try:
                import boto3
                from botocore.client import Config

                endpoint = os.getenv("S3_ENDPOINT_URL")
                if endpoint:
                    # Local development with MinIO
                    logger.info(
                        f"Creating local storage client with endpoint: {endpoint}"
                    )
                    return boto3.client(
                        "s3",
                        endpoint_url=endpoint,
                        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "minioadmin"),
                        aws_secret_access_key=os.getenv(
                            "AWS_SECRET_ACCESS_KEY", "minioadmin"
                        ),
                        config=Config(
                            signature_version="s3v4", s3={"addressing_style": "path"}
                        ),
                    )
                else:
                    # Use AWS S3
                    return boto3.client("s3")
            except ImportError:
                logger.warning("boto3 not installed - using mock storage")
                return MockStorage()

        return MockStorage()

    @staticmethod
    def create(
        job_id: str = "test-job-123",
        user_id: str = "test-user",
        organization_id: str = "test-org",
        tier: str = "foundational",
        api_data: Optional[Dict[str, Any]] = None,
        use_devkit: bool = False,
        use_real_storage: bool = False,
        mode: str = "interactive",
    ) -> ExecutionContext:
        """
        Create mock execution context.

        Args:
            job_id: Job identifier
            user_id: User identifier
            organization_id: Organization identifier
            tier: Subscription tier
            api_data: Optional API test data
            use_devkit: Whether to connect to local devkit services
            use_real_storage: Use real S3/MinIO instead of mock
            mode: Execution mode flag ("interactive", "async", or "workflow") propagated to module context

        Returns:
            Mock execution context
        """
        return {
            "job_id": job_id,
            "user_id": user_id,
            "organization_id": organization_id,
            "tier": tier,
            "mode": mode,
            "api": MockAPI(
                api_data,
                use_devkit=use_devkit,
                use_real_storage=use_real_storage,
            ),
            "storage": MockContext._create_storage_client(opt_in=use_real_storage),
            "execution_time": _now_utc(),
        }


class ModuleTester:
    """Test harness for HLA-Compass modules"""

    def __init__(self):
        """Initialize module tester"""
        self.logger = logging.getLogger(f"{__name__}.ModuleTester")
        self.use_devkit = False
        self.use_real_storage = False

    def configure_local_devkit(self, *, use_real_storage: bool = False):
        """Configure tester to use local devkit container.

        Args:
            use_real_storage: When True, use the configured S3/MinIO client instead of the in-memory mock.
        """
        self.use_devkit = True
        self.use_real_storage = use_real_storage

    def test_local(
        self,
        module_path: str,
        input_data: dict[str, Any],
        context: ExecutionContext | None = None,
    ) -> dict[str, Any]:
        """
        Test module locally.

        Args:
            module_path: Path to module's main.py
            input_data: Input data for module
            context: Optional execution context (will create mock if not provided)

        Returns:
            Module execution result
        """
        if context is None:
            context = MockContext.create(
                use_devkit=self.use_devkit,
                use_real_storage=self.use_real_storage,
            )

        # Load module
        module = self._load_module(module_path)

        # Execute
        try:
            result = module(input_data, context)
            self.logger.info("Module executed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Module execution failed: {e}")
            raise

    def _load_module(self, module_path: str) -> Callable:
        """Load module from file"""
        module_path = Path(module_path)

        if not module_path.exists():
            raise ValueError(f"Module not found: {module_path}")

        # Load module dynamically
        module_name = f"hla_compass_test_{uuid.uuid4().hex}"
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None or spec.loader is None:
            raise ValueError(f"Cannot load module from {module_path}")

        module = importlib.util.module_from_spec(spec)
        previous = sys.modules.pop(module_name, None)
        sys.modules[module_name] = module
        try:
            spec.loader.exec_module(module)

            # Prefer top-level execute for simple function modules
            if hasattr(module, "execute"):
                return module.execute

            # Otherwise, find a Module subclass and wrap it to call run()
            mod_class = None
            for name in dir(module):
                obj = getattr(module, name)
                try:
                    from .module import Module as _BaseModule  # local import to avoid cycles
                except Exception:
                    _BaseModule = Module
                if (
                    isinstance(obj, type)
                    and issubclass(obj, _BaseModule)
                    and obj is not _BaseModule
                ):
                    mod_class = obj
                    break

            if not mod_class:
                raise ValueError(
                    "Module must have an 'execute' function or a class inheriting from hla_compass.Module"
                )

            def _runner(input_data, context):
                instance = mod_class()
                return instance.run(input_data, context)

            return _runner
        finally:
            sys.modules.pop(module_name, None)
            if previous is not None:
                sys.modules[module_name] = previous

    def test_with_class(
        self,
        module_class: type[Module],
        input_data: dict[str, Any],
        context: ExecutionContext | None = None,
    ) -> dict[str, Any]:
        """
        Test module class that inherits from Module base class.

        Args:
            module_class: Module class
            input_data: Input data
            context: Optional execution context

        Returns:
            Module execution result
        """
        if context is None:
            context = MockContext.create(
                use_devkit=self.use_devkit,
                use_real_storage=self.use_real_storage,
            )

        # Create module instance
        module = module_class()

        # Execute using run method
        return module.run(input_data, context)

    def quickstart(
        self,
        module_class: type[Module],
        sample_input: dict[str, Any] | None = None,
        *,
        mode: str = "interactive",
        use_devkit: bool | None = None,
        use_real_storage: bool | None = None,
    ) -> dict[str, Any]:
        """
        Run a module class using a generated context and sample data.

        Args:
            module_class: Module subclass to execute.
            sample_input: Optional input payload (defaults to manifest defaults).
            mode: Execution mode to stamp into the context ("interactive", "async", "workflow").
            use_devkit: Override tester devkit flag for this run.
            use_real_storage: Override tester storage flag for this run.

        Returns:
            Module execution result dictionary.
        """
        manifest_defaults = self._derive_defaults_from_manifest(module_class)
        input_payload = sample_input or manifest_defaults or {}

        context = MockContext.create(
            use_devkit=self.use_devkit if use_devkit is None else use_devkit,
            use_real_storage=self.use_real_storage if use_real_storage is None else use_real_storage,
            mode=mode,
        )

        self.logger.info("Running module quickstart with payload: %s", input_payload)
        return self.test_with_class(module_class, input_payload, context)

    def _derive_defaults_from_manifest(self, module_class: type[Module]) -> dict[str, Any]:
        try:
            module_instance = module_class()
        except Exception as exc:
            self.logger.warning("Could not instantiate module class %s: %s", module_class.__name__, exc)
            return {}

        inputs = module_instance.manifest.get("inputs", {})
        defaults: dict[str, Any] = {}

        if isinstance(inputs, dict):
            if inputs.get("type") == "object" and "properties" in inputs:
                for name, schema in inputs.get("properties", {}).items():
                    if "default" in schema:
                        defaults[name] = schema["default"]
            else:
                for name, schema in inputs.items():
                    if isinstance(schema, dict) and "default" in schema:
                        defaults[name] = schema["default"]

        if not defaults:
            self.logger.info("No defaults found in manifest; quickstart will use empty input payload")

        return defaults

    def create_test_suite(
        self, module_path: str, test_cases: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Run multiple test cases.

        Args:
            module_path: Path to module
            test_cases: List of test cases with 'input' and 'expected' keys

        Returns:
            Test results
        """
        results = {
            "total": len(test_cases),
            "passed": 0,
            "failed": 0,
            "errors": [],
            "details": [],
        }

        for i, test_case in enumerate(test_cases):
            test_name = test_case.get("name", f"Test {i + 1}")

            try:
                result = self.test_local(
                    module_path, test_case["input"], test_case.get("context")
                )

                # Check expected output if provided
                if "expected" in test_case:
                    if self._validate_output(result, test_case["expected"]):
                        results["passed"] += 1
                        status = "passed"
                    else:
                        results["failed"] += 1
                        status = "failed"
                        results["errors"].append(f"{test_name}: Output mismatch")
                else:
                    results["passed"] += 1
                    status = "passed"

                results["details"].append(
                    {"name": test_name, "status": status, "output": result}
                )

            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"{test_name}: {str(e)}")
                results["details"].append(
                    {"name": test_name, "status": "error", "error": str(e)}
                )

        return results

    def _validate_output(self, actual: Any, expected: Any) -> bool:
        """Validate output against expected"""
        if isinstance(expected, dict) and isinstance(actual, dict):
            for key, value in expected.items():
                if key not in actual:
                    return False
                if not self._validate_output(actual[key], value):
                    return False
            return True
        else:
            return actual == expected

    def benchmark(
        self, module_path: str, input_data: dict[str, Any], iterations: int = 10
    ) -> dict[str, Any]:
        """
        Benchmark module performance.

        Args:
            module_path: Path to module
            input_data: Input data
            iterations: Number of iterations

        Returns:
            Benchmark results
        """
        import time

        context = MockContext.create()
        module = self._load_module(module_path)

        # Warmup
        module(input_data, context)

        # Benchmark
        times = []
        for _ in range(iterations):
            start = time.time()
            module(input_data, context)
            times.append(time.time() - start)

        return {
            "iterations": iterations,
            "total_time": sum(times),
            "average_time": sum(times) / len(times),
            "min_time": min(times),
            "max_time": max(times),
            "times": times,
        }

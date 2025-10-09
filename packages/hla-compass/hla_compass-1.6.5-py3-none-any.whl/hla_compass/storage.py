"""
Storage utilities for HLA-Compass modules.

Quick Reference
===============
- ``save_file``: accepts ``bytes``/``str`` or any file-like object with ``read()``;
  metadata values are coerced to strings automatically.
- ``save_json`` / ``save_csv`` / ``save_text`` / ``save_html``: convenience wrappers
  that call ``save_file`` with sensible MIME types.
- ``save_excel`` and ``save_figure``: emit rich artifacts; Excel export requires the
  optional ``hla-compass[data]`` extra (``pandas`` + ``xlsxwriter``).
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union, BinaryIO, IO
from io import BytesIO
import mimetypes

logger = logging.getLogger(__name__)


class StorageError(Exception):
    """Storage operation error"""


class MissingDependencyError(StorageError):
    """Raised when an optional dependency is required but not installed."""


class Storage:
    """
    Storage utilities for module results.

    Provides simplified access to S3 storage for saving module outputs.
    """

    def __init__(self, storage_client):
        """
        Initialize storage utilities.

        Args:
            storage_client: Storage client from execution context
        """
        self.client = storage_client
        self.logger = logging.getLogger(f"{__name__}.Storage")

    def save_file(
        self,
        filename: str,
        content: Union[bytes, str, BinaryIO, IO[bytes], IO[str]],
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Save a file to result storage.

        Args:
            filename: Name of the file
            content: File content (bytes, string, or file-like object)
            content_type: MIME type (auto-detected if not provided)
            metadata: Additional metadata

        Returns:
            URL or identifier of the saved file
        """
        try:
            body = self._coerce_content(content)

            # Auto-detect content type if not provided
            if content_type is None:
                content_type, _ = mimetypes.guess_type(filename)
                if content_type is None:
                    content_type = "application/octet-stream"

            self.logger.debug(f"Saving file: {filename} ({content_type})")

            normalized_metadata = self._normalize_metadata(metadata)

            result = self.client.put_object(
                key=filename,
                body=body,
                content_type=content_type,
                metadata=normalized_metadata,
            )

            self.logger.info(f"File saved successfully: {filename}")
            return result

        except Exception as e:
            self.logger.error(f"Failed to save file {filename}: {e}")
            raise StorageError(f"Failed to save file: {str(e)}")

    def _coerce_content(
        self, content: Union[bytes, str, BinaryIO, IO[bytes], IO[str]]
    ) -> bytes:
        if isinstance(content, bytes):
            return content
        if isinstance(content, bytearray):
            return bytes(content)
        if isinstance(content, memoryview):
            return content.tobytes()
        if isinstance(content, str):
            return content.encode("utf-8")

        if hasattr(content, "read"):
            data = content.read()
            seek = getattr(content, "seek", None)
            if callable(seek):  # reset pointer when possible
                try:
                    seek(0)
                except Exception:  # pragma: no cover - optional
                    pass
            if isinstance(data, bytes):
                return data
            if isinstance(data, str):
                return data.encode("utf-8")
            raise StorageError(
                "Unsupported content stream type; expected bytes or str from file-like read()"
            )

        raise StorageError("Unsupported content type for storage upload")

    def _normalize_metadata(self, metadata: Optional[Dict[str, Any]]) -> Dict[str, str]:
        if not metadata:
            return {}

        normalized: Dict[str, str] = {}
        for key, value in metadata.items():
            if value is None:
                continue

            if isinstance(value, (list, tuple, set)):
                normalized_value = ",".join(str(item) for item in value)
            else:
                normalized_value = str(value)

            normalized[str(key)] = normalized_value

        return normalized

    def save_json(self, filename: str, data: Any, indent: int = 2) -> str:
        """
        Save JSON data to storage.

        Args:
            filename: Name of the file (should end with .json)
            data: Data to save as JSON
            indent: JSON indentation

        Returns:
            URL or identifier of the saved file
        """
        if not filename.endswith(".json"):
            filename += ".json"

        content = json.dumps(data, indent=indent, default=str)
        return self.save_file(filename, content, "application/json")

    def save_csv(self, filename: str, dataframe, index: bool = False) -> str:
        """
        Save pandas DataFrame as CSV.

        Args:
            filename: Name of the file (should end with .csv)
            dataframe: Pandas DataFrame
            index: Whether to include index

        Returns:
            URL or identifier of the saved file
        """
        if not filename.endswith(".csv"):
            filename += ".csv"

        content = dataframe.to_csv(index=index)
        return self.save_file(filename, content, "text/csv")

    def save_excel(
        self, filename: str, dataframe, sheet_name: str = "Sheet1", index: bool = False
    ) -> str:
        """
        Save pandas DataFrame as Excel file.

        Args:
            filename: Name of the file (should end with .xlsx)
            dataframe: Pandas DataFrame or dict of DataFrames
            sheet_name: Sheet name (if single DataFrame)
            index: Whether to include index

        Returns:
            URL or identifier of the saved file
        """
        if not filename.endswith(".xlsx"):
            filename += ".xlsx"

        # Import pandas lazily to avoid hard dependency for non-data users
        try:
            import pandas as pd  # type: ignore
        except Exception as e:  # pragma: no cover
            raise MissingDependencyError(
                "Excel export requires optional dependencies. Install via:\n"
                "  pip install 'hla-compass[data]'\n"
                f"(missing pandas: {e})"
            ) from e

        # Create Excel file in memory
        buffer = BytesIO()

        try:
            if isinstance(dataframe, dict):
                # Multiple sheets
                with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:  # type: ignore
                    for name, df in dataframe.items():
                        df.to_excel(writer, sheet_name=name, index=index)
            else:
                # Single sheet
                dataframe.to_excel(buffer, sheet_name=sheet_name, index=index)
        except Exception as e:  # pragma: no cover
            # Provide clearer guidance when xlsxwriter engine is missing
            raise MissingDependencyError(
                "Failed to write Excel file. Ensure 'xlsxwriter' is installed.\n"
                "Install via: pip install 'hla-compass[data]'\n"
                f"(original error: {e})"
            ) from e

        buffer.seek(0)
        return self.save_file(
            filename,
            buffer.read(),
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def save_text(self, filename: str, content: str, encoding: str = "utf-8") -> str:
        """
        Save text content to storage.

        Args:
            filename: Name of the file
            content: Text content
            encoding: Text encoding

        Returns:
            URL or identifier of the saved file
        """
        return self.save_file(filename, content.encode(encoding), "text/plain")

    def save_html(self, filename: str, content: str) -> str:
        """
        Save HTML content to storage.

        Args:
            filename: Name of the file (should end with .html)
            content: HTML content

        Returns:
            URL or identifier of the saved file
        """
        if not filename.endswith(".html"):
            filename += ".html"

        return self.save_file(filename, content, "text/html")

    def save_figure(
        self, filename: str, figure, format: str = "png", dpi: int = 150
    ) -> str:
        """
        Save matplotlib figure to storage.

        Args:
            filename: Name of the file
            figure: Matplotlib figure object
            format: Image format (png, svg, pdf)
            dpi: Resolution for raster formats

        Returns:
            URL or identifier of the saved file
        """
        # Ensure correct extension
        if not filename.endswith(f".{format}"):
            filename = f"{filename}.{format}"

        # Save figure to buffer
        buffer = BytesIO()
        figure.savefig(buffer, format=format, dpi=dpi, bbox_inches="tight")
        buffer.seek(0)

        # Determine content type
        content_types = {
            "png": "image/png",
            "svg": "image/svg+xml",
            "pdf": "application/pdf",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
        }
        content_type = content_types.get(format, "application/octet-stream")

        return self.save_file(filename, buffer.read(), content_type)

    def create_download_url(self, filename: str, expires_in: int = 3600) -> str:
        """
        Create a pre-signed download URL.

        Args:
            filename: Name of the file
            expires_in: URL expiration time in seconds

        Returns:
            Pre-signed download URL
        """
        try:
            return self.client.create_presigned_url(key=filename, expires_in=expires_in)
        except Exception as e:
            self.logger.error(f"Failed to create download URL: {e}")
            raise StorageError(f"Failed to create download URL: {str(e)}")

    def list_files(self, prefix: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List files in storage.

        Args:
            prefix: Optional prefix to filter files

        Returns:
            List of file metadata
        """
        try:
            return self.client.list_objects(prefix=prefix)
        except Exception as e:
            self.logger.error(f"Failed to list files: {e}")
            raise StorageError(f"Failed to list files: {str(e)}")

    def delete_file(self, filename: str) -> bool:
        """
        Delete a file from storage.

        Args:
            filename: Name of the file to delete

        Returns:
            True if successful
        """
        try:
            self.client.delete_object(key=filename)
            self.logger.info(f"Deleted file: {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete file {filename}: {e}")
            raise StorageError(f"Failed to delete file: {str(e)}")


# Convenience function for working with multiple files
class ResultBundle:
    """
    Helper for bundling multiple result files.
    """

    def __init__(self, storage: Storage, prefix: str = "results"):
        """
        Initialize result bundle.

        Args:
            storage: Storage instance
            prefix: Prefix for all files in the bundle
        """
        self.storage = storage
        self.prefix = prefix
        self.files = []

    def add_json(self, name: str, data: Any) -> str:
        """Add JSON file to bundle"""
        filename = f"{self.prefix}/{name}.json"
        url = self.storage.save_json(filename, data)
        self.files.append({"name": name, "type": "json", "url": url})
        return url

    def add_csv(self, name: str, dataframe) -> str:
        """Add CSV file to bundle"""
        filename = f"{self.prefix}/{name}.csv"
        url = self.storage.save_csv(filename, dataframe)
        self.files.append({"name": name, "type": "csv", "url": url})
        return url

    def add_figure(self, name: str, figure, format: str = "png") -> str:
        """Add figure to bundle"""
        filename = f"{self.prefix}/{name}.{format}"
        url = self.storage.save_figure(filename, figure, format)
        self.files.append({"name": name, "type": format, "url": url})
        return url

    def get_manifest(self) -> Dict[str, Any]:
        """Get manifest of all files in bundle"""
        return {
            "prefix": self.prefix,
            "file_count": len(self.files),
            "files": self.files,
        }

    def save_manifest(self) -> str:
        """Save bundle manifest"""
        return self.storage.save_json(
            f"{self.prefix}/manifest.json", self.get_manifest()
        )

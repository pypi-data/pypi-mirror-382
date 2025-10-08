"""Deployment utilities for Plotly Cloud CLI."""

import json
import os
import pathlib
import re
import zipfile
from typing import Optional

import httpx
import tomli
import tomli_w

from plotly_cloud._api_types import App, AppRequest
from plotly_cloud._cloud_env import cloud_config
from plotly_cloud._definitions import AppDeploymentConfig
from plotly_cloud._oauth import OAuthClient

from .exceptions import (
    APIError,
    AppCreationError,
    AppPublishError,
    DependencyValidationError,
    DeploymentClientError,
    DeploymentError,
    FileSizeError,
    FileSystemError,
    ForbiddenError,
    NetworkError,
    PackagingError,
    PlotlyCloudError,
)

# Maximum allowed zip file size (80MB)
MAX_ZIP_SIZE = 80 * 1024 * 1024

# Required dependencies for deployment
REQUIRED_DEPENDENCIES = {"dash"}


def validate_dependencies(project_path: str) -> None:
    """
    Validate that the project has required dependencies (dash).

    Checks requirements.txt or pyproject.toml for the required dependencies.

    Args:
        project_path: Path to the project directory

    Returns:
        True if all required dependencies are found, False otherwise
    """
    requirements_path = os.path.join(project_path, "requirements.txt")
    pyproject_path = os.path.join(project_path, "pyproject.toml")

    found_deps = set()

    # Check requirements.txt
    if os.path.exists(requirements_path):
        try:
            with open(requirements_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        # Extract package name (handle versions, extras, etc.)
                        # Split on version operators and extras
                        dep_name = re.split(r"[>=<!\[~]", line)[0].strip()
                        if dep_name:  # Only add non-empty names
                            found_deps.add(dep_name.lower())
        except Exception as err:
            raise DependencyValidationError(f"Error reading requirement file: {requirements_path}") from err

    # Check pyproject.toml
    elif os.path.exists(pyproject_path):
        try:
            with open(pyproject_path, "rb") as f:
                data = tomli.load(f)

            # Check different possible locations for dependencies
            dep_sources = [
                data.get("project", {}).get("dependencies", []),
                data.get("tool", {}).get("poetry", {}).get("dependencies", {}),
                data.get("build-system", {}).get("requires", []),
            ]

            for deps in dep_sources:
                if isinstance(deps, list):
                    # Handle list format (like project.dependencies)
                    for dep in deps:
                        if isinstance(dep, str):
                            dep_name = re.split(r"[>=<!\[~]", dep)[0].strip()
                            if dep_name:  # Only add non-empty names
                                found_deps.add(dep_name.lower())
                elif isinstance(deps, dict):
                    # Handle dict format (like poetry dependencies)
                    for dep_name in deps.keys():
                        found_deps.add(dep_name.lower())
        except Exception as err:
            raise DependencyValidationError(f"Error reading pyproject file: {pyproject_path}") from err
    else:
        raise FileNotFoundError("No requirements.txt or pyproject.toml found in project directory.")

    # Check if all required dependencies are present
    missing_deps = REQUIRED_DEPENDENCIES - found_deps

    if missing_deps:
        raise DependencyValidationError(
            f"Missing required dependencies: {', '.join(sorted(missing_deps))}.\n\n"
            ""
            "please add them to your requirements.txt or pyproject.toml"
        )


def parse_gitignore(project_path: str) -> set[str]:
    """Parse .gitignore file and return set of patterns to exclude."""
    gitignore_path = os.path.join(project_path, ".gitignore")
    exclude_patterns = set()

    # Always exclude common virtual environment directories
    exclude_patterns.update(
        {
            "venv/",
            "venv",
            ".venv/",
            ".venv",
            "env/",
            "env",
            ".env/",
            ".env",
            "__pycache__/",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".Python",
            "build/",
            "develop-eggs/",
            "dist/",
            "downloads/",
            "eggs/",
            ".eggs/",
            "lib/",
            "lib64/",
            "parts/",
            "sdist/",
            "var/",
            "wheels/",
            "*.egg-info/",
            ".installed.cfg",
            "*.egg",
            "MANIFEST",
            ".git/",
            ".gitignore",
        }
    )

    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        exclude_patterns.add(line)
        except Exception as e:
            raise FileSystemError("Warning: Could not read .gitignore file") from e

    return exclude_patterns


def should_exclude_path(path: str, exclude_patterns: set[str]) -> bool:
    """Check if a path should be excluded based on gitignore patterns."""
    path_parts = pathlib.Path(path).parts

    for pattern in exclude_patterns:
        # Handle directory patterns (ending with /)
        if pattern.endswith("/"):
            pattern_name = pattern.rstrip("/")
            if pattern_name in path_parts:
                return True
        # Handle wildcard patterns (basic support)
        elif pattern.startswith("*"):
            extension = pattern[1:]  # Remove the *
            if path.endswith(extension):
                return True
        # Handle exact file patterns (must be exact match at any level)
        elif pattern == os.path.basename(path):
            return True

    return False


async def create_deployment_zip(project_path: str, output_path: str) -> int:
    """
    Create a zip file for deployment, excluding files based on .gitignore.

    Args:
        project_path: Path to the project directory
        output_path: Path where the zip file should be created

    Returns:
        Size of the created zip file in bytes

    Raises:
        ValueError: If zip file exceeds size limit
    """
    exclude_patterns = parse_gitignore(project_path)

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_path):
            # Remove excluded directories from dirs list to avoid walking them
            dirs[:] = [d for d in dirs if not should_exclude_path(os.path.join(root, d), exclude_patterns)]

            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, project_path)

                # Ensure relative_path is a string
                if isinstance(relative_path, bytes):
                    relative_path = relative_path.decode("utf-8")

                # Skip if file should be excluded
                if should_exclude_path(relative_path, exclude_patterns):
                    continue

                # Skip if file is the output zip itself
                if os.path.abspath(file_path) == os.path.abspath(output_path):
                    continue

                try:
                    zipf.write(file_path, relative_path)
                except (OSError, PermissionError):
                    # Skip files that can't be read, continue with others
                    continue

    # Check zip file size
    zip_size = os.path.getsize(output_path)
    if zip_size > MAX_ZIP_SIZE:
        os.remove(output_path)  # Clean up the oversized zip
        raise FileSizeError(
            f"Deployment package is too large ({zip_size / (1024 * 1024):.1f}MB)",
            f"Maximum allowed size is {MAX_ZIP_SIZE / (1024 * 1024):.0f}MB. "
            "Consider excluding more files in your .gitignore.",
        )

    return zip_size


def get_config_path(project_path: str, config_file: str = "plotly-cloud.toml") -> str:
    """Get the full path to the configuration file.

    Args:
        project_path: Path to the project directory
        config_file: Name of the configuration file

    Returns:
        Full path to the configuration file
    """
    return os.path.join(project_path, config_file)


def load_deployment_config(config_path: str) -> AppDeploymentConfig:
    """Load configuration from TOML file.

    Args:
        config_path: Path to the configuration file

    Returns:
        Dictionary containing configuration data
    """
    if not os.path.exists(config_path):
        return {}

    with open(config_path, "rb") as f:
        config: AppDeploymentConfig = tomli.load(f)  # type: ignore
    return config


def save_deployment_config(config: AppDeploymentConfig, config_path: str) -> None:
    """Save configuration to TOML file.

    Args:
        config: Configuration dictionary
        config_path: Path to save the configuration file
    """
    with open(config_path, "wb") as f:
        tomli_w.dump(config, f)


def format_app_url(app_url: Optional[str]) -> str:
    """Format app URL to full HTTPS URL.

    Args:
        app_url: The app URL from the API (just the subdomain part)

    Returns:
        Full HTTPS URL or empty string if app_url is None/empty
    """
    if not app_url:
        return ""
    return f"https://{app_url}.plotly.app"


def _handle_error_response(response: Optional[httpx.Response], operation: str) -> PlotlyCloudError:
    """Handle error responses from API calls.

    Args:
        response: The HTTP response object
        operation: Description of the operation that failed

    Raises:
        Appropriate error based on the response
    """
    if not response:
        return DeploymentError(f"Error performing {operation}")

    # Handle 403 Forbidden specifically
    if response.status_code == 403:
        return ForbiddenError(f"Failed to {operation}: Access forbidden")

    # Parse error based on content type
    content_type = response.headers.get("content-type", "").lower()

    if content_type.startswith("application/json"):
        try:
            error_data = response.json()
            # Try different error message formats - authkit forwards various formats
            error_msg = (
                error_data.get("message")  # Common authkit format
                or error_data.get("error")  # Standard OAuth format
                or "Unknown error"
            )
            error_desc = error_data.get("error_description", "")
        except (json.JSONDecodeError, KeyError):
            error_msg = f"HTTP {response.status_code}"
            error_desc = "Invalid JSON response"
    elif content_type.startswith("text/html"):
        # Extract text from HTML using regex
        html_text = response.text.strip()
        clean_text = re.sub(r"<[^>]+>", "", html_text)  # Remove HTML tags
        clean_text = " ".join(clean_text.split())  # Clean up whitespace
        error_msg = f"HTTP {response.status_code}"
        error_desc = clean_text[:200] + ("..." if len(clean_text) > 200 else "")  # Truncate long HTML
    else:
        # Plain text or other content types
        error_msg = f"HTTP {response.status_code}"
        error_desc = response.text.strip()

    if "create" in operation.lower():
        return AppCreationError(f"Failed to {operation}: {error_msg}", error_desc)
    elif "publish" in operation.lower():
        return AppPublishError(f"Failed to {operation}: {error_msg}", error_desc)
    else:
        return APIError(f"Failed to {operation}: {error_msg}", status_code=response.status_code, details=error_desc)


class DeploymentClient:
    """Client for handling Plotly Cloud deployments."""

    def __init__(self, oauth_client: Optional[OAuthClient] = None):
        self.api_base_url = cloud_config.get_api_base_url().rstrip("/")
        self.oauth_client = oauth_client
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        headers = {"user-agent": "PlotlyCloudCLI"}
        if self.oauth_client:
            access_token = await self.oauth_client.get_access_token()
            if access_token:
                headers["Authorization"] = f"Bearer {access_token}"

        self._client = httpx.AsyncClient(
            timeout=300.0,  # 5 minute timeout
            headers=headers,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    async def _refresh_token_if_needed(self, response: httpx.Response) -> bool:
        """Refresh token if needed based on response. Returns True if token was refreshed."""
        if response.status_code == 401 and self.oauth_client:
            try:
                new_token = await self.oauth_client.refresh_access_token()
                if self._client:
                    self._client.headers["Authorization"] = f"Bearer {new_token}"
                return True
            except Exception:
                # Token refresh failed, continue with original error
                pass
        return False

    async def create_app(self, name: str, zip_path: str = "") -> App:
        """Create a new application and upload deployment in same request.

        Args:
            name: Application name
            zip_path: Path to deployment zip file to upload

        Returns:
            App response from the API

        Raises:
            Exception: If API call fails
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use within async context manager.")

        if not zip_path or not os.path.exists(zip_path):
            raise PackagingError(f"Zip file not found: {zip_path}")

        url = f"https://{self.api_base_url}/api/app"

        try:
            # Create typed request data
            app_request: AppRequest = {"name": name}

            # Upload deployment in same request as app creation
            retry_count = 0
            response = None
            while retry_count <= 1:
                with open(zip_path, "rb") as f:
                    files = {"file": (os.path.basename(zip_path), f, "application/zip")}
                    data = {"json": json.dumps(app_request)}
                    response = await self._client.post(url, data=data, files=files)

                if response.status_code in (200, 201):
                    api_response: App = response.json()
                    return api_response

                token_refreshed = await self._refresh_token_if_needed(response)
                if token_refreshed:
                    retry_count += 1
                else:
                    break

            raise _handle_error_response(response, "create app")
        except httpx.RequestError as e:
            raise NetworkError("Failed to create app", str(e)) from e

    async def publish_app(self, app_id: str, zip_path: str = "") -> App:
        """Publish existing application and upload deployment in same request.

        Args:
            app_id: Application ID
            zip_path: Path to deployment zip file to upload

        Returns:
            App response from the API

        Raises:
            Exception: If API call fails
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use within async context manager.")

        if not zip_path or not os.path.exists(zip_path):
            raise PackagingError(f"Zip file not found: {zip_path}")

        url = f"https://{self.api_base_url}/api/app/{app_id}/publish"

        try:
            # Upload deployment in same request as app publish
            retry_count = 0
            response = None
            while retry_count <= 1:
                with open(zip_path, "rb") as f:
                    files = {"file": (os.path.basename(zip_path), f, "application/zip")}
                    response = await self._client.post(url, files=files)

                if response.status_code in (200, 201):
                    api_response: App = response.json()
                    return api_response

                token_refreshed = await self._refresh_token_if_needed(response)
                if token_refreshed:
                    retry_count += 1
                else:
                    break

            raise _handle_error_response(response, "publish app")
        except httpx.RequestError as e:
            raise NetworkError("Failed to publish app", str(e)) from e

    async def get_app_status(self, app_id: str) -> App:
        """Get application status and details.

        Args:
            app_id: Application ID

        Returns:
            App data from the API

        Raises:
            DeploymentClientError: If client is not initialized
            APIError: If API call fails
            NetworkError: If network request fails
        """
        if not self._client:
            raise DeploymentClientError("Client not initialized. Use within async context manager.")

        url = f"https://{self.api_base_url}/api/app/{app_id}"

        try:
            retry_count = 0
            response = None
            while retry_count <= 1:
                response = await self._client.get(url)

                if response.status_code == 200:
                    api_response: App = response.json()
                    return api_response

                token_refreshed = await self._refresh_token_if_needed(response)
                if token_refreshed:
                    retry_count += 1
                else:
                    break

            raise _handle_error_response(response, "get app status")
        except httpx.RequestError as e:
            raise NetworkError("Failed to get app status", str(e)) from e

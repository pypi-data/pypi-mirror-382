"""RPC interface for Plotly Cloud publishing in dev tools."""

import asyncio
import importlib
import os
import tempfile
from typing import Any

import dash
from typing_extensions import Literal, NotRequired, TypedDict

from plotly_cloud._cloud_env import cloud_config
from plotly_cloud._definitions import AppDeploymentConfig
from plotly_cloud._deploy import (
    DeploymentClient,
    create_deployment_zip,
    format_app_url,
    get_config_path,
    load_deployment_config,
    save_deployment_config,
    validate_dependencies,
)
from plotly_cloud._oauth import OAuthClient
from plotly_cloud.exceptions import TokenError


class PublishOperations:
    check_auth = "initialize"


class PublishOperation(TypedDict):
    """RPC operation structure for dev tools publishing."""

    operation: Literal["initialize", "authenticate", "auth_poll", "publish", "status"]
    data: Any


class RPCResponse(TypedDict):
    """Standard RPC response structure."""

    result: NotRequired[Any]
    error: NotRequired[str]


class PlotlyCloudPublishRPC:
    """RPC handler for Plotly Cloud publishing operations in dev tools."""

    def __init__(self) -> None:
        """Initialize the RPC handler."""
        client_id = cloud_config.get_oauth_client_id()
        self.oauth_client = OAuthClient(client_id)
        self._app_setup = None  # Fallback incase get_app fails.

    def get_project_path(self):
        app = None
        try:
            app = dash.det_app()  # type: ignore
        except Exception:
            app = self._app_setup

        assert app
        app_module = importlib.import_module(app.config.name)
        return os.path.dirname(str(app_module.__file__))

    async def handle_operation(self, publish_operation: PublishOperation) -> RPCResponse:
        """Handle a publish operation from dev tools.

        Args:
            publish_operation: The operation to perform with its data

        Returns:
            RPCResponse with data and optional error

        Raises:
            ValueError: If operation is not supported
        """
        operation_name = publish_operation["operation"]
        data = publish_operation.get("data")

        # Get the method by operation name (direct match)
        if not hasattr(self, operation_name):
            raise ValueError(f"Unsupported operation: {operation_name}")

        try:
            method = getattr(self, operation_name)
            return await method(data)
        except Exception as e:
            return {"error": str(e)}

    async def initialize(self, data: Any) -> RPCResponse:
        is_authenticated = await self.oauth_client.is_authenticated()

        try:
            # Try to refresh the access token so it's still valid
            await self.oauth_client.refresh_access_token()
        except TokenError:
            is_authenticated = False
            self.oauth_client.clear_credentials()

        project_path = self.get_project_path()

        config_path = get_config_path(project_path, os.path.join(project_path, "plotly-cloud.toml"))
        config = load_deployment_config(config_path)

        app_id = config.get("app_id")
        existing = app_id is not None
        status = "new"
        app_name = config.get("name", os.path.basename(project_path))
        app_url = ""

        if app_id is not None and is_authenticated:
            async with DeploymentClient(self.oauth_client) as deploy_client:
                status_data = await deploy_client.get_app_status(app_id)
                status = status_data.get("status", "")
                app_url = format_app_url(status_data.get("app_url", ""))

        return {
            "result": {
                "authenticated": is_authenticated,
                "existing": existing,
                "status": status,
                "app_name": app_name,
                "app_path": project_path,
                "app_id": app_id,
                "app_url": app_url,
            }
        }

    async def authenticate(self, data: Any) -> RPCResponse:
        device_auth = await self.oauth_client.request_device_authorization()
        return {"result": device_auth}

    async def auth_poll(self, data: Any) -> RPCResponse:
        device_code = data.get("device_code")
        status_code, response = await self.oauth_client.check_authentication_status(device_code)
        if status_code == 200:
            await self.oauth_client._save_credentials(dict(response))
            return {"result": {"success": True}}
        else:
            error = response.get("error", "unknown_error")
            if error == "authorization_pending":
                return {"result": {}}
            elif error == "slow_down":
                delay = 1 + data.get("delayed", 0)
                return {"result": {"delay": delay}}
            elif error == "expired_token":
                return {"result": {"try_again": True}}
            elif error == "access_denied":
                return {"error": "Access denied by user"}
            else:
                return {"error": "Authentication Failed"}

    async def status(self, data: Any) -> RPCResponse:
        app_id = data.get("app_id")
        async with DeploymentClient(self.oauth_client) as deploy_client:
            status_data = await deploy_client.get_app_status(app_id)
            app_url = format_app_url(status_data.get("app_url", ""))
            return {"result": {"status": status_data.get("status", ""), "app_url": app_url}}

    async def publish(self, data: Any) -> RPCResponse:
        app_path = data.get("app_path")
        app_id = data.get("app_id")
        app_name = data.get("app_name")

        config_path = get_config_path(app_path)

        temp_file = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
        zip_path = temp_file.name
        temp_file.close()

        validate_dependencies(app_path)

        await create_deployment_zip(app_path, zip_path)

        async with DeploymentClient(self.oauth_client) as deploy_client:
            if app_id:
                # update app
                app_data = await deploy_client.publish_app(app_id, zip_path)
                config = load_deployment_config(config_path)

                if config.get("app_url") != app_data.get("app_url"):
                    config["app_url"] = app_data.get("app_url", "")
                    save_deployment_config(config, config_path)

                return {"result": {"app_id": app_id, "app_url": format_app_url(app_data.get("app_url"))}}
            else:
                # create new app
                app_data = await deploy_client.create_app(app_name, zip_path)

                config: AppDeploymentConfig = {
                    "name": app_name,
                    "app_id": app_data.get("id", ""),
                    "app_url": app_data.get("app_url", ""),
                }

                save_deployment_config(config, config_path)

                return {"result": {"app_id": app_data.get("id"), "app_url": format_app_url(app_data.get("app_url"))}}

    async def wait_auth(self, data: Any):
        # this just wait to circumvent setTimeout with window.open restriction.
        await asyncio.sleep(2)
        return {"result": {}}

    async def logout(self, data: Any):
        await self.oauth_client.logout()
        return {"result": {}}

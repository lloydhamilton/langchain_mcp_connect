import asyncio
import json
from asyncio import gather
from contextlib import asynccontextmanager
from logging import getLogger

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import Tool
from pydantic import BaseModel, Field

from .data_models.mcp_servers import McpServers

log = getLogger("mcp_services.get_servers")


class ConfigurationError(Exception):
    """Error raised when there is an issue with the configuration."""

    pass


class CallInput(BaseModel):
    """Data model for call tool input."""

    name: str = Field(
        ...,
        description="The name of the tool to call from the server.",
        examples=["retrieve-documents"],
    )
    arguments: dict = Field(
        ...,
        description="The arguments to pass to the tool. This should be inferred "
        "from the list tool schema.",
        examples=[{"query": "lloyd hamilton data engineer", "k": 1, "threshold": 0.5}],
    )


class LangChainMcp:
    """List all the available tools for all servers."""

    def __init__(self, config_path: str = "./claude_mcp_config.json"):
        self.config_path = config_path
        self._server_configs: McpServers | None = None

    @property
    def server_configs(self) -> McpServers:
        """Get the server configurations."""
        if self._server_configs is None:
            self._server_configs = self._load_config()
        return self._server_configs

    def _load_config(self) -> McpServers:
        """Load mcp server configurations from file."""
        if self._server_configs is None:
            try:
                with open(self.config_path) as f:
                    config_data = json.load(f)
                self._server_configs = McpServers(**config_data)
            except FileNotFoundError as e:
                raise ConfigurationError(
                    f"Configuration file not found: {self.config_path}"
                ) from e
            except json.JSONDecodeError as e:
                raise ConfigurationError(
                    f"Invalid JSON in configuration file: {self.config_path}"
                ) from e
        return self._server_configs

    @staticmethod
    @asynccontextmanager
    async def get_session(server_params: StdioServerParameters) -> ClientSession:
        """Get a client MCP session.

        Args:
            server_params (StdioServerParameters): The server parameters.

        Yields:
            ClientSession: The client session for the MCP server.

        """
        async with (
            stdio_client(server_params) as (read, write),
            ClientSession(read, write) as session,
        ):
            await session.initialize()
            yield session

    async def _fetch_server_tools(
        self, server_name: str, params: StdioServerParameters
    ) -> tuple[str, Tool]:
        """List the available tools to call.

        Args:
            server_name (Server): The name of the server to create a session.
            params (StdioServerParameters): The server parameters.

        Returns:
            tuple[str, Tool]: The server name and the available tools.

        """
        log.info(f"Listing tools for server: {server_name}")
        async with self.get_session(params) as session:
            list_tool_results = await session.list_tools()
            return server_name, list_tool_results

    async def fetch_all_server_tools(self) -> dict:
        """List the available tools for all servers.

        Returns:
            dict: The available tools for all servers in the format
                {server_name: tools}.
        """
        coroutines = [
            self._fetch_server_tools(server_name, params)
            for server_name, params in self.server_configs.mcpServers.items()
        ]
        results = await gather(*coroutines)
        return {name: tools.model_dump(mode="json") for name, tools in results}

    async def _list_server_resources(
        self, server_name: str, params: StdioServerParameters
    ) -> tuple[str, Tool]:
        """List the available resources on a server.

        Args:
            server_name (Server): The name of the server to create a session.
            params (StdioServerParameters): The server parameters.

        Returns:
            tuple[str, Tool]: The server name and the available resources.

        """
        log.info(f"Listing resources for server: {server_name}")
        async with self.get_session(params) as session:
            list_resources_results = await session.list_resources()
            return server_name, list_resources_results

    async def list_all_server_resources(self) -> dict:
        """List the available resources for all servers.

        Returns:
            dict: The available resources for all servers in the format
                {server_name: resources}.
        """
        coroutines = [
            self._list_server_resources(server_name, params)
            for server_name, params in self.server_configs.mcpServers.items()
        ]
        results = await gather(*coroutines)
        return {name: resources.model_dump(mode="json") for name, resources in results}

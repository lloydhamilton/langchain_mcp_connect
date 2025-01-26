import json
from asyncio import gather
from contextlib import asynccontextmanager
from logging import getLogger
from typing import Never

try:
    from jsonschema_pydantic import jsonschema_to_pydantic
    from langchain_core.tools import BaseTool
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from mcp.types import ListToolsResult, Tool
    from pydantic import BaseModel

except ImportError as e:
    raise ImportError(
        f"Please install the required packages by running: {e}"
        "pip install langchain-core mcp jsonschema-pydantic"
    ) from e


from .data_models.mcp_servers import McpServers

log = getLogger("mcp_services.LangChainMcp")


class ConfigurationError(Exception):
    """Error raised when there is an issue with the configuration."""

    pass


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
            except FileNotFoundError as error:
                raise ConfigurationError(
                    f"Configuration file not found: {self.config_path}"
                ) from error
            except json.JSONDecodeError as error:
                raise ConfigurationError(
                    f"Invalid JSON in configuration file: {self.config_path}"
                ) from error
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

    async def _fetch_langchain_tools(
        self, server_name: str, params: StdioServerParameters
    ) -> list[BaseTool]:
        """List the available tools to call.

        Args:
            server_name (Server): The name of the server to create a session.
            params (StdioServerParameters): The server parameters.

        Returns:
            list[BaseTool]: The available tools for the server as LangChain tools.

        """
        log.info(f"Listing tools for server: {server_name}")
        async with self.get_session(params) as session:
            list_tool_results: ListToolsResult = await session.list_tools()
            all_tools: list[BaseTool] = []
            for tool in list_tool_results.tools:
                adaptor = await self.convert_mcp_to_langchain_tools(
                    server_name, tool, params
                )
                all_tools.append(adaptor)
            return all_tools

    @staticmethod
    async def convert_mcp_to_langchain_tools(
        server_name: str, tool: Tool, params: StdioServerParameters
    ) -> BaseTool:
        """Convert an MCP tool to a LangChain tool.

        Args:
            server_name (str): The name of the mcp server.
            tool (Tool): The MCP tool to convert to LangChain Tool.
            params (StdioServerParameters): The server parameters.
        """
        logger = getLogger(f"mcp_services.{server_name}.{tool.name}")

        class McpLangchainAdaptor(BaseTool):
            """Adaptor class to convert MCP tool to LangChain tool."""

            name: str = tool.name
            description: str = tool.description
            args_schema: type[BaseModel] = jsonschema_to_pydantic(tool.inputSchema)

            @staticmethod
            @asynccontextmanager
            async def get_session(
                server_params: StdioServerParameters,
            ) -> ClientSession:
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
                    logger.info(f"Session created for {server_name}:{tool.name}")
                    yield session

            def _run(self, **kwargs: dict) -> Never:
                raise NotImplementedError("Only async operation is supported")

            async def _arun(self, **kwargs: dict) -> list:
                async with self.get_session(params) as session:
                    logger.info(
                        f"Calling tool {server_name}:{tool.name} "
                        f"with arguments {kwargs}"
                    )
                    results = await session.call_tool(self.name, kwargs)
                    return results

        return McpLangchainAdaptor()

    async def fetch_all_server_tools(self) -> list[BaseTool]:
        """List the available tools for all servers.

        Returns:
            list[BaseTool]: The available tools for all servers as LangChain tools.
        """
        coroutines = [
            self._fetch_langchain_tools(server_name, params)
            for server_name, params in self.server_configs.mcpServers.items()
        ]
        results = await gather(*coroutines)
        return [item for sublist in results for item in sublist]

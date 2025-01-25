import logging

from langchain_core.tools import tool
from mcp.types import AnyUrl
from pydantic import BaseModel, Field

from langchain_mcp_connect.get_servers import LangChainMcp

log = logging.getLogger("mcp_call_tool")


class CallInput(BaseModel):
    """Data model for call tool input."""

    server_name: str = Field(
        ...,
        description="The name of the server.",
        examples=["vector_store"],
    )
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


class ReadResourceInput(BaseModel):
    """Data model for list resource input."""

    server_name: str = Field(
        ...,
        description="The name of the server.",
        examples=["vector_store"],
    )
    name: str = Field(
        ...,
        description="The name of the tool to call from the server.",
        examples=["retrieve-documents"],
    )
    uri: str = Field(
        ...,
        description="The URI to list resources from.",
        examples=["postgres://public/schemas"],
    )


def load_mcp_params() -> LangChainMcp:
    """Load the server parameters."""
    return LangChainMcp()


@tool("call-tool", args_schema=CallInput)
async def call_tool(server_name: str, name: str, arguments: dict) -> list:
    """Call a tool with the given name and arguments.

    Args:
        server_name: The name of the server.
        name: The name of the tool to call.
        arguments: The arguments to pass to the tool.

    Example:
        call_tool(
            "vector-store-server",
            "retrieve-documents",
            {"query": "lloyd hamilton data engineer", "k": 1, "threshold": 0.5}
        )

    Returns:
        list: The list of results from the tool.
    """
    log.info(
        f"Calling tool {name} with arguments {arguments} from server {server_name}"
    )
    mcp = load_mcp_params()
    params = mcp.server_configs.mcpServers.get(server_name)
    async with mcp.get_session(params) as session:
        return await session.call_tool(name, arguments)


@tool("read-resources-tool", args_schema=ReadResourceInput)
async def read_resources_tool(server_name: str, name: str, uri: str) -> list:
    """List the resources available on a server.

    Args:
        server_name: The name of the server.
        name: The name of the tool to call.
        uri: The URI to list resources from.

    Example:
        read_resources_tool(
            server_name="postgres",
            name="table_names",
            uri="postgres://public/schemas"
        )
    """
    log.info(f"Reading resource {name} from server {server_name} at {uri}")
    mcp = load_mcp_params()
    params = mcp.server_configs.mcpServers.get(server_name)
    async with mcp.get_session(params) as session:
        return await session.read_resource(AnyUrl(uri))

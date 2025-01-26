import os

import pytest
from langchain_core.tools import BaseTool as LangChainBaseTool
from mcp.types import Tool as McpTool
from pydantic import BaseModel

from langchain_mcp_connect import LangChainMcp


@pytest.fixture
def mock_mcp_tool() -> McpTool:
    """Return a mock McpTool object."""
    return McpTool(
        name="get_file_contents",
        description="Retrieve the file contents of a file from a github repository",
        inputSchema={
            "type": "object",
            "properties": {
                "owner": {
                    "type": "string",
                    "description": "Repository owner (username or organization)",
                },
                "repo": {"type": "string", "description": "Repository name"},
                "path": {
                    "type": "string",
                    "description": "Path to the file or directory",
                },
                "branch": {
                    "type": "string",
                    "description": "Branch to get contents from",
                },
            },
            "required": ["owner", "repo", "path"],
            "additionalProperties": False,
            "$schema": "http://json-schema.org/draft-07/schema#",
        },
    )


class TestLangChainMCP:
    """Test the LangChainMcp class."""

    def test_init(self) -> None:
        """Test the __init__ method.

        Assets that the config_path is set to "./claude_mcp_config.json" and
        the _server_configs is None.
        """
        lcp = LangChainMcp()
        assert lcp.config_path == "./claude_mcp_config.json"
        assert lcp._server_configs is None

    def test_server_configs(self) -> None:
        """Test the server_configs property.

        Assets that the server_configs property returns the _load_config method.
        """
        os.environ["GITHUB_PERSONAL_ACCESS_TOKEN"] = "test"
        os.environ["OPENAI_API_KEY"] = "test"

        lcp = LangChainMcp()

        assert [key for key in lcp.server_configs.mcpServers] == [
            "git",
            "filesystem",
            "github",
        ]
        assert lcp.server_configs == lcp._load_config()

    @pytest.mark.asyncio
    async def test_convert_mcp_to_langchain_tools(self, mock_mcp_tool: McpTool) -> None:
        """Test the convert_mcp_to_langchain_tools method.

        Assets that the _convert_mcp_to_langchain_tools method returns a list of
        BaseTool objects.
        """
        lcp = LangChainMcp()
        param = lcp.server_configs.mcpServers["github"]
        langchain_tool = await lcp.convert_mcp_to_langchain_tools(
            "github", mock_mcp_tool, param
        )

        assert isinstance(langchain_tool, LangChainBaseTool)
        assert langchain_tool.name == "get_file_contents"
        assert langchain_tool.description == (
            "Retrieve the file contents of a file " "from a github repository"
        )
        assert issubclass(langchain_tool.args_schema, BaseModel)

    @pytest.mark.asyncio
    async def test_mcp_langchain_adaptor_methods(self, mock_mcp_tool: McpTool) -> None:
        """Test that the correct methods exists for McpLangChainAdaptor.

        Asserts that only async operations are valid
        """
        lcp = LangChainMcp()

        param = lcp.server_configs.mcpServers["github"]
        langchain_tool = await lcp.convert_mcp_to_langchain_tools(
            "github", mock_mcp_tool, param
        )

        assert hasattr(langchain_tool, "get_session")
        assert hasattr(langchain_tool, "_arun")
        assert hasattr(langchain_tool, "_run")

        with pytest.raises(NotImplementedError):
            langchain_tool._run()

import os

import pytest

from langchain_mcp_connect.data_models import McpServers, StdioServerParameters
from langchain_mcp_connect.data_models.mcp_servers import SseServerParameters


class TestStdioServerParameters:
    """Test the StdioServerParameters model."""

    def test_environment_variables(self) -> None:
        """Test that the model sources environment variables with ENV_ prefix.

        Asserts that the environment variable is correctly sourced when ENV_ prefix
        is used.
        """
        os.environ["TEST_ENV_VAR"] = "wubba.lubba.dub.dub"
        stdio_server_parameters = StdioServerParameters(
            command="uvx", args=["./"], env={"TEST_ENV_VAR": "ENV_TEST_ENV_VAR"}
        )
        assert isinstance(stdio_server_parameters, StdioServerParameters)
        assert stdio_server_parameters.command == "uvx"
        assert stdio_server_parameters.args == ["./"]
        assert stdio_server_parameters.env["TEST_ENV_VAR"] == "wubba.lubba.dub.dub"

    def test_environment_variables_raise(self) -> None:
        """Test that the model sources environment variables with ENV_ prefix.

        Asserts that the environment variable is correctly sourced when ENV_ prefix
        is used.
        """
        with pytest.raises(ValueError):
            StdioServerParameters(
                command="uvx", args=["./"], env={"ANOTHER_VAR": "ENV_ANOTHER_VAR"}
            )

    def test_server_mapping(self) -> None:
        """Test that the model correctly maps the server configuration."""
        servers = {
            "mcpServers": {
                "stdioserver": {"command": "uvx", "args": ["./"]},
                "sseserver": {"url": "http://localhost:8080/sse"},
            }
        }

        mcpServers = McpServers(**servers)
        assert mcpServers.mcpServers["stdioserver"] == StdioServerParameters(
            command="uvx", args=["./"]
        )
        assert mcpServers.mcpServers["sseserver"] == SseServerParameters(
            url="http://localhost:8080/sse"
        )

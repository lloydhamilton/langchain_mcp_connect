import os

from langchain_mcp_connect.data_models import StdioServerParameters


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

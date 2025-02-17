import os
import sys
from typing import Any

from mcp import StdioServerParameters
from pydantic import BaseModel, Field, field_validator

# Environment variables to inherit by default
DEFAULT_INHERITED_ENV_VARS = (
    [
        "APPDATA",
        "HOMEDRIVE",
        "HOMEPATH",
        "LOCALAPPDATA",
        "PATH",
        "PROCESSOR_ARCHITECTURE",
        "SYSTEMDRIVE",
        "SYSTEMROOT",
        "TEMP",
        "USERNAME",
        "USERPROFILE",
    ]
    if sys.platform == "win32"
    else ["HOME", "LOGNAME", "PATH", "SHELL", "TERM", "USER"]
)


def get_default_environment() -> dict[str, str]:
    """Returns a default environment.

    Inherited object are environment variables deemed safe to inherit.
    """
    env: dict[str, str] = {}

    for key in DEFAULT_INHERITED_ENV_VARS:
        value = os.environ.get(key)
        if value is None:
            continue

        if value.startswith("()"):
            # Skip functions, which are a security risk
            continue

        env[key] = value

    return env


class SseServerParameters(BaseModel):
    """Data model for the sse server parameters."""

    url: str = Field(
        ...,
        description="The url of the sse server.",
    )
    headers: dict[str, Any] | None = Field(
        None, description="The headers of the sse server."
    )
    timeout: float = Field(5, description="The timeout of the sse server.")
    sse_read_timeout: float = Field(
        60 * 5,
        description="how long (in seconds) the client will wait for "
        "a new event before disconnecting.",
    )


class StdioServerParameters(StdioServerParameters):
    """Data model for the stdio server parameters."""

    @field_validator("env", mode="before")
    @classmethod
    def parse_env(cls, env: dict) -> dict[str, str] | None:
        """Parse the environment variables.

        For each environment variable that starts with "ENV_", replace the value with
        the value of the corresponding environment variable.

        Args:
            env: The environment variables.
        """
        default_env = get_default_environment()
        for key in env:
            if env[key].startswith("ENV_"):
                env_var = os.environ.get(env[key][4:])
                if env_var is None:
                    raise ValueError(f"Environment variable {env[key][4:]} not found.")
                env[key] = env_var
        return default_env | env


class McpServers(BaseModel):
    """Data model for mcp servers."""

    mcpServers: dict[str, StdioServerParameters | SseServerParameters] = Field(
        ...,
        description="The list of mcp servers configurations.",
    )

    @field_validator("mcpServers", mode="before")
    @classmethod
    def parse_configs(
        cls, mcpServers: dict
    ) -> dict[any, StdioServerParameters | SseServerParameters]:
        """Parse the mcp servers configurations.

        Args:
            mcpServers: The mcp servers configurations.

        Returns:
            list[StdioServerParameters | SseServerParameters]: The list of mcp servers
                configurations.
        """
        return {server: cls.__mapParamters(mcpServers[server]) for server in mcpServers}

    @staticmethod
    def __mapParamters(server: dict) -> StdioServerParameters | SseServerParameters:
        """Map the parameters to the correct type."""
        if "url" in server:
            return SseServerParameters(**server)
        else:
            return StdioServerParameters(**server)

import os
import sys

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
                env[key] = os.environ.get(env[key][4:])
        return default_env | env


class McpServers(BaseModel):
    """Data model for mcp servers."""

    mcpServers: dict[str, StdioServerParameters] = Field(
        ...,
        description="The list of mcp servers configurations.",
    )

    @field_validator("mcpServers", mode="before")
    @classmethod
    def parse_configs(cls, mcpServers: dict) -> dict[any, StdioServerParameters]:
        """Parse the mcp servers configurations.

        Args:
            mcpServers: The mcp servers configurations.

        Returns:
            list[StdioServerParameters]: The list of mcp servers configurations.
        """
        return {
            server: StdioServerParameters(**mcpServers[server]) for server in mcpServers
        }

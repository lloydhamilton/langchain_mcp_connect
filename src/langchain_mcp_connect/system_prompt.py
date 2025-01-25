import json

from langchain_core.messages import SystemMessage
from pydantic import BaseModel, field_validator

initial_prompt = """
# Context #
You are a helpful AI assistant that can call different tools to help you with yours
task.

# TOOLS #

Use default values when available.
These are the available tool you have access to:

{tools}

When calling the call-tool, you need to use the following syntax:
```
call-tool(
    server_name="vector_store",
    name="retrieve-document",
    arguments={{
        "query": "This is a sample query",
        "k": 5,
        "threshold": 0.5
    }}
)
```
Where server_name is the name of the server you want to call the tool from.
Where name is the name of the tool you want to call and arguments is the argument you
want to pass to the tool.

# RESOURCES #

These are the resources you have access to:

{resources}

When you need access to the resources, you can calling the read-resource-tool.
You will need to use the following syntax:
```
read-resource-tool(
    server_name="vector_store",
    name="list-resources",
    uri="postgres://public/schemas"
)
```
Where server_name is the name of the server you want to call the resource from.
Where name is the name of the resource you want to call.
Uri is the URI you want to fetch the resource from.
"""


class MspToolPrompt(BaseModel):
    """Data model for the MSP tool prompt."""

    tools: str
    resources: str

    @field_validator("tools", "resources", mode="before")
    @classmethod
    def parse_dict(cls, val: dict) -> str:
        """Parse the tools."""
        return json.dumps(val)

    def get_prompt(
        self,
    ) -> SystemMessage:
        """Format the prompt to return a system message."""
        system_prompt = initial_prompt.format(
            tools=self.tools, resources=self.resources
        )
        return SystemMessage(content=system_prompt)

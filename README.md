# Langchain Model Context Protocol Connector

## Introduction
The Model Context Protocol (MCP) is an open-source standard released by Anthropic. 
The Model Context Protocol highlights the importance of tooling standardisation through open protocols. 
Specifically, it standardises how applications interact and provide context to LLMs. 
Just like how HTTP standardises how we communicate across the internet, MCP provides a standard protocol for LLM to interact with external tools. 
You can find out more about the MCP at https://github.com/modelcontextprotocol and https://modelcontextprotocol.io/introduction

This project introduces tools to easily integrate MCP with langchain.

## Example usage

The langchain_mcp_connect contain key methods to determine available tools and resources
in the model context protocol. The schemas of input arguments for tools and resources 
are injected into the system prompt and form part of the initial prompt. Before starting,
please ensure you meet the pre-requisites.

### Pre requisites

1. Install the python environment with [uv](https://astral.sh/blog/uv)
```bash
uv add langchain_mcp_connect
```

2. Define your tool within `claude_mcp_config.json` file in the root directory. For a list 
of available tools see [here](https://github.com/modelcontextprotocol/servers/tree/main).
```json
{
  "mcpServers": {
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git", "--repository", "./"]
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "./"
      ]
    },
    "github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ENV_GITHUB_PERSONAL_ACCESS_TOKEN"
      }
    }
  }
}
```

3. Define environment variables. `langchain_mcp_connect` is able to inject secrets from
the current environment. To do so, prefix the name of your environment variable with 
`ENV_` in `claude_mcp_config.json` to inject envrionment variables into the current
context. In the example above, ensure you have defined `GITHUB_PERSONAL_ACCESS_TOKEN`
in your current environment with:

```bash
export GITHUB_PERSONAL_ACCESS_TOKEN="<YOUR_TOKEN_HERE>"
```

### Usage

```python
import argparse
import asyncio
import logging

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_mcp_connect import MspToolPrompt, call_tool
from langchain_mcp_connect.get_servers import LangChainMcp
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

load_dotenv()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("LangChainMcp")


def list_tools() -> dict:
    """List all available tools.

    Calls all list tools method for all configured MCP servers.
    """
    mcp = LangChainMcp()
    return asyncio.run(mcp.fetch_all_server_tools())


def list_resources() -> dict:
    """List all available resources.

    Calls all list resources method for all configured MCP servers.
    """
    mcp = LangChainMcp()
    return asyncio.run(mcp.list_all_server_resources())


async def invoke_agent(
    model: ChatOpenAI, query: str, tools: dict, resources: dict
) -> dict:
    """Invoke the agent with the given query."""
    agent_executor = create_react_agent(model, [call_tool])

    # Create a system prompt and a human message
    system_prompt = MspToolPrompt(tools=tools, resources=resources).get_prompt()
    human_message = HumanMessage(content=query)

    # Invoke the agent
    r = await agent_executor.ainvoke(
        input=dict(messages=[system_prompt, human_message])
    )

    return r


if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Langchain Model Context Protocol demo"
    )
    parser.add_argument("-q", "--query", type=str, help="Query to be executed")
    args = parser.parse_args()

    # Define the llm
    llm = ChatOpenAI(
        model="gpt-4o",
        model_kwargs={
            "max_tokens": 4096,
            "temperature": 0.0,
        },
    )

    # Invoke the agent
    response = asyncio.run(
        invoke_agent(llm, args.query, list_tools(), list_resources())
    )

    log.info(response)
```


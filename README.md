
<h1 align="center">
  Langchain Model Context Protocol Connector
</h1>

[![build status](https://github.com/lloydhamilton/langchain_mcp_connect/actions/workflows/continuous-deployment.yaml/badge.svg)](https://github.com/lloydhamilton/langchain_mcp_connect/actions/workflows/continuous-deployment.yaml)
![GitHub Release](https://img.shields.io/github/v/release/lloydhamilton/langchain_mcp_connect)

## Introduction
This project introduces tools to easily integrate Anthropic Model Context Protocol(MCP) with langchain. 
It provides a simple way to connect to MCP servers and access tools that can be made available to LangChain.
Most importantly, `langchain-mcp-connect` allows developers to easily integrate their LLMs with a rich ecosystem 
of [pre-built](https://github.com/modelcontextprotocol/servers/tree/main) MCP servers.

MCP integrations with langchain expands the capabilities of LLM by providing access to community servers 
and additional resources. This means that we do not need to create custom
tools for each LLM, but rather use the same tools across different LLMs.

## Installation
```bash
pip install langchain-mcp-connect
```

## What is the Model Context Protocol (MCP)?
The Model Context Protocol (MCP) is an open-source standard released by Anthropic. 
The Model Context Protocol highlights the importance of tooling standardisation through open protocols. 
Specifically, it standardises how applications interact and provide context to LLMs. 
Just like how HTTP standardises how we communicate across the internet, MCP provides a standard protocol for LLM to interact with external tools.
You can find out more about the MCP at https://github.com/modelcontextprotocol and https://modelcontextprotocol.io/introduction.

## Example usage
The `langchain_mcp_connect` contain key methods to connect MCP server tools to LangChain. Before starting,
please ensure you meet the pre-requisites.
For a detailed example on how `langchain_mcp_connect` can be used, see this [demo](https://github.com/lloydhamilton/agentic_ai_mcp_demo) project.

### Defining a tool
Define your tool within `claude_mcp_config.json` file in the root directory. For a list 
of available tools and how to configure tools see [here](https://github.com/modelcontextprotocol/servers/tree/main). 
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
      },
      "sseService": {
        "url": "http://localhost:8000/sse"
      }
    }
  }
}
```

### Environment Variables
Managing secrets is a key aspect of any project. The `langchain_mcp_connect` tool is 
able to inject secrets from the current environment. 
To do so, prefix the name of your environment variable with 
`ENV_` in `claude_mcp_config.json` to inject environment variables into the current
context. In the example above, ensure you have defined `GITHUB_PERSONAL_ACCESS_TOKEN`
in your current environment with:

```bash
export GITHUB_PERSONAL_ACCESS_TOKEN="<YOUR_TOKEN_HERE>"
export OPENAI_API_KEY="<YOUR_KEY_HERE>"
```

### Running the example
You can find an example usage in the `src/example/agent.py` file. You will need to 
install [uv](https://astral.sh/blog/uv).

```bash
uv run src/example/agent.py
```

### Example code
```python
import asyncio
import logging
import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from langchain_mcp_connect import LangChainMcp

load_dotenv()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("LangChainMcp")

if "GITHUB_PERSONAL_ACCESS_TOKEN" not in os.environ:
    raise ValueError(
        "Please set the GITHUB_PERSONAL_ACCESS_TOKEN environment variable."
    )
if "OPENAI_API_KEY" not in os.environ:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")


if __name__ == "__main__":

    QUERY = "What tools do you have access to?"

    # Define the llm
    llm = ChatOpenAI(
        model="gpt-4o",
        model_kwargs={
            "max_tokens": 4096,
            "temperature": 0.0,
        },
    )

    # Fetch tools
    mcp = LangChainMcp()
    tools = mcp.list_mcp_tools()

    # Bind tools to the agent
    agent_executor = create_react_agent(llm, tools)
    human_message = dict(messages=[HumanMessage(content=QUERY)])
    
    # Run the agent asynchronously
    response = asyncio.run(
        agent_executor.ainvoke(input=human_message)
    )

    log.info(response)
```

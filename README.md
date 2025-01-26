
<h1 align="center">
  Langchain Model Context Protocol Connector
</h1>

## Introduction
This project introduces tools to easily integrate Anthropic Model Context Protocol(MCP) with langchain. 
It provides a simple way to connect to MCP servers and access tools that can be made available to LangChain.

MCP integrations with langchain expands the capabilities of LLM by providing access to an ecosystem 
of community build servers and additional resources. This means that we do not need to create custom
tools for each LLM, but rather use the same tools across different LLMs.

## What is the Model Context Protocol (MCP)?
The Model Context Protocol (MCP) is an open-source standard released by Anthropic. 
The Model Context Protocol highlights the importance of tooling standardisation through open protocols. 
Specifically, it standardises how applications interact and provide context to LLMs. 
Just like how HTTP standardises how we communicate across the internet, MCP provides a standard protocol for LLM to interact with external tools.
You can find out more about the MCP at https://github.com/modelcontextprotocol and https://modelcontextprotocol.io/introduction.

## Example usage

The langchain_mcp_connect contain key methods to determine available tools and resources
in the model context protocol. The schemas of input arguments for tools and resources 
are injected into the system prompt and form part of the initial prompt. Before starting,
please ensure you meet the pre-requisites.

For a detail example on how `langchain_mcp_connect` can be used, see this [demo](https://github.com/lloydhamilton/agentic_ai_mcp_demo) project.

### Pre requisites

1. Install [uv](https://astral.sh/blog/uv)

### Defining a tool

Define your tool within `claude_mcp_config.json` file in the root directory. For a list 
of available tools and how to confiure tools see [here](https://github.com/modelcontextprotocol/servers/tree/main). 
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

### Environment Variables

Managing secrets is a key aspect of any project. The `langchain_mcp_connect` tool is 
able to inject secrets from the current environment. 
To do so, prefix the name of your environment variable with 
`ENV_` in `claude_mcp_config.json` to inject envrionment variables into the current
context. In the example above, ensure you have defined `GITHUB_PERSONAL_ACCESS_TOKEN`
in your current environment with:

```bash
export GITHUB_PERSONAL_ACCESS_TOKEN="<YOUR_TOKEN_HERE>"
export OPENAI_API_KEY="<YOUR_KEY_HERE>"
```

### Running the example

```bash
uv run src/example/agent.py
```
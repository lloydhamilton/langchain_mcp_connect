# /// script
# dependencies = [
#   "langchain>=0.3.9",
#   "langgraph>=0.2.53",
#   "langchain-openai>=0.2.10",
#   "langchain-community>=0.3.9",
#   "langchain-mcp-connect>=2.0.0",
# ]
# ///

import argparse
import asyncio
import logging
import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.tools import BaseTool
from langchain_mcp_connect import LangChainMcp
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

load_dotenv()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("LangChainMcp")

if "GITHUB_PERSONAL_ACCESS_TOKEN" not in os.environ:
    raise ValueError(
        "Please set the GITHUB_PERSONAL_ACCESS_TOKEN environment variable."
    )
if "OPENAI_API_KEY" not in os.environ:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")


async def invoke_agent(
    model: ChatOpenAI,
    query: str,
    langchain_tools: list[BaseTool],
) -> dict:
    """Invoke the agent with the given query."""
    agent_executor = create_react_agent(model, langchain_tools)

    # Create a system prompt and a human message
    human_message = HumanMessage(content=query)

    # Invoke the agent
    r = await agent_executor.ainvoke(input=dict(messages=[human_message]))

    return r


if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Langchain Model Context Protocol demo"
    )
    parser.add_argument(
        "-q",
        "--query",
        type=str,
        help="Query to be executed",
        default="What tools do you have access to?",
    )
    args = parser.parse_args()

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

    # Invoke the agent
    response = asyncio.run(
        invoke_agent(model=llm, query=args.query, langchain_tools=tools)
    )

    log.info(response)

# /// script
# dependencies = [
#   "langchain>=0.3.9",
#   "langgraph>=0.2.53",
#   "langchain-openai>=0.2.10",
#   "langchain-community>=0.3.9",
#   "langchain-mcp-connect>=2.0.0",
# ]
# ///

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
    response = agent_executor.invoke(input=human_message)

    log.info(response)

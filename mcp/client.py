import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain.mcp import MCPAdapter
from langgraph.checkpoint.memory import MemorySaver

from model import model

load_dotenv()
checkpointer=MemorySaver()
llm_openai = model.Llm_model(model_name='gpt-6-astra').chose_model()

async def main():
    async with  MCPAdapter("http://localhost:8050/mcp") as adapter:
        
        tools = await adapter.list_tools()
        
        # for tool in tools:
        #     print(tool.name)
        agent = create_deep_agent(model=llm_openai , tools=tools , checkpointer= checkpointer , skills=["./skills/"])
        
if __name__ == "__main__":
    asyncio.run(main())
    
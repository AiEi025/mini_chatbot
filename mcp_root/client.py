import asyncio
import sys
from pathlib import Path

skills_dir = Path(__file__).parent.parent / "skills"
workspace_dir = Path(__file__).parent.parent / "workspace"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from deepagents.middleware.skills import SkillsMiddleware
from deepagents.middleware.subagents import SubAgent
from dotenv import load_dotenv
from langchain.mcp import MCPAdapter
from langgraph.checkpoint.memory import MemorySaver

from model import model

load_dotenv()
_checkpointer=MemorySaver()
_llm_openai = model.Llm_model(model_name='deepseek-v4-flash').chose_model()

python_fixer_subagent = SubAgent(
    name="python-fixer-agent",
    description="Fix Python files. Use when user uploads .py file.",
    system_prompt="You are a Python code fixer...",
    skills=[f"{skills_dir}/python-fixer/"],  # همین Skill شما
    # interrupt_on={
    #     # ابزارهای نوشتن این Subagent نیاز به تأیید دارند
    #     "write_file": {"allowed_decisions": ["approve", "edit", "reject"]},
    #     "edit_file": {"allowed_decisions": ["approve", "edit", "reject"]},
    #     "read_file": False,
    # },
)

daily_planner_subagent = {
    "name": "daily-planner",
    "description": "Plan and organize the user's day. Use when the user asks for daily planning, task prioritization, or time blocking.",
    "system_prompt": """You are a daily planning assistant. Your job is to help the user organize their day effectively.

When the user asks for help planning their day:
1. Gather context: Ask for tasks, appointments, and priorities.
2. Identify priorities: Distinguish urgent vs. important.
3. Estimate time: Ask for realistic durations.
4. Use write_todos: Create a structured TODO list with content, activeForm, and status.
5. Order logically: Sequence tasks by energy levels and fixed times.
6. Update progress: Mark tasks completed and move the next to in_progress.

## Guidelines
- Confirm available working hours before planning.
- Ask specific questions if the user is vague.
- Suggest breaks and buffer time between high-focus tasks.""",
    "skills": [f"{skills_dir}/daily-planner/"], 
}

base_dir=str(Path(__file__).parent.parent) 
skills_backend = FilesystemBackend(
    root_dir=str(base_dir),  # mini_chatbot
    virtual_mode=True
)
skills_middleware = SkillsMiddleware(
    backend=skills_backend,
    sources=["skills"],  # نسبی به root = mini_chatbot
)
async def main():
    async with  MCPAdapter("http://localhost:8050/mcp") as adapter:
        
        tools = await adapter.list_tools()
        
        # for tool in tools:
        #     print(tool.name)
        agent = create_deep_agent(model=_llm_openai ,
                                  tools=tools ,
                                  skills=[str(skills_dir)],
                                  checkpointer= _checkpointer,
                                  backend=FilesystemBackend(root_dir=f'{workspace_dir}/python',virtual_mode=True),
                                  subagents=[python_fixer_subagent,daily_planner_subagent],
                                  middleware=[skills_middleware]
                                  
                                  )
        async for chunk in agent.astream(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": """please fix the but in this file main.py"""
                    }
                ]
            },
            config={
                "configurable": {
                    "thread_id": "user_1"
                }
            }
        ):
            print(chunk)

asyncio.run(main())
                   
        
    
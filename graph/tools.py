# python package tools
from pathlib import Path
from typing import Literal

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from deepagents.middleware.skills import SkillsMiddleware
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

# read_only_rules = [
#     FilesystemPermission(
#         operations=["write"],          # عملیات نوشتن
#         paths=["/**"],                 # در تمام مسیرها
#         mode="deny",                   # را ممنوع کن
#     )]

class CustomAgent:
    def __init__(
        self,
        model,
        agent_type: Literal["l_agent", "d_agent"],
        skill_path: str | Path | None = None,
        workspace_path: str | Path | None = None,
        tools=None,
        sysprompt=None,
        checkpointer=None,
    ):
        self.agent_type = agent_type
        self.skill_path = Path(skill_path) if skill_path else None
        self.workspace_path = Path(workspace_path) if workspace_path else None
        self.model = model
        self.checkpointer = checkpointer or MemorySaver()
        self.tools = tools or []
        self.sysprompt = sysprompt

        middlewares = []
        if self.skill_path:
            backend = FilesystemBackend(root_dir=self.skill_path ,virtual_mode=True)
            middlewares.append(
                SkillsMiddleware(
                    backend=backend,
                    sources=["skills/"]
                )
)

        if self.workspace_path:
            self.workspace_path.mkdir(parents=True, exist_ok=True)
            backend = FilesystemBackend(root_dir=str(self.workspace_path))
        else:
            backend = None

        # انتخاب نوع agent
        if self.agent_type == "d_agent":
            self.agent = create_deep_agent(
                model=self.model,
                tools=self.tools,
                system_prompt=self.sysprompt,
                backend=backend,       
                middleware=middlewares,
                checkpointer=self.checkpointer,
            )
        elif self.agent_type == "l_agent":
            self.agent = create_agent(
                model=self.model,
                tools=self.tools,
                system_prompt=self.sysprompt,
                middleware=middlewares,
                checkpointer=self.checkpointer,
            )
        else:
            raise ValueError(f"Unknown agent_type: {self.agent_type}")
        
def extract_tool_calls(messages):

    tool_calls = []

    for message in messages:

        calls = getattr(message, "tool_calls", None)

        if calls:
            tool_calls.extend(calls)

    return tool_calls
# python package tools
from pathlib import Path
from typing import Literal

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from deepagents.middleware.skills import SkillsMiddleware
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver


class CustomAgent:
    def __init__(self ,model, agent_type:Literal['l_agent','d_agent'] ,skill_path:str|Path|None , workspace_path:str|Path|None , tools = None , sysprompt=None):
        self.agent_type = agent_type
        self.skill_path = skill_path
        self.workspace_path = workspace_path
        self.model = model
        self.checkpointer = MemorySaver()
        self.tools = tools
        self.sysprompt =sysprompt
        base_dir=str(Path(__file__).parent.parent) 
        skills_backend = FilesystemBackend(
    root_dir=str(base_dir),  # mini_chatbot
    virtual_mode=True
)
        self.skills_middleware = SkillsMiddleware(
    backend=skills_backend,
    sources=["skills"],  # نسبی به root = mini_chatbot
)
    def build(self):
        if self.agent_type == 'd_agent':
            return create_deep_agent(model= self.model,
                                     backend= FilesystemBackend(
                                         root_dir=str(self.workspace_path),
                                         virtual_mode= True
                                     ),
                                     middleware=[self.skills_middleware],
                                     skills=[str(self.skill_path)],
                                     checkpointer=self.checkpointer,
                                     tools=self.tools)
        elif self.agent_type == 'l_agent':
            return create_agent(model=self.model,
                                tools=self.tools,
                                system_prompt= self.sysprompt
                                )
        else:
            raise ValueError('you must choose valid agent type')
        
        
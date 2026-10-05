import json
import sys
from pathlib import Path
from typing import Annotated, Literal, TypedDict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel


class Graph_state(BaseModel):
    messages: Annotated[list[BaseMessage] , add_messages]
    question:str = ""
    status:Literal['python','planning','tools']='tools'
    attempts: int = 3
    validation:bool = True
    validation_feedback:str = "" 
    file_path: str | None = None
    
class Router_state(TypedDict):
    state:Literal['python','planning','tools']=None
class Planning_state(TypedDict):
    status:Literal['ok','no']='ok'
    feedback:str = ""
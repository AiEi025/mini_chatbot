import sys
from pathlib import Path
from typing import Annotated, Literal, TypedDict

from pydantic import Field

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel

from counting.counting import RetryContext


class Router_state(TypedDict):
    state:Literal['python','planning','tools','general']
class Planning_state(TypedDict):
    status: bool
    feedback:str 
class ToolValidationState(BaseModel):
    status: bool
    feedback: str


class Graph_state(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages]

    question: str = ""

    status: Literal[
        "python",
        "planning",
        "tools",
        'general'
    ] = 'general'

    validation: bool = True
    validation_feedback: str = ""

    retry: RetryContext = Field(
        default_factory=RetryContext
    )

    file_path: str | None = None
    thread_id:str | None = None 
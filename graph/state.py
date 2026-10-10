import sys
from pathlib import Path
from typing import Annotated, Literal, TypedDict

from pydantic import Field

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel


class Router_state(TypedDict):
    state:Literal['python','planning','tools','general']
class Planning_state(TypedDict):
    status: bool
    feedback:str 
class ToolValidationState(BaseModel):
    status: bool
    feedback: str
class RetryContext(BaseModel):
    attempts_used: int = 0
    max_attempts: int = 3

    @property
    def can_retry(self) -> bool:
        return self.attempts_used < self.max_attempts
    @property
    def exhausted(self) -> bool:
        return self.attempts_used >= self.max_attempts

    def record_attempt(self) -> "RetryContext":
        return self.model_copy(
            update={
                "attempts_used": self.attempts_used + 1
            }
        )

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
# python package tools
from pathlib import Path
from typing import Annotated, Literal

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from deepagents.middleware.skills import SkillsMiddleware
from langchain.agents import create_agent
from langchain.tools import InjectedToolArg, tool
from langchain_core.tools import StructuredTool
from langgraph.checkpoint.memory import MemorySaver

from tools.rag import RAG

rag =RAG()

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

@tool
def files_rag(
    query: str,
    thread_id: Annotated[str, InjectedToolArg],   # ← agent نمی‌بیندش
) -> str:
    """Search the content of the file currently uploaded and indexed
    by the user for THIS chat.

    Use this tool when:
    - The user asks about information contained in their uploaded file.
    - The user asks to summarize, explain, compare, or extract
      information from the uploaded document.
    - The answer should be grounded in the uploaded document.
    - The user refers to "my file", "the document", "the PDF",
      "the uploaded text", or similar.

    Do NOT use this tool for:
    - General knowledge questions.
    - Current or up-to-date information.
    - Web research.
    - Questions unrelated to the uploaded file.
    - Math, code writing, or tasks that don't require document content.

    For current or external information, use web search instead.

    Args:
        query: A focused question or search query about the uploaded file.
            Keep it short and specific. Example: "return policy for
            damaged items" instead of "tell me everything about returns".

    Returns:
        The most relevant passages retrieved from the uploaded file,
        separated by "---". If no relevant content is found, returns
        an empty string.
    """
    return rag.find_retrieve(query=query, thread_id=thread_id)

def make_rag_tool(thread_id: str) -> StructuredTool:
    """Build a RAG tool bound to a specific chat thread."""

    def _rag(query: str) -> str:
        """Search the content of the file currently uploaded and indexed
        by the user for THIS chat.

        Use this tool when:
        - The user asks about information contained in their uploaded file.
        - The user asks to summarize, explain, compare, or extract
          information from the uploaded document.
        - The answer should be grounded in the uploaded document.
        - The user refers to "my file", "the document", "the PDF",
          "the uploaded text", or similar.

        Do NOT use this tool for:
        - General knowledge questions.
        - Current or up-to-date information.
        - Web research.
        - Questions unrelated to the uploaded file.
        - Math, code writing, or tasks that don't require document content.

        For current or external information, use web search instead.

        Args:
            query: A focused question or search query about the uploaded file.

        Returns:
            The most relevant passages retrieved from the uploaded file.
        """
        return rag.find_retrieve(query=query, thread_id=thread_id)

    return StructuredTool.from_function(
        func=_rag,
        name="files_rag",
        description=_rag.__doc__,
    )
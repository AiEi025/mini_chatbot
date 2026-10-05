import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server import create_proxy

from tools.python_validator import PythonValidator
from tools.rag import RAG

BASE_DIR = Path(__file__).resolve().parent.parent

WORKSPACE = BASE_DIR / "workspace" / "python"

rag =RAG()
validator = PythonValidator(
    workspace_dir=WORKSPACE
)
load_dotenv()


mcp = FastMCP()

@mcp.tool
async def files_rag(query: str) -> str:
    """
    Search the content of the file currently uploaded and indexed
    by the user.

    Use this tool when:
    - The user asks about information contained in their uploaded file.
    - The user asks to summarize, explain, compare, or extract information
      from the uploaded document.
    - The answer should be grounded in the uploaded document.

    Do NOT use this tool for:
    - General knowledge questions.
    - Current or up-to-date information.
    - Web research.
    - Questions unrelated to the uploaded file.

    For current or external information, use web search instead.

    Args:
        query: A focused question or search query about the uploaded file.

    Returns:
        The most relevant passages retrieved from the uploaded file.
    """
    top3 = rag.find_retrieve(query=query)
    return top3

# @mcp.tool
# def validate_python_file(file_path: str) -> dict:
#     """
#     Validate a Python file by executing it.

#     Use this after editing or fixing a Python file.

#     Args:
#         file_path:
#             Path of the Python file inside the Python workspace.

#     Returns:
#         Validation result including stdout, stderr and return code.
#     """

#     return validator.validate(file_path)


mcp.mount(
    create_proxy(
        {
            "mcpServers": {
                "ddg-search": {
                                    "command": "uvx",
                                    "args": ["duckduckgo-mcp-server"]
                                },
            }
        }
    )
)

if __name__ == "__main__":
    mcp.run(transport="streamable-http",
        host="localhost",
        port=8050
        )


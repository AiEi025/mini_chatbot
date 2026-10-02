import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server import create_proxy

load_dotenv()

from tools.rag import find_retrieve, retriever

mcp = FastMCP()

@mcp.tool
def files_rag(query: str, name: str, content: str) -> str:
    """Perform RAG on an uploaded file.

    Args:
        query: User's question
        name: Original filename (e.g. 'doc.pdf')
        content: Base64-encoded file content
    """
    try:
        file_bytes = base64.b64decode(content)
    except Exception as e:
        return f"Error decoding file: {e}"

    try:
        retrievers = retriever(
            upload_file_name=name,
            upload_file_getvalue=file_bytes,
        )
        top3 = find_retrieve(best_retriever=retrievers, query=query)
        return top3
    except Exception as e:
        return f"Error in RAG: {e}"



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


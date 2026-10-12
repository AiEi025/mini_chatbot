import sys
from pathlib import Path
import os
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server import create_proxy

BASE_DIR = Path(__file__).resolve().parent.parent


load_dotenv()


mcp = FastMCP("NexusOrchestrator")

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


tavily_api_key = os.environ.get("TAVILY_API_KEY")

if not tavily_api_key:
    raise ValueError("TAVILY_API_KEY environment variable is not set.")

# ساخت URL مستقیم برای Tavily Remote MCP
tavily_url = f"https://mcp.tavily.com/mcp/?tavilyApiKey={tavily_api_key}"

# Mount کردن پروکسی Tavily
mcp.mount(
    create_proxy(tavily_url),
    namespace="tavily"
)






if __name__ == "__main__":
    mcp.run(transport="streamable-http",
        host="localhost",
        port=8050
        )


import sys
from pathlib import Path

from langchain_core.messages import HumanMessage

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent)
)
from graph.graph import graph
from graph.state import Graph_state


async def run_graph(user_input: str):
    initial_state = Graph_state(
        messages=[
            HumanMessage(content=user_input)
        ],
        question=user_input,
    )

    config = {
        "configurable": {
            "thread_id": "user_123"
        }
    }

    result = await graph.ainvoke(
        initial_state,
        config=config
    )

    return result
import sys
from pathlib import Path

from langchain_core.messages import HumanMessage

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent)
)
import asyncio
import threading

from graph.graph import graph
from graph.state import Graph_state


class AsyncRunner:
    def __init__(self):
        self.loop = asyncio.new_event_loop()

        self.thread = threading.Thread(
            target=self._run_loop,
            daemon=True,
        )
        self.thread.start()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def run(self, coro):
        future = asyncio.run_coroutine_threadsafe(
            coro,
            self.loop,
        )
        return future.result()

async def run_graph(user_input: str , thread_id:str):
    initial_state = Graph_state(
        messages=[
            HumanMessage(content=user_input)
        ],
        question=user_input,
    )

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = await graph.ainvoke(
        initial_state,
        config=config
    )

    return result
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
from counting.counting import RetryContext


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

async def run_graph(user_input: str, thread_id: str):
    initial_state = Graph_state(
        messages=[
            HumanMessage(content=user_input)
        ],
        question=user_input,
        thread_id=thread_id,
        retry=RetryContext()
    )

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    # بررسی وضعیت قبل از اجرای درخواست جدید
    # previous = await graph.aget_state(config)

    # print("\n--- PREVIOUS CHECKPOINT ---")
    print("Thread ID:", thread_id)
    # print("Previous messages:")

    # for message in previous.values.get("messages", []):
    #     print(message.type, repr(message.content))

    result = await graph.ainvoke(
        initial_state,
        config=config
    )

    print("\n--- RESULT AFTER INVOKE ---")
    print("Total messages:", len(result.get("messages", [])))

    for message in result.get("messages", []):
        print(message.type, repr(message.content))

    return result
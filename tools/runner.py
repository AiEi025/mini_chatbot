
import asyncio
import os
import selectors
import threading

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg import AsyncConnection
from psycopg.conninfo import make_conninfo
from psycopg.rows import dict_row

from graph.graph import build_graph
from graph.state import Graph_state, RetryContext

load_dotenv()


class AsyncRunner:
    def __init__(self):
        self.loop = asyncio.SelectorEventLoop(
            selectors.SelectSelector()
        )
        self.ready = threading.Event()

        self.connection = None
        self.checkpointer = None
        self.graph = None

        self.thread = threading.Thread(
            target=self._run_loop,
            daemon=True,
        )
        self.thread.start()
        self.ready.wait()

        # اتصال و ساخت گراف روی event loop دائمی
        self.run(self._initialize())

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.ready.set()
        self.loop.run_forever()

    def run(self, coro):
        future = asyncio.run_coroutine_threadsafe(
            coro,
            self.loop,
        )
        return future.result()

    async def _initialize(self):
        conninfo = make_conninfo(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            dbname=os.environ["POSTGRES_DB"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
        )

        self.connection = await AsyncConnection.connect(
            conninfo,
            autocommit=True,
            prepare_threshold=0,
            row_factory=dict_row,
        )

        self.checkpointer = AsyncPostgresSaver(
            self.connection
        )

        # جدول‌های داخلی LangGraph
        await self.checkpointer.setup()

        # ساخت گراف با ذخیره‌ساز PostgreSQL
        self.graph = build_graph(self.checkpointer)


async def run_graph(
    user_input: str,
    thread_id: str,
    graph,
):
    initial_state = Graph_state(
        messages=[HumanMessage(content=user_input)],
        question=user_input,
        thread_id=thread_id,
        retry=RetryContext(),
    )

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }
    print('thread_id = '+ thread_id)
    snapshot = await graph.aget_state(config)
    print(snapshot.values['messages'].content)
    return await graph.ainvoke(
        initial_state,
        config=config,
    )

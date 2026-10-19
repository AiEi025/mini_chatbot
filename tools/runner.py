import asyncio
import os
import selectors
import threading

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres.aio import AsyncPostgresStore
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
        self.store_connection = None
        self.store = None
        self.graph = None

        self.thread = threading.Thread(
            target=self._run_loop,
            daemon=True,
        )
        self.thread.start()
        self.ready.wait()

        # اتصال، ساخت گراف و آماده‌سازی جدول‌ها
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
        self.store_connection = await AsyncConnection.connect(
        conninfo,
        autocommit=True,
        prepare_threshold=0,
        row_factory=dict_row,
        )
        self.store = AsyncPostgresStore(self.store_connection)
        await self.store.setup()
        # ساخت گراف با Checkpointer
        self.graph = build_graph(checkpointer=self.checkpointer , store=self.store)

        # جدول مدیریت چت‌ها
        await self._create_chat_sessions_table()

    async def _create_chat_sessions_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS chat_sessions (
            thread_id UUID PRIMARY KEY,
            title TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            deleted_at TIMESTAMPTZ NULL
        );
        """

        create_index_query = """
        CREATE INDEX IF NOT EXISTS idx_chat_sessions_active
        ON chat_sessions (updated_at DESC)
        WHERE deleted_at IS NULL;
        """

        async with self.connection.cursor() as cur:
            await cur.execute(create_table_query)
            await cur.execute(create_index_query)

    # ----------------------------------
    # 1. ایجاد چت
    # ----------------------------------
    async def create_chat(
        self,
        thread_id: str,
        first_message: str,
    ):
        title = " ".join(first_message.split()).strip()

        if not title:
            title = "New chat"
        elif len(title) > 80:
            title = title[:77] + "..."

        query = """
            INSERT INTO chat_sessions (
                thread_id,
                title
            )
            VALUES (%s, %s)
            ON CONFLICT (thread_id)
            DO UPDATE SET
                title = CASE
                    WHEN chat_sessions.title = 'گفتگوی جدید'
                    THEN EXCLUDED.title
                    ELSE chat_sessions.title
                END,
                updated_at = NOW()
            RETURNING thread_id, title, created_at, updated_at;
            """

        async with self.connection.cursor() as cur:
            await cur.execute(
                query,
                (thread_id, title),
            )
            return await cur.fetchone()

    # ----------------------------------
    # 2. دریافت فهرست چت‌های فعال
    # ----------------------------------
    async def list_chats(self):
        query = """
        SELECT
            thread_id,
            title,
            created_at,
            updated_at
        FROM chat_sessions
        WHERE deleted_at IS NULL
        ORDER BY updated_at DESC;
        """

        async with self.connection.cursor() as cur:
            await cur.execute(query)
            return await cur.fetchall()

    # ----------------------------------
    # 3. بازیابی پیام‌های یک چت
    # ----------------------------------
    async def get_chat_messages(
        self,
        thread_id: str,
    ):
        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

        snapshot = await self.graph.aget_state(config)

        if not snapshot or not snapshot.values:
            return []

        return snapshot.values.get("messages", [])

    # ----------------------------------
    # 4. به‌روزرسانی زمان آخرین فعالیت
    # ----------------------------------
    async def update_chat_activity(
        self,
        thread_id: str,
    ):
        query = """
        UPDATE chat_sessions
        SET updated_at = NOW()
        WHERE thread_id = %s
          AND deleted_at IS NULL;
        """

        async with self.connection.cursor() as cur:
            await cur.execute(query, (thread_id,))

    # ----------------------------------
    # 5. حذف منطقی چت
    # ----------------------------------
    async def delete_chat(
        self,
        thread_id: str,
    ):
        query = """
        UPDATE chat_sessions
        SET deleted_at = NOW()
        WHERE thread_id = %s
          AND deleted_at IS NULL
        RETURNING thread_id;
        """

        async with self.connection.cursor() as cur:
            await cur.execute(query, (thread_id,))
            return await cur.fetchone()


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

    return await graph.ainvoke(
        initial_state,
        config=config,
    )
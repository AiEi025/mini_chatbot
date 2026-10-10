
import uuid

import streamlit as st
from langchain_core.messages import AIMessage

from file_manager.file_manager import File_Manager
from tools.runner import AsyncRunner, run_graph

# ----------------------------
# App configuration
# ----------------------------

st.set_page_config(
    page_title="NEXUS AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ----------------------------
# Custom theme
# ----------------------------

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(
                ellipse at 10% 0%,
                rgba(17, 75, 94, 0.32),
                transparent 42%
            ),
            #081923;
        color: #EAF3F7;
    }

    [data-testid="stSidebar"] {
        background: #0B202C;
        border-right: 1px solid #244453;
    }

    [data-testid="stHeader"] {
        background: rgba(8, 25, 35, 0.85);
    }

    .hero {
        padding: 1.3rem 1.5rem;
        border: 1px solid #244453;
        border-radius: 20px;
        background: linear-gradient(
            120deg,
            #102D3B,
            #0B202C
        );
        margin-bottom: 1.2rem;
    }

    .hero h1 {
        color: #F0F7FA;
        margin-bottom: 0.3rem;
    }

    .hero p {
        color: #A7C0CC;
        margin-bottom: 0;
    }

    .accent {
        color: #FF9D45;
    }

    [data-testid="stChatMessage"] {
        border: 1px solid #244453;
        border-radius: 16px;
        background: rgba(16, 43, 57, 0.65);
    }

    [data-testid="stChatInput"] {
        border-color: #315365;
    }

    div.stButton > button {
        border-radius: 12px;
        border: 1px solid #315365;
        background: #102D3B;
        color: #EAF3F7;
        transition: 0.2s ease;
    }

    div.stButton > button:hover {
        border-color: #FF9D45;
        color: #FFB875;
    }

    [data-testid="stFileUploader"] {
        background: #102733;
        border-radius: 14px;
        padding: 0.5rem;
    }

    hr {
        border-color: #244453;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------
# Persistent app resources
# ----------------------------

@st.cache_resource
def get_async_runner():
    return AsyncRunner()


@st.cache_resource
def get_file_manager():
    return File_Manager()


runner = get_async_runner()
file_manager = get_file_manager()


# ----------------------------
# Session state
# ----------------------------

def create_chat():
    chat_id = str(uuid.uuid4())

    st.session_state.chats[chat_id] = {
        "title": "گفتگوی جدید",
        "messages": [],
    }

    st.session_state.active_chat_id = chat_id


if "chats" not in st.session_state:
    st.session_state.chats = {}

if "active_chat_id" not in st.session_state:
    create_chat()

if st.session_state.active_chat_id not in st.session_state.chats:
    create_chat()


# ----------------------------
# Sidebar
# ----------------------------

with st.sidebar:
    st.markdown(
        """
        <h2 style="margin-bottom:0;color:#F0F7FA">
            🤖 NEXUS <span style="color:#FF9D45">AI</span>
        </h2>
        <p style="color:#91AEBB;font-size:13px">
            Your personal AI workspace
        </p>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "＋  گفتگوی جدید",
        use_container_width=True,
        type="primary",
    ):
        create_chat()
        st.rerun()

    st.divider()

    st.markdown("### 💬 تاریخچه")

    for chat_id, chat in reversed(
        list(st.session_state.chats.items())
    ):
        title = chat["title"]

        if st.button(
            f"💬  {title}",
            key=f"chat_{chat_id}",
            use_container_width=True,
        ):
            st.session_state.active_chat_id = chat_id
            st.rerun()

    st.divider()

    st.markdown("### 📁 فایل‌ها")

    upload_file = st.file_uploader(
        "فایل موردنظر را انتخاب کن",
        type=["txt", "pdf", "md", "py"],
        key="sidebar_upload",
        help="PDF و TXT برای RAG، فایل MD برای مهارت‌ها و PY برای کار با کد.",
    )

    if upload_file is not None:
        # Identify the exact uploaded content so that ordinary
        # Streamlit reruns do not repeatedly index the same file.
        import hashlib

        file_bytes = upload_file.getvalue()
        upload_hash = hashlib.sha256(file_bytes).hexdigest()

        if st.session_state.get("indexed_file_hash") != upload_hash:
            try:
                with st.spinner("در حال آماده‌سازی فایل..."):
                    file_manager.index_file(
                        upload_file=upload_file
                    )

                st.session_state.indexed_file_hash = upload_hash
                st.session_state.active_file_name = upload_file.name
                st.success(f"فایل آماده شد: {upload_file.name}")

            except Exception as exc:
                st.error(f"خطا در آماده‌سازی فایل: {exc}")

    active_file = st.session_state.get("active_file_name")

    if active_file:
        st.caption(f"فایل فعال: {active_file}")
    else:
        st.caption("هنوز فایلی انتخاب نشده است.")


# ----------------------------
# Main chat
# ----------------------------

active_chat_id = st.session_state.active_chat_id
active_chat = st.session_state.chats[active_chat_id]

st.markdown(
    """
    <div class="hero">
        <h1>NEXUS <span class="accent">AI</span></h1>
        <p>
            یک محیط برای گفتگو، جست‌وجو، برنامه‌ریزی و توسعه‌ی Python
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Render only the messages stored for the selected UI conversation.
for message in active_chat["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ----------------------------
# Chat input and execution
# ----------------------------

prompt = st.chat_input("پیامت را بنویس...")

if prompt:
    active_chat["messages"].append(
        {"role": "user", "content": prompt}
    )

    if active_chat["title"] == "گفتگوی جدید":
        active_chat["title"] = prompt[:32]

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            with st.spinner("NEXUS در حال فکر کردن است..."):
                result = runner.run(
                    run_graph(
                        prompt,
                        thread_id=active_chat_id,
                    )
                )

            # Find the latest assistant message that looks like
            # a final answer, rather than a tool-call message.
            answer = None

            for message in reversed(result["messages"]):
                if (
                    isinstance(message, AIMessage)
                    and isinstance(message.content, str)
                    and message.content.strip()
                    and not getattr(message, "tool_calls", None)
                ):
                    answer = message.content
                    break

            if not answer:
                answer = "پاسخ نهایی از Agent دریافت نشد."

            st.markdown(answer)

            active_chat["messages"].append(
                {"role": "assistant", "content": answer}
            )

        except Exception as exc:
            st.error("هنگام اجرای Agent خطایی رخ داد.")
            st.exception(exc)
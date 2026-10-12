import hashlib
import uuid

import streamlit as st
from langchain_core.messages import AIMessage

from file_manager.file_manager import File_Manager
from tools.runner import AsyncRunner, run_graph

# ============================================================
# APP CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="NEXUS AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# THEME
# ============================================================

st.markdown(
    """
    <style>
    :root {
        --bone: #F4F1E9;
        --surface: #FAF8F3;
        --sidebar: #E9E9DF;
        --olive: #737F60;
        --olive-dark: #606B50;
        --olive-border: #879174;
        --text: #30342D;
        --muted: #666A60;
        --border: #D6D7CC;
    }

    /* Global */
    .stApp {
        background: var(--bone);
        color: var(--text);
    }

    body,
    [data-testid="stMarkdownContainer"],
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    label {
        color: var(--text);
    }

    h1, h2, h3, h4, h5, h6 {
        color: var(--text) !important;
    }

    [data-testid="stHeader"] {
        background: rgba(244, 241, 233, 0.96);
    }

    [data-testid="stMain"] {
        background: var(--bone);
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 1050px;
        padding-top: 1.6rem;
        padding-bottom: 8rem !important;
    }

    /* Sidebar: light background and dark text */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div:first-child {
        background: var(--sidebar);
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] * {
        color: var(--text);
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: var(--muted);
    }

    [data-testid="stSidebar"] hr {
        border-color: var(--border);
    }

    /* Sidebar chat history buttons */
    [data-testid="stSidebar"] div.stButton > button {
        width: 100%;
        min-height: 42px;
        border-radius: 11px;
        border: 1px solid transparent;
        background: transparent;
        color: var(--text) !important;
        text-align: right;
        transition: background 0.18s ease,
                    border-color 0.18s ease;
    }

    [data-testid="stSidebar"] div.stButton > button:hover {
        background: var(--bone);
        border-color: var(--border);
    }

    /* New chat and selected chat */
    [data-testid="stSidebar"] div.stButton > button[kind="primary"] {
        background: #DDE0D3 !important;
        border: 1px solid #D0D4C5 !important;
        color: var(--text) !important;
    }

    [data-testid="stSidebar"] div.stButton > button[kind="primary"]:hover {
        background: #D4D9C9 !important;
        color: var(--text) !important;
    }

    /* Hero */
    .hero {
        padding: 1.5rem 1.6rem;
        margin-bottom: 1.5rem;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 18px;
    }

    .hero h1 {
        font-size: 2rem;
        font-weight: 700;
        margin: 0 0 0.45rem 0;
        color: var(--text) !important;
    }

    .hero p {
        color: var(--muted) !important;
        margin: 0;
        line-height: 1.9;
    }

    .hero-mark {
        color: var(--olive-dark) !important;
    }

    /* Chat messages */
    [data-testid="stChatMessage"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 15px;
        padding: 1rem 1.1rem;
        margin-bottom: 0.8rem;
    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"],
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] span {
        color: var(--text) !important;
        line-height: 1.9;
    }

    [data-testid="stChatMessage"] pre {
        background: #EAE7DD;
        border: 1px solid var(--border);
        border-radius: 10px;
    }

    [data-testid="stChatMessage"] code {
        color: var(--text);
    }

    [data-testid="stChatMessage"] a {
        color: var(--olive-dark) !important;
    }

    /* ========================================================
       CHAT INPUT BAR
       The attachment + input row is positioned as one unit.
       Its left offset is adjusted when the desktop sidebar is open.
    ======================================================== */


    [data-testid="stMain"] [data-testid="stChatInput"]:focus-within {
        border-color: var(--bone) !important;
        box-shadow: 0 0 0 2px rgba(244, 241, 233, 0.3),
                    0 5px 24px rgba(48, 52, 45, 0.12) !important;
    }

    [data-testid="stMain"] [data-testid="stChatInput"] textarea {
        color: var(--bone) !important;
        caret-color: var(--bone) !important;
        background: transparent !important;
        max-height: 6rem !important;
        overflow-y: auto !important;
        resize: none !important;
        line-height: 1.7 !important;
    }

    [data-testid="stMain"] [data-testid="stChatInput"] textarea::placeholder {
        color: var(--bone) !important;
        opacity: 0.9 !important;
    }

    [data-testid="stMain"] [data-testid="stChatInput"] button {
        color: var(--bone) !important;
    }

    [data-testid="stMain"] [data-testid="stChatInput"] button:hover {
        background: var(--olive-dark) !important;
    }

    /* ========================================================
       ATTACHMENT + INPUT: SAME FIXED BOTTOM BAR
    ======================================================== */

    /*
       The attachment column and chat input are rendered in
       the same Streamlit horizontal block. Fix that row as a
       single unit, so the attachment button stays beside the
       input rather than floating elsewhere on the page.
    */

    [data-testid="stMain"] div[data-testid="stHorizontalBlock"]:has(
        [data-testid="stChatInput"]
    ) {
        position: fixed !important;
        z-index: 999 !important;

        left: 1.5rem !important;
        right: 1.5rem !important;
        bottom: 1rem !important;

        width: auto !important;
        max-width: 1000px;
        margin: 0 auto !important;
        padding: 0.55rem !important;
        box-sizing: border-box;

        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: flex-end !important;
        gap: 0.6rem !important;

        background: var(--olive) !important;
        border: 1px solid var(--olive-dark);
        border-radius: 17px;
        box-shadow: 0 5px 24px rgba(48, 52, 45, 0.12);
    }

    /*
       The chat input itself is no longer independently fixed:
       it sits naturally inside the shared bar.
    */

    [data-testid="stMain"] div[data-testid="stHorizontalBlock"]:has(
        [data-testid="stChatInput"]
    ) [data-testid="stChatInput"] {
        position: static !important;
        inset: auto !important;
        width: 100% !important;
        max-width: none !important;
        margin: 0 !important;
        box-shadow: none !important;
        flex: 1 1 auto !important;
    }

    [data-testid="stMain"] div[data-testid="stHorizontalBlock"]:has(
        [data-testid="stChatInput"]
    ) > [data-testid="column"] {
        min-width: 0 !important;
    }

    [data-testid="stMain"] div[data-testid="stHorizontalBlock"]:has(
        [data-testid="stChatInput"]
    ) > [data-testid="column"]:last-child {
        flex: 0 0 3rem !important;
        width: 3rem !important;
    }

    /* Attachment button */
    [data-testid="stMain"] [data-testid="stPopover"] > button {
        width: 100%;
        min-height: 2.8rem;
        border: 1px solid var(--olive-border) !important;
        background: var(--olive-dark) !important;
        color: var(--bone) !important;
        border-radius: 12px !important;
        transition: background 0.18s ease;
    }

    [data-testid="stMain"] [data-testid="stPopover"] > button:hover {
        background: #535E46 !important;
        color: var(--bone) !important;
    }

    /* Prevent the conversation from being hidden by the bar */
    [data-testid="stMainBlockContainer"] {
        padding-bottom: 8rem !important;
    }

    /* ========================================================
       FILE UPLOADER
    ======================================================== */

    [data-testid="stPopoverBody"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 14px;
    }

    [data-testid="stPopoverBody"] * {
        color: var(--text);
    }

    /*
       Keep the uploader in its normal neutral style.
       Only make its informational text readable.
    */

    [data-testid="stFileUploader"] {
        background: var(--surface) !important;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0.6rem;
    }

    [data-testid="stFileUploader"] section {
        background: var(--olive-dark) !important;
        border: 1px dashed var(--olive-border) !important;
        border-radius: 10px;
    }

    [data-testid="stFileUploader"] section *,
    [data-testid="stFileUploader"] section small,
    [data-testid="stFileUploader"] section span,
    [data-testid="stFileUploader"] section div,
    [data-testid="stFileUploader"] section p {
        color: var(--bone) !important;
    }

    [data-testid="stFileUploader"] button {
        color: var(--text) !important;
        border-color: var(--border) !important;
    }

    /* General buttons */
    div.stButton > button {
        border-radius: 11px;
        border: 1px solid var(--border);
        background: var(--surface);
        color: var(--text) !important;
        transition: background 0.18s ease,
                    border-color 0.18s ease;
    }

    div.stButton > button:hover {
        border-color: var(--olive);
        background: #EAE7DD;
        color: var(--text) !important;
    }

    /* Other form controls */
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stNumberInput"] input {
        color: var(--text) !important;
        background: var(--surface);
        border-color: var(--border);
        border-radius: 10px;
    }

    [data-testid="stSelectbox"] * {
        color: var(--text);
    }

    [data-testid="stSpinner"] * {
        color: var(--text) !important;
    }

    [data-testid="stAlert"] {
        border-radius: 12px;
    }

    hr {
        border-color: var(--border);
    }

    /* Responsive */
    @media (max-width: 900px) {
        [data-testid="stMain"] div[data-testid="stHorizontalBlock"]:has(
            [data-testid="stChatInput"]
        ) {
            left: 1rem !important;
            right: 1rem !important;
            bottom: 0.6rem !important;
            max-width: none !important;
        }

        

        [data-testid="stMainBlockContainer"] {
            padding-left: 1rem;
            padding-right: 1rem;
            padding-bottom: 7rem !important;
        }
    }

    @media (max-width: 480px) {
        .hero {
            padding: 1rem;
            border-radius: 14px;
        }

        .hero h1 {
            font-size: 1.65rem;
        }

        [data-testid="stMain"] div[data-testid="stHorizontalBlock"]:has(
            [data-testid="stChatInput"]
        ) {
            left: 0.5rem !important;
            right: 0.5rem !important;
            bottom: 0.4rem !important;
            gap: 0.35rem !important;
            padding: 0.4rem !important;
        }

        [data-testid="stMain"] div[data-testid="stHorizontalBlock"]:has(
            [data-testid="stChatInput"]
        ) > [data-testid="column"]:last-child {
            flex-basis: 2.7rem !important;
            width: 2.7rem !important;
        }
    }

    /* Desktop: reserve the sidebar's actual layout space when it is open.
       Streamlit's standard sidebar is about 21rem wide. */
    @media (min-width: 901px) {
        body:has([data-testid="stSidebar"][aria-expanded="true"])
        [data-testid="stMain"] div[data-testid="stHorizontalBlock"]:has(
            [data-testid="stChatInput"]
        ) {
            left: calc(21rem + 1.5rem) !important;
            right: 1.5rem !important;
        }
    }

    /* On narrow screens the sidebar overlays the page rather than taking
       permanent layout width. Hide the bar while it is open, so it cannot
       sit on top of the sidebar; it returns when the sidebar closes. */
    @media (max-width: 900px) {
        body:has([data-testid="stSidebar"][aria-expanded="true"])
        [data-testid="stMain"] div[data-testid="stHorizontalBlock"]:has(
            [data-testid="stChatInput"]
        ) {
            visibility: hidden !important;
            pointer-events: none !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# PERSISTENT RESOURCES
# ============================================================

@st.cache_resource
def get_async_runner():
    return AsyncRunner()


@st.cache_resource
def get_file_manager():
    return File_Manager()


runner = get_async_runner()
file_manager = get_file_manager()


# ============================================================
# SESSION STATE
# ============================================================

def create_chat():
    chat_id = str(uuid.uuid4())

    st.session_state.chats[chat_id] = {
        "title": "گفتگوی جدید",
        "messages": [],
        "file_name": None,
        "file_hash": None,
    }

    st.session_state.active_chat_id = chat_id


if "chats" not in st.session_state:
    st.session_state.chats = {}

for chat in st.session_state.chats.values():
    chat.setdefault("file_name", None)
    chat.setdefault("file_hash", None)
    chat.setdefault("messages", [])
    chat.setdefault("title", "گفتگوی جدید")

if "active_chat_id" not in st.session_state:
    create_chat()

if st.session_state.active_chat_id not in st.session_state.chats:
    create_chat()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown(
        """
        <div style="padding: 0.35rem 0 0.6rem 0;">
            <h2 style="
                margin: 0;
                color: #30342D;
                font-size: 1.65rem;
                letter-spacing: -0.04em;
            ">
                🤖 NEXUS
                <span style="color: #606B50;">AI</span>
            </h2>
            <p style="
                margin-top: 0.35rem;
                margin-bottom: 0;
                font-size: 0.83rem;
                color: #666A60;
            ">
                فضای کاری هوشمند شما
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "＋  گفتگوی جدید",
        key="new_chat_button",
        use_container_width=True,
        type="primary",
    ):
        create_chat()
        st.rerun()

    st.divider()

    st.markdown("### تاریخچه گفتگو")

    for chat_id, chat in reversed(
        list(st.session_state.chats.items())
    ):
        title = chat["title"].strip() or "گفتگوی جدید"

        if len(title) > 30:
            title = title[:30] + "…"

        is_active = (
            chat_id == st.session_state.active_chat_id
        )

        button_label = (
            f"●  {title}" if is_active
            else f"💬  {title}"
        )

        if st.button(
            button_label,
            key=f"chat_{chat_id}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.active_chat_id = chat_id
            st.rerun()


# ============================================================
# ACTIVE CHAT
# ============================================================

active_chat_id = st.session_state.active_chat_id
active_chat = st.session_state.chats[active_chat_id]


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">
        <h1>
            NEXUS <span class="hero-mark">AI</span>
        </h1>
        <p>
            یک فضای یکپارچه برای گفتگو، جست‌وجو،
            برنامه‌ریزی و توسعه‌ی Python
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CHAT HISTORY
# ============================================================

for message in active_chat["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ============================================================
# ATTACHMENT + CHAT INPUT
# ============================================================

# Both controls are placed in one horizontal row.
# CSS keeps this row fixed at the bottom of the main area.

input_col, attach_col = st.columns(
    [9, 1],
    vertical_alignment="bottom",
)

with attach_col, st.popover("📎", use_container_width=True):
    st.markdown("**فایل این گفتگو**")

    upload_file = st.file_uploader(
        "فایل موردنظر را انتخاب کن",
        type=["txt", "pdf", "md", "py"],
        key=f"chat_upload_{active_chat_id}",
        help=(
            "PDF و TXT برای RAG، فایل MD برای مهارت‌ها "
            "و PY برای کار با کد."
        ),
        label_visibility="collapsed",
    )

    if upload_file is not None:
        file_bytes = upload_file.getvalue()
        upload_hash = hashlib.sha256(
            file_bytes
        ).hexdigest()

        if active_chat.get("file_hash") != upload_hash:
            try:
                with st.spinner("در حال آماده‌سازی فایل..."):
                    file_manager.index_file(
                        upload_file=upload_file,
                        thread_id=active_chat_id
                    )

                active_chat["file_hash"] = upload_hash
                active_chat["file_name"] = upload_file.name

                st.success(
                    f"فایل آماده شد: {upload_file.name}"
                )

            except Exception as exc:
                st.error(
                    f"خطا در آماده‌سازی فایل: {exc}"
                )

    if active_chat.get("file_name"):
        st.caption(
            f"فایل فعال: {active_chat['file_name']}"
        )
    else:
        st.caption("هنوز فایلی انتخاب نشده است.")


with input_col:
    prompt = st.chat_input(
        "پیامت را بنویس...",
        key=f"chat_input_{active_chat_id}",
    )


# ============================================================
# CHAT EXECUTION
# ============================================================

if prompt:
    active_chat["messages"].append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    if active_chat["title"] == "گفتگوی جدید":
        active_chat["title"] = (
            prompt.strip().replace("\n", " ")[:32]
            or "گفتگوی جدید"
        )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            with st.spinner("NEXUS در حال فکر کردن است..."):
                result = runner.run(
                    run_graph(
                        user_input=prompt,
                        thread_id=active_chat_id,
                    )
                )

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
                {
                    "role": "assistant",
                    "content": answer,
                }
            )

        except Exception as exc:
            st.error("هنگام اجرای Agent خطایی رخ داد.")
            st.exception(exc)


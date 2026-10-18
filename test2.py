# import os

# import psycopg
# from dotenv import load_dotenv

# load_dotenv()


# connection_string = (
#     f"host={os.getenv('POSTGRES_HOST', 'localhost')} "
#     f"port={os.getenv('POSTGRES_PORT', '5432')} "
#     f"dbname={os.getenv('POSTGRES_DB')} "
#     f"user={os.getenv('POSTGRES_USER')} "
#     f"password={os.getenv('POSTGRES_PASSWORD')}"
# )

# try:
#     with psycopg.connect(connection_string) as conn:
#         with conn.cursor() as cur:
#             cur.execute("SELECT version();")
#             version = cur.fetchone()[0]

#             cur.execute("SELECT current_database();")
#             database = cur.fetchone()[0]

#         print("Connection successful!")
#         print("Database:", database)
#         print("PostgreSQL version:", version)

# except Exception as e:
#     print("Connection failed:", e)






from langchain_core.prompts import ChatPromptTemplate

from graph.state import Router_state
from model.model import Llm_model

llm = (
    Llm_model(
        model_name='deepseek-v4-flash',
        reasoning_effort="high",
    )
    .chose_model()
    .with_structured_output(
        Router_state,
        method="json_mode",
    )
)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        'Return JSON with one field "state", '
        'whose value is one of: python, planning, tools, general.',
    ),
    ("human", "{question}"),
])

chain = prompt | llm

print(chain.invoke({"question": "How can I travel from New York to Los Angeles?"}))
from openai import OpenAI
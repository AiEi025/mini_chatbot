from typing import Literal, TypedDict

from langchain_core.prompts import ChatPromptTemplate

from model.model import Llm_model


class Router_state(TypedDict):
    state:Literal['python','planning','tools']=None
llm = Llm_model('deepseek-v4-flash',0).chose_model().with_structured_output(Router_state)
prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            You are the router of an AI assistant.

            Classify the user's request into exactly one category:

            - python:
              when the user wants to inspect, debug, fix, or modify
              an uploaded Python file.

            - planning:
              when the user asks for planning, scheduling,
              prioritization, or time management.

            - tools:
              when the request requires web search, RAG,Uploaded files, or another tool.

            Return only the structured classification.
            """
        ),
        ("human", "{question}")
    ])
chain = prompt | llm
result = chain.invoke({"question": 'tell me about shipping policy from uploaded file'})    
print(result['category'])
print(result['state'])
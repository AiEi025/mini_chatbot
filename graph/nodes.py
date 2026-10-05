import asyncio
import json
import sys
from pathlib import Path

from tools import python_validator

skills_dir = Path(__file__).parent.parent / "skills"
workspace_dir = Path(__file__).parent.parent / "workspace"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import state
from dotenv import load_dotenv
from langchain.tools import ToolNode
from langchain_core.prompts import ChatPromptTemplate

from graph.tools import CustomAgent
from mcp_root.client import main
from model.model import Llm_model

load_dotenv()
py_collection = Path(__file__).resolve().parent.parent /'py_collection.json'

mcp_tools = asyncio.run(main())
tool_node = ToolNode(mcp_tools)
 
def router(g_state:state.Graph_state)->state.Graph_state:
    query = g_state.messages[-1].content
    llm = Llm_model('openrouter',0).chose_model().with_structured_output(state.Router_state)
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
              when the request requires web search, RAG, or another tool.

            Return only the structured classification.
            """
        ),
        ("human", "{query}")
    ])
    chain = prompt | llm
    result = chain.invoke({"query": query})    
    return {'status':result["messages"] , 'question':query}

python_agent = CustomAgent(model=Llm_model("deepseek-v4-flash",0).chose_model(),
                           agent_type='d_agent',
                           skill_path=skills_dir/ "python-fixer",
                           workspace_path=workspace_dir/'python').build()
def python_node(g_state:state.Graph_state)->state.Graph_state:
    
    with open(py_collection, 'r', encoding='utf-8') as r:
        data = json.load(r)
    question = g_state.question
    g_state.file_path =data['collection_name']
    file_path = g_state.file_path
    validation = g_state.validation
    if not file_path:
        raise ValueError("file_path is missing")
    if validation:
        prompt = f"""
                    Fix the Python file.
        
                    User request:
                    {question}
        
                    Target file:
                    {file_path}
        
                    Read the file first.
                    Analyze the problem.
                    Fix the problem by editing the file.
                    Do not modify unrelated files.
                    """
        
        result = python_agent.invoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                },
                config={'configurable':{'thread_id':'user_1'}}
            )

        return {
        "messages": result["messages"]
        }
    elif validation == False:
        validation_feedback = g_state.validation_feedback
        prompt = f"""
                            Fix the Python file.
                
                            subprocess return stdout and stderr:
                            {validation_feedback}
                
                            Target file:
                            {file_path}
                
                            Read the file first.
                            Analyze the problem.
                            Fix the problem by editing the file.
                            Do not modify unrelated files.
                            """
        result = python_agent.invoke(
                    {
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    },
                    config={'configurable':{'thread_id':'user_1'}}
                )
        return {'messages':result["messages"] , 'validation_feedback':"" , "attempts":g_state.attempts - 1}
              
def validation_node(g_state: state.Graph_state) -> state.Graph_state: 
    file_path = g_state.file_path
    if not file_path:
        raise ValueError("file_path is missing")
    result = python_validator.PythonValidator(workspace_dir = workspace_dir).validate(file_path=file_path)
    attemp = g_state.attempts
    if attemp <= 0:
        validation = True
        return {'validation_feedback':result['stdout'] + result['stderr'] , 'validation':validation}
    return {'validation_feedback':result['stdout'] + result['stderr'] , 'validation':result['ok']}

def cond_python(g_state: state.Graph_state)->str|state.Graph_state:
    validation = g_state.validation
    attemp = g_state.attempts 
    if validation or attemp <= 0:
        return 'end'
    return 'python_node'

planning_agent = CustomAgent(model = Llm_model('deepseek-v4-flash' , 0.3).chose_model() ,
                             agent_type='d_agent',
                             skill_path=skills_dir/ "daily-planner",
                             sysprompt="""You are a daily planning assistant. Your job is to help the user organize their day effectively.

When the user asks for help planning their day:
1. Gather context: Ask for tasks, appointments, and priorities.
2. Identify priorities: Distinguish urgent vs. important.
3. Estimate time: Ask for realistic durations.
4. Use write_todos: Create a structured TODO list with content, activeForm, and status.
5. Order logically: Sequence tasks by energy levels and fixed times.
6. Update progress: Mark tasks completed and move the next to in_progress.

## Guidelines
- Confirm available working hours before planning.
- Ask specific questions if the user is vague.
- Suggest breaks and buffer time between high-focus tasks.""").build()
def planning_node(g_state:state.Graph_state)->state.Graph_state:
    validation = g_state.validation
    if validation:
        question = g_state.question
        result = planning_agent.invoke({
        "messages": [
                {
                    "role": "user",
                    "content": question
                }
                ]
            })
        return {'messages':result['messages']}
    else:
        feedback = g_state.validation_feedback
        message = g_state.messages[-1].content
        prompt = f"""
The previous planning result was:

{message}

A planning critic reviewed it and provided this feedback:

{feedback}

Please revise the planning result according to the critic feedback.

Original user request:
{g_state.question}

Return an improved final plan.
"""
        result = planning_agent.invoke({"messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                        ]})
        return{'messages':result['messages'] , 'attempts':g_state.attempts - 1}
        
        
def planning_validation(g_state:state.Graph_state)->state.Graph_state:
    question = g_state.question
    message = g_state.messages[-1].content
    prompt = f"""
You are a strict planning critic.

User request:
{question}

Generated plan:
{message}

Check whether the plan:
1. Addresses the user's request.
2. Covers the important tasks.
3. Has a logical order.
4. Avoids obvious time conflicts.
5. Respects constraints mentioned by the user.
6. Is actionable and realistic.

Return:
- status=True if the plan is acceptable.
- status=False if it needs revision.
- feedback explaining what must be improved.
"""

    llm = Llm_model('openrouter').chose_model().with_structured_output(state.Planning_state)
    result = llm.invoke(prompt)
    return {'validation_feedback':result['feedback'] , 'validation':result['status']}

def cond_planning(g_state:state.Graph_state)->str:
    validation = g_state.validation
    attemp = g_state.attempts
    if validation or attemp <= 0:
        return 'end'
    return 'planning_node'

def tools_node(g_state:state.Graph_state)->state.Graph_state:
    ...
    
    
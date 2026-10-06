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
from langchain_core.prompts import ChatPromptTemplate

from graph.tools import CustomAgent, extract_tool_calls
from mcp_root.client import main
from model.model import Llm_model

load_dotenv()
py_collection = Path(__file__).resolve().parent.parent /'py_collection.json'

mcp_tools = asyncio.run(main())
# tool_node = ToolNode(mcp_tools)
 
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
                },config={'configurable':{'thread_id':'user_1'}}
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
        retry = g_state.retry.record_attempt()
        
        result = python_agent.invoke(
                    {
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    },config={'configurable':{'thread_id':'user_1'}}
                    
                )
        return {'messages':result["messages"] , 'validation_feedback':"" , "retry":retry}
              
def validation_node(g_state: state.Graph_state) -> state.Graph_state: 
    file_path = g_state.file_path
    if not file_path:
        raise ValueError("file_path is missing")
    result = python_validator.PythonValidator(workspace_dir = workspace_dir).validate(file_path=file_path)
    retry = g_state.retry
    if retry.exhausted:
        validation = True
        return {'validation_feedback':result['stdout'] + result['stderr'] , 'validation':validation}
    return {'validation_feedback':result['stdout'] + result['stderr'] , 'validation':result['ok']}

def cond_python(g_state: state.Graph_state)->str|state.Graph_state:
    validation = g_state.validation
    retry = g_state.retry 
    if validation or retry.exhausted:
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
            },config={'configurable':{'thread_id':'user_1'}})
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
        retry = g_state.retry.record_attempt()
        result = planning_agent.invoke({"messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                        ]},config={'configurable':{'thread_id':'user_1'}})
        return{'messages':result['messages'] , 'retry':retry}
        
        
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
    retry = g_state.retry.exhausted
    if retry:
        return {'validation_feedback':result['feedback'] , 'validation':True}
    return {'validation_feedback':result['feedback'] , 'validation':result['status']}

def cond_planning(g_state:state.Graph_state)->str:
    validation = g_state.validation
    retry = g_state.retry.exhausted
    if validation or retry:
        return 'end'
    return 'planning_node'

tool_agent = CustomAgent(model=Llm_model('deepseek-v4-flash' , 0.3).chose_model(),
                         agent_type='l_agent',
                         tools=mcp_tools,
                         sysprompt=None)
def tools_node(g_state:state.Graph_state)->state.Graph_state:
    question = g_state.question
    retry = g_state.retry.record_attempt()
    if g_state.validation:
        prompt = f"""
Answer the user's request.

User request:
{question}

Use the available tools when they are necessary.
Do not use a tool if it is not needed.

After using the tools, provide a clear final answer to the user.
"""
        result = tool_agent.invoke({'messages':[{
            'role':'user',
            'content':prompt
        }]},config={'configurable':{'thread_id':'user_1'}})
        return {'messages':result['messages']}
    
    last_message = g_state.messages[-1].content
    feedback = g_state.validation_feedback
    prompt = f"""
You previously attempted to answer the user's request, but the result
did not pass validation.

Original user request:
{question}

Previous answer:
{last_message}

Validation feedback:
{feedback}

Please try again.

Use the available tools when necessary.
Pay close attention to the validation feedback.
Do not repeat the previous mistake.

Return a new, improved final answer to the user.
"""

    result = tool_agent.invoke({'messages':[{
        'role':'user',
        'content':prompt
    }]},config={'configurable':{'thread_id':'user_1'}})
    return{'messages':result['messages'] , 'retry':retry}

def tools_validation(g_state:state.Graph_state)->state.Graph_state:
    tool_calls = extract_tool_calls(g_state.messages)
    question = g_state.question
    
    messages = []

    for message in g_state.messages:

        content = getattr(message, "content", None)

        if content:
            messages.append(
                f"{message.__class__.__name__}: {content}"
            )

    conversation = "\n\n".join(messages)
    
    prompt = f"""
You are a strict tool-use critic.

Your job is to evaluate whether an AI agent used tools correctly
and whether its final answer is supported by the tool results.

User request:
{question}

Agent execution:
{conversation}

Tool calls:
{tool_calls}

Evaluate the following:

1. Relevance
Does the final answer actually address the user's request?

2. Tool selection
Were the selected tools appropriate for the user's request?
If no tool was necessary, using a tool should not automatically be
considered an error.

3. Tool arguments
Were the arguments passed to the tools appropriate and relevant?

4. Tool results
Do the tool results provide useful information for answering the request?

5. Grounding
Is the final answer supported by the information returned by the tools?
The agent must not invent facts that are not supported by the tool results.

6. Completeness
If the request required information from a tool, did the agent obtain
enough information to provide a useful answer?

Return:
- status=True if the execution and final answer are acceptable.
- status=False if the agent should retry.
- feedback must clearly explain what is wrong and what should be changed
  during the retry.

Do not mark an answer as invalid merely because no tool was used.
Judge whether the agent's behavior was appropriate for the user's request.
"""
    llm = Llm_model('openrouter',0).chose_model().with_structured_output(state.ToolValidationState)
    result = llm.invoke(prompt)
    if g_state.retry.exhausted:
        return{'validation_feedback':result.feedback , 'validation':True}
    return {
    "validation": result.status,
    "validation_feedback": result.feedback,
}

def cond_tools(g_state:state.Graph_state)->str:
    validation = g_state.validation
    retry = g_state.retry
    if validation or retry.exhausted:
        return 'end'
    return 'tools_node'
    
  
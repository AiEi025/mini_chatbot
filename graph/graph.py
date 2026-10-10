import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

import graph.nodes as node
from graph import state

checkpointer = MemorySaver()
builder = StateGraph(state.Graph_state)

builder.add_node('router', node.router_node)
builder.add_node('python', node.python_node)
builder.add_node('py_validate', node.py_validation)
builder.add_node('plan', node.planning_node)
builder.add_node('plan_validate', node.planning_validation)
builder.add_node('tools', node.tools_node)
builder.add_node('tools_validate', node.tools_validation)
builder.add_node('general' , node.general_node)

builder.set_entry_point('router')

# مسیریابی به فقط یک مسیر
builder.add_conditional_edges(
    'router',
    node.route_decision,
    {'python': 'python', 'plan': 'plan', 'tools': 'tools' , 'general':'general'}
)

# اجرا → اعتبارسنجی
builder.add_edge('python', 'py_validate')
builder.add_edge('plan', 'plan_validate')
builder.add_edge('tools', 'tools_validate')
builder.add_edge('general' , END)

# اعتبارسنجی → retry یا پایان
builder.add_conditional_edges('py_validate',  node.cond_python,   {'end': END, 'python_node': 'python'})
builder.add_conditional_edges('plan_validate', node.cond_planning, {'end': END, 'planning_node': 'plan'})
builder.add_conditional_edges('tools_validate', node.cond_tools,  {'end': END, 'tools_node': 'tools'})

graph = builder.compile(checkpointer=checkpointer)


try:
    graph.get_graph().draw_mermaid_png(output_file_path='./graph_nodes.png')
except Exception as e:
    print(f'رسم گراف ناموفق بود: {e}')
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
builder.add_node('python',node.python_node)
builder.add_node('py_validate',node.py_validation)
builder.add_node('plan' , node.planning_node)
builder.add_node('plan_validate', node.planning_validation)
builder.add_node('tools',node.tools_node)
builder.add_node('tools_validate',node.tools_validation)
builder.set_entry_point('router')

builder.add_conditional_edges('py_validate' , node.cond_python , {'end':END , 'python_node':'python'})
builder.add_conditional_edges('plan_validate',node.cond_planning , {'end':END ,'planning_node':'plan'})
builder.add_conditional_edges('tools_validate',node.cond_tools , {'end':END ,'tools_node':'tools'})

graph = builder.compile(checkpointer=checkpointer)
graph.get_graph().draw_mermaid_png(output_file_path='./graph.png')

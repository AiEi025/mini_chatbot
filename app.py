import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from file_manager.file_manager import File_Manager
from tools.runner import run_graph

file_manager = File_Manager()



# try:
upload_file = st.file_uploader(label='Upload',max_upload_size = 20 ,type=["txt", "pdf","md","py"])
query = st.text_input(label='input retriever')
if upload_file:
    file_manager.index_file(upload_file= upload_file)

button = st.button(label='confirm')
if button and query:
    result = asyncio.run(run_graph(query))
    st.text_area(label='answer',
        value=result["messages"][-1].content
    )
else:
        st.warning(body='please please write your query')
        
# except:
#     st.error( body="you should upload pdf or txt file ")

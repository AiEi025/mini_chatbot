import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from file_manager.file_manager import File_Manager

file_manager = File_Manager()

# try:
upload_file = st.file_uploader(label='Upload',max_upload_size = 20 ,type=["txt", "pdf","md","py"])
if upload_file == None:
    st.warning(body='please upload file')
else:
    file_manager.index_file(upload_file= upload_file)
    query = st.text_input(label='input retriever')
    button = st.button(label='confirm')
    if button:pass
         #st.text_area(asyncio.run(main(query=query)))
# except:
#     st.error( body="you should upload pdf or txt file ")

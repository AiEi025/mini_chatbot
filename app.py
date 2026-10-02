# this page related to streamlit 

# in this section we need to built a chat bot 
# that can gave file for RAG

import streamlit as st

from tools import rag

# try:
upload_file = st.file_uploader(label='Upload',max_upload_size = 20 ,type=["txt", "pdf","md"])
if upload_file == None:
    st.warning(body='please upload file')
else:
    st.text_area(label='text_reader' , value=upload_file.getvalue())
    query = st.text_input(label='input retriever')
    button = st.button(label='confirm')
    if button:
        retriever = rag.retriever(upload_file=upload_file)
        st.text_area(label = 'rag_response' , value=rag.find_retrieve(query=query , best_retriever=retriever))
# except:
#     st.error( body="you should upload pdf or txt file ")

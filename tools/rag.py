import hashlib
from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.document_loaders.parsers import PyPDFParser
from langchain_core.documents import Document
from langchain_core.documents.base import Blob
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"


def retriever(upload_file_name ,upload_file_getvalue ):
    suffix = Path(upload_file_name).suffix.lower()  

    # --- ساخت لیست Document در هر دو حالت ---
    if suffix == ".pdf":
        blob = Blob.from_data(
            upload_file_getvalue,
            mime_type="application/pdf",
            path=upload_file_name,
        )
        docs = list(PyPDFParser().parse(blob))   # ← لیست Document

    elif suffix == ".txt":
        text = upload_file_getvalue
        if isinstance(text, bytes):
            text = text.decode("utf-8", errors="ignore")
        docs = [Document(page_content=text, metadata={"source": upload_file_name})]
        
    elif suffix =='.md':
        SKILLS_DIR.mkdir(parents=True, exist_ok=True)
        safe_name = Path(upload_file_name)
        dest = SKILLS_DIR / safe_name
        if dest.exists():
            file_hash = hashlib.md5(upload_file_getvalue).hexdigest()[:8]
            dest = SKILLS_DIR / f"{dest.stem}_{file_hash}{dest.suffix}"

        dest.write_bytes(upload_file_getvalue)

    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )




    all_chunks = text_splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(model_name = 'sentence-transformers/all-mpnet-base-v2',
                                      encode_kwargs={"normalize_embeddings": True})
    collection_name = Path(upload_file_name).stem
    if Path(f"./chroma_db/{collection_name}").exists():
        vectorstore = Chroma(embedding_function = embeddings,
                                      persist_directory="./chroma_db",
                                      collection_name=collection_name)
    else:
        vectorstore = Chroma.from_documents(embedding = embeddings,
                                        documents=all_chunks,
                                  persist_directory="./chroma_db",
                                  collection_name=collection_name)    

    retriever = vectorstore.as_retriever(search_kwargs ={'k':3})
    return retriever 

def find_retrieve(query: str , best_retriever) -> str:
   
    docs = best_retriever.invoke(query)
    
    return "\n\n---\n\n".join(doc.page_content for doc in docs)
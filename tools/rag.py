import json
import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent)
)

from langchain_chroma import Chroma
from langchain_classic.retrievers import EnsembleRetriever
from langchain_huggingface import HuggingFaceEmbeddings


class RAG:

    def __init__(self):
        self.BASEPATH = Path(__file__).resolve().parent.parent / ".chroma_db"
        self.PATH_COLLECTION = Path("./collection.json")

        # Retriever در ابتدا وجود ندارد
        self.retriever = None

        # Embedding model
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2",
            encode_kwargs={
                "normalize_embeddings": True
            }
        )

    def find_retrieve(self, query: str, thread_id: str) -> str:
    
        with open(self.PATH_COLLECTION, 'r', encoding='utf-8') as r:
            data = json.load(r)
    
        collection_names = data.get(thread_id, [])
    
        if not collection_names:
            return "هیچ فایلی برای این گفتگو یافت نشد."
    
        retrievers = []
        for name in collection_names:
            collection_path = self.BASEPATH / thread_id / name
    
            # اگر پوشه کالکشن وجود نداشت، رد شو
            if not collection_path.exists():
                continue
            
            vectorstore = Chroma(
                embedding_function=self.embeddings,
                persist_directory=str(collection_path),
                collection_name=name,
            )
            retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
            retrievers.append(retriever)
    
        if not retrievers:
            return "هیچ دادهٔ قابل بازیابی‌ای پیدا نشد."
    
        # ادغام چندین Retriever
        ensemble = EnsembleRetriever(
            retrievers=retrievers,
            weights=[1.0] * len(retrievers)   # وزن مساوی (می‌توانی بعداً تنظیم کنی)
        )
    
        docs = ensemble.invoke(query)
        docs = docs[:5]
    
        return "\n\n---\n\n".join(doc.page_content for doc in docs)
    
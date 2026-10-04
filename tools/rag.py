import json
import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent)
)

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


class RAG:

    def __init__(self):

        # مسیر Chroma
        self.CHROMA_DIR = self.BASE_DIR / "chroma_db"
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

    def find_retrieve(self, query: str) -> str:
        path_collection = self.PATH_COLLECTION
        with open(path_collection, 'r', encoding='utf-8') as r:
            data = json.load(r)
        self.vectorstore = Chroma(
                            embedding_function=self.embeddings,
                            persist_directory=str(
                                self.CHROMA_DIR
                            ),
                            collection_name=data['collection_name'],
                        )
        self.retriever = (
                        self.vectorstore.as_retriever(
                            search_kwargs={
                                "k": 3
                            }
                        )
                    )

        docs = self.retriever.invoke(query)

        return "\n\n---\n\n".join(
            doc.page_content
            for doc in docs
        )

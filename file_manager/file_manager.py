import hashlib
import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent)
)
from langchain_chroma import Chroma
from langchain_community.document_loaders.parsers import PyPDFParser
from langchain_core.documents import Document
from langchain_core.documents.base import Blob
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from file_manager.tools import collection


class File_Manager:

    def __init__(self):

        # مسیر پروژه
        self.BASE_DIR = Path(__file__).resolve().parent.parent

        # مسیر skills
        self.SKILLS_DIR = self.BASE_DIR / "skills"
        self.WORKSPACE=self.BASE_DIR /"workspace"

        # مسیر Chroma
        self.CHROMA_DIR = self.BASE_DIR / ".chroma_db"
        self.PATH_COLLECTION = Path("./collection.json")
        self.PYTHON_COLLECTION = Path("./py_collection.json")

        # Embedding model
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2",
            encode_kwargs={
                "normalize_embeddings": True
            }
        )

        # Text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )

    def index_file(self, upload_file , thread_id:str ):

        """
        دریافت فایل Streamlit و ساخت Vector Store
        """

        if upload_file is None:
            raise ValueError("No file was uploaded.")

        upload_file_name = upload_file.name
        upload_file_getvalue = upload_file.getvalue()

        suffix = Path(upload_file_name).suffix.lower()
        

        # --------------------------------
        # PDF
        # --------------------------------

        if suffix == ".pdf":

            blob = Blob.from_data(
                upload_file_getvalue,
                mime_type="application/pdf",
                path=upload_file_name,
            )

            docs = list(
                PyPDFParser().parse(blob)
            )

        # --------------------------------
        # TXT
        # --------------------------------

        elif suffix == ".txt":

            text = upload_file_getvalue

            if isinstance(text, bytes):
                text = text.decode(
                    "utf-8",
                    errors="ignore"
                )

            docs = [
                Document(
                    page_content=text,
                    metadata={
                        "source": upload_file_name
                    }
                )
            ]

        # --------------------------------
        # Markdown
        # --------------------------------

        elif suffix == ".md":

            safe_name = Path(upload_file_name)
        
            if "python" in safe_name.stem.lower():
                skill_dir = self.SKILLS_DIR / "python-fixer"
        
            elif "plan" in safe_name.stem.lower():
                skill_dir = self.SKILLS_DIR / "daily-planner"

            else:
                skill_dir = self.SKILLS_DIR /"general"
        
            skill_dir.mkdir(
                parents=True,
                exist_ok=True
            )
            dest = skill_dir / safe_name

            if dest.exists():
            
                file_hash = hashlib.md5(
                    upload_file_getvalue
                ).hexdigest()[:8]
        
                dest = skill_dir / (
                    f"{dest.stem}_{file_hash}{dest.suffix}"
                )
        
            dest.write_bytes(
                upload_file_getvalue
            )
        elif suffix == '.py':
            safe_name = Path(upload_file_name)
            workspace_dir = self.WORKSPACE / thread_id / "python"
            workspace_dir.mkdir(parents=True ,exist_ok=True)
            dest = workspace_dir / safe_name
            if dest.exists():
                file_hash = hashlib.md5(
                                    upload_file_getvalue
                                ).hexdigest()[:8]
                        
                dest = workspace_dir / (
                                    f"{dest.stem}_{file_hash}{dest.suffix}"
                                )
                collection(collection_name=self.PYTHON_COLLECTION , dest=dest , thread_id=thread_id)
                
            else:
                collection(collection_name=self.PYTHON_COLLECTION , dest=dest , thread_id=thread_id)
                    
            dest.write_bytes(
                             upload_file_getvalue
                            )
        
        else:pass

        # --------------------------------
        # Split Documents
        # --------------------------------
        if suffix == '.pdf' or suffix == '.txt':
            all_chunks = self.text_splitter.split_documents(docs)
        
            # --------------------------------
            # Collection name
            # --------------------------------
            collection_name = Path(upload_file_name).stem
        
            path_collection = self.PATH_COLLECTION
            collection(collection_name=path_collection, dest=collection_name, thread_id=thread_id)
        
            # --------------------------------
            # Create / Load Chroma
            # --------------------------------
            collection_path = self.CHROMA_DIR / thread_id / collection_name
            collection_path.mkdir(parents=True, exist_ok=True)
        
            # اگر پوشه خالی بود → کالکشن جدید بساز
            if not any(collection_path.iterdir()):
                self.vectorstore = Chroma.from_documents(
                    documents=all_chunks,
                    embedding=self.embeddings,
                    persist_directory=str(collection_path),
                    collection_name=collection_name,
                )
            else:
                # اگر از قبل وجود داشت → لود کن
                self.vectorstore = Chroma(
                    persist_directory=str(collection_path),
                    embedding_function=self.embeddings,
                    collection_name=collection_name,
                )
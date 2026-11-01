<<<<<<< HEAD
from langchain_core.documents import Document
from app.configs.settings import Settings
from pathlib import Path
import csv
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.utils import get_logger

logger = get_logger(__name__)

class DocumentService:
    """Service for document processing."""

    SUPPORTED_FILE_EXTENSIONS = {".csv"}

    TRANSCRIPT_CSV_FIELDNAMES = {
        "id",
        "start",
        "end",
        "url",
        "channel_id",
        "title",
        "published",
        "text",
    }

    def __init__(self, chunk_size: int | None = None, chunk_overlap: int | None = None):
        settings = Settings()
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, 
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
            length_function=len,
        )

    def _is_transcript_csv(self, file_path: Path) -> bool:
        with file_path.open(newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            if not reader.fieldnames:
                return False 
            fields = set[str](reader.fieldnames)
            return self.TRANSCRIPT_CSV_FIELDNAMES.issubset(fields)


    def load_transcript_csv(self, file_path: Path, source_name: str | None = None) -> list[Document]:
        """Load a transcript CSV file into a list of documents."""
        documents: list[Document] = []

        with file_path.open(newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                text = row.get("text", "").strip()
                if not text:
                    continue
                metadata = {
                    "source": source_name,
                    "id": row.get("id", ""),
                    "start": row.get("start", ""),
                    "end": row.get("end", ""),
                    "url": row.get("url", ""),
                    "channel_id": row.get("channel_id", ""),
                    "title": row.get("title", ""),
                    "published": row.get("published", ""),
                }

                documents.append(Document(page_content=text, metadata=metadata))
        logger.info(f"Loaded {len(documents)} documents from {file_path}")
        return documents

    def load_file(self, file_path: Path, source_name: str | None = None) -> list[Document]:
        file_path = Path(file_path)
        source = source_name or file_path.name 
        ext = file_path.suffix.lower()
        if ext not in self.SUPPORTED_FILE_EXTENSIONS:
            raise ValueError(f"Unsupported file extension: {ext}")

        if ext == ".csv":
            if self._is_transcript_csv(file_path):
                docs = self.load_transcript_csv(file_path, source)
            else:
                raise ValueError(f"Unsupported CSV file: {file_path}")
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
        
        return docs


    def split_documents(self, documents: list[Document]) -> list[Document]:
        return self.text_splitter.split_documents(documents)

    def process_file(self, file_path: Path, source_name: str | None = None) -> list[Document]:
        documents = self.load_file(file_path, source_name)
        return self.split_documents(documents)


    
=======




from asyncio.log import logger
import csv
from typing import Self
from xml.dom.minidom import Document

from anyio import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.configs import settings
from app.configs.settings import get_settings


class DocumentService:
    """Service for managing and processing documents"""
    Supported_extensions = {".csv"}

    def __init__(self, chunk_size:int | None =None, chunk_overlap:int | None = None):
        settings = get_settings()
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        logger.info(f"Initialized DocumentService with chunk_size: {self.chunk_size}, chunk_overlap: {self.chunk_overlap}")
        self.text_splitter= RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )

    transcript_csv_header = {"id", "text", "start", "end", "url", "channel_id", "title", "published"}
    def _is_transcript_csv(self, file_path: str) -> bool:
        """Check if the file is a transcript CSV based on its header"""
        with file_path.open('r', encoding='utf-8') as f:
            reader = csv.dictReader(f)
            if reader.fieldnames is None:
                return False
            fields=set[str](reader.fieldnames)
            return self.transcript_csv_header.issubset(fields) and len(fields)== len(self.transcript_csv_header)
        
    def load_transcript_csv(self, file_path: str,source_name:str):
        """Load transcript from a CSV file"""
        documents:list[Document]=[]

        with open(file_path,'r',encoding='utf-8') as f:
            reader=csv. DictReader(f)
            for row in reader:
                text=row.get("text","").strip()
                if not text:
                    continue
                metadata={
                    "source": source_name,
                    "id": row.get("id","").strip(),
                    "start": row.get("start","").strip(),
                    "end": row.get("end","").strip(),
                    "url": row.get("url","").strip(),
                    "channel_id": row.get("channel_id","").strip(),
                    "title": row.get("title","").strip(),
                    "published": row.get("published","").strip(),
                }
                documents.append(page_content=text, metadata=metadata))
        logger.info(f"Loaded {len(documents)} documents from {file_path}")
        return documents

    def text_split_documents(self,documents:list[Document]) -> list[Document]:
        """split documents into smaller chunks based on the chunk size and overlap
        """
        return self.text_splitter.split_documents(documents)


    def load_file(self, file_path: str, source_name: str) -> list[Document]:
        """Load a file and return a list of documents"""
        
        file_path = Path(file_path)
        source=source_name or file_path.name
        extension = file_path.suffix.lower()
        if extension not in Self.Supported_extensions:
            raise ValueError(f"Unsupported file extension: {extension}. Supported extensions are: {Self.Supported_extensions}")
        if extension == ".csv":
            if self._is_transcript_csv(file_path):
                logger.info(f"Loading transcript CSV from {file_path}")
                return self.load_transcript_csv(file_path, source)
            else:
                raise ValueError(f"File {file_path} is not a recognized transcript CSV. Please ensure it has the correct header: {self.transcript_csv_header}")

        else:
            raise ValueError(f"Unsupported file extension: {extension}. Supported extensions are: {Self.Supported_extensions}")

    def prcess_file(self,file_path:str,source_name:str) -> list[Document]:
        """Load and split a file into documents"""
        documents=self.load_file(file_path,source_name)
        logger.info(f"Loaded {len(documents)} documents from {file_path}")
        split_documents=self.text_split_documents(documents)
        logger.info(f"Split into {len(split_documents)} documents")
        return split_documents
>>>>>>> 2c341cf (Implement document ingestion service)

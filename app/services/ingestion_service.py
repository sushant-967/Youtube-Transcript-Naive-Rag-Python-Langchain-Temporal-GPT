import uuid
from app.configs.settings import get_settings
from app.repositories.vector_store_repository import VectorStoreRepository
from app.services.document_service import DocumentService
from pathlib import Path
from app.utils import get_logger

logger = get_logger(__name__)


class IngestionService:

    def __init__(self):
        self.settings = get_settings()
        self.document_service = DocumentService()
        self.vector_store_repository = VectorStoreRepository()

    def save_upload_batch(self, file_pairs: list[tuple[str, bytes]]) -> tuple[str, list[Path]]:
        batch_id = str(uuid.uuid4())
        upload_dir = Path(self.settings.upload_dir) / batch_id
        upload_dir.mkdir(parents=True, exist_ok=True)
        saved_files = []

        for filename, file_content in file_pairs:
            file_path = upload_dir / filename
            file_path.write_bytes(file_content)
            saved_files.append(file_path)
            logger.info(f"Saved file: {file_path}")
        return batch_id, saved_files

    def ingest_file_at_path(self, file_path: Path, source_name: str | None = None) -> list[str]:
        name=source_name or file_path.stem

        chunks = self.document_service.process_file(file_path, name)
        if not chunks:
            return {"filename": file_path.name, "chunks_created":0,"document_ids": []}
        
        document_ids = self.vector_store_repository.add_documents(chunks)
        
        return {"filename": file_path.name, "chunks_created": len(chunks), "document_ids": document_ids}

    def ingest_files_at_sync(self, file_pairs:list[tuple[str, bytes]]) -> list[dict]:
        _, paths= self.save_upload_batch(file_pairs)
        results = []
        for path in paths:
            result = self.ingest_file_at_path(path)
            results.append(result)
        total_chunks = sum(result["chunks_created"] for result in results)
        logger.info(f"Total chunks created from batch: {total_chunks}")
        return {
            "chunks_created": total_chunks,
            "files": results,
            "files_total": len(results),
            "message":"Documents uploaded and indexed successfully."
        }

        
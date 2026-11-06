




from asyncio.log import logger
from pathlib import Path

from temporalio import workflow

from app.temporal.activities.ingestion import parse_documents_activity, chunk_documents_activity, index_documents_activity
from datetime import timedelta


DEFAULT_INDEX_BATCH_SIZE = 100

@dataclass 
class FileIngestInput:
    local_path: str
    filename: str

@dataclass
class BatchIngestProgress:
    status: str ="RUNNING"
    files_total: int = 0
    files_completed: int = 0
    current_filename: str | None = None
    file_results: list[dict[str,Any]] = Field(default_factory=list)

@workflow.defn
class BatchIngestWorkflow:
    """Workflow to handle batch ingestion of files. It parses, chunks, and indexes documents from the provided file paths."""
    
    def __init__(self)->None:
        self.progress = BatchIngestProgress()

    @workflow.query
    def get_progress(self) -> BatchIngestProgress:
        """Query to get the current progress of the batch ingestion."""
        return self.progress

    @workflow.run
    async def run(self, file_inputs: list[FileIngestInput]) -> BatchIngestProgress:
        """Run the batch ingestion workflow."""
        self.progress.status = "RUNNING"
        batch_size=DEFAULT_INDEX_BATCH_SIZE
        self.progress.files_total = len(file_inputs)

        for file_input in file_inputs:
            self.progress.current_filename = file_input.filename
           
            # Parse documents
            doc_dicts = await workflow.execute_activity(
                parse_documents_activity,
                file_input.local_path,
                file_input.filename,
                start_to_close_timeout=timedelta(minutes=30),
            )

            # Chunk documents
            chunk_dicts = await workflow.execute_activity(
                chunk_documents_activity,
                doc_dicts,
                start_to_close_timeout=timedelta(minutes=30),
            )

            # Index documents in batches
            total_chunks = len(chunk_dicts)
            indexed_count = 0
            for i in range(0, total_chunks, DEFAULT_INDEX_BATCH_SIZE):
                batch = chunk_dicts[i:i + DEFAULT_INDEX_BATCH_SIZE]
                indexed_count += await workflow.execute_activity(
                    index_documents_activity,
                    batch,
                    start_to_close_timeout=timedelta(minutes=30),
                    heartbeat_timeout=timedelta(minutes=5)
                )

            self.progress.file_results.append({
                "filename": file_input.filename,
                "chunks_created": total_chunks,
                "document_ids":[]
            })
         
            self.progress.files_completed += 1
        self.progress.status = "COMPLETED"
        self.progress.current_filename = None
        return self.progress


from attrs import asdict

from app.temporal.client import get_temporal_client
from app.utils.logger import get_logger
from app.configs.settings import get_settings
from app.services.ingestion_service import IngestionService
from app.temporal.workflows.ingestion import BatchIngestWorkflow, FileIngestInput



logger=get_logger(__name__)

class TemporalIngestionService:
    """Service for ingesting documents using Temporal workflows."""
    
    def __init__(self):
        self.settings=get_settings()
        self.ingestion_service=IngestionService()

    async def start_batch_ingestion(self, file_pairs: list[tuple[str, bytes]]) -> str:
        """Start a batch ingestion workflow."""
        batch_id, paths = self.ingestion_service.save_upload_batch(file_pairs)
        file_inputs = [FileIngestInput(filename=path.name, source_name=path.stem) for path in paths]
        
        client = await get_temporal_client()
        handle =await client.start_workflow(
            BatchIngestWorkflow.run,
            file_inputs,
            id=f"batch_ingest_{batch_id}",
            task_queue=self.settings.temporal_task_queue
        )
        logger.info(f"Started batch ingestion workflow with ID: batch_ingest_{batch_id}")
        return {
            "message": "Batch ingestion workflow started successfully.",
            "workflow_id": f"batch_ingest_{batch_id}",
            "batch_id": batch_id,
            "run_id":handle.run_id,
            "files_total": len(file_inputs),
            "filenames": [file_input.filename for file_input in file_inputs]

        }

    async def get_workflow_progress(self, workflow_id: str) -> dict:
        client = await get_temporal_client()
        handle = client.get_workflow_handle(workflow_id)
        progress=None
        try:
            progress = await handle.query(BatchIngestWorkflow.get_progress)
        except Exception as e:
            progress = None
        if progress:
            data=asdict(progress)
            return {
                "workflow_id": workflow_id,
                "status": data.get("status", "UNKNOWN"),
                "files_total": data.get("files_total"),
                "files_completed": data.get("files_completed"),
                "current_filename": data.get("current_filename"),
                "file_results": data.get("file_results"),
            }
        return {
            "workflow_id": workflow_id,
            "status": "UNKNOWN",
            "files_total": 0,
            "files_completed": 0,
            "current_filename": None,
            "file_results": [],
        }
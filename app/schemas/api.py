from pydantic import BaseModel, Field
from datetime import datetime

class HealthResponse(BaseModel):
    """Response for the health check endpoint."""

    status: str = Field(..., description="The status of the application.")
    timestamp: datetime = Field(..., description="The timestamp of the response.")

class DocumentBatchUploadResponse(BaseModel):
    """Response for the document batch upload endpoint."""

    chunks_created: int = Field(..., description="The number of chunks created.")
    files: list[dict] = Field(..., description="The files that were uploaded and indexed.")
    files_total: int = Field(..., description="The total number of files that were uploaded.")
    message: str = Field(..., description="The message from the ingestion service.")

class AsyncIngestionStartedResponse(BaseModel):
    """Response for the asynchronous ingestion started endpoint."""

    workflow_id: str = Field(..., description="The ID of the started workflow.")
    batch_id: str = Field(..., description="The ID of the batch that was started.")
    run_id: str = Field(..., description="The run ID of the started workflow.")
    filenames: list[str] = Field(..., description="The names of the files that were uploaded.")
    files_total: int = Field(..., description="The total number of files that were uploaded.")
    message: str = Field(..., description="The message from the ingestion service.")

class IngestStatusResponse(BaseModel):
    """Response for the ingestion status endpoint."""

    workflow_id: str = Field(..., description="The ID of the workflow.")
    status: str = Field(..., description="The current status of the ingestion process.")
    files_total: int = Field(..., description="The total number of files to be ingested.")
    files_completed: int = Field(..., description="The number of files that have been completed.")
    current_filename: str | None = Field(None, description="The name of the file currently being processed.")
    file_results: list[dict] = Field(..., description="The results of the processed files.")
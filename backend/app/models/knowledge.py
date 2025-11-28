from beanie import Document, PydanticObjectId
from pydantic import Field
from datetime import datetime
from typing import Optional, List

class DocumentItem(Document):
    user_id: PydanticObjectId
    filename: str
    file_type: str
    content: str            # The extracted text lives here
    file_size: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "pending" # pending -> processing -> indexed

class EmbeddingChunk(Document):
    document_id: PydanticObjectId  # Link to the parent PDF
    chunk_index: int               # Order (0, 1, 2...)
    text: str                      # The actual paragraph content
    vector: List[float]

    class Settings:
        name = "embedding_chunks"
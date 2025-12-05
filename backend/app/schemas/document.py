from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID

class DocumentBase(BaseModel):
    title: str
    filename: str

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = None

class DocumentInDBBase(DocumentBase):
    id: UUID
    mayan_document_id: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
    owner_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Document(DocumentInDBBase):
    pass

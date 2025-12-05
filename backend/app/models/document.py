from sqlalchemy import Column, String, DateTime, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    
    # Reference to the document in Mayan EDMS
    mayan_document_id = Column(String, nullable=True)
    
    # AI Analysis results
    summary = Column(Text, nullable=True)
    tags = Column(JSONB, nullable=True) # Using JSONB for tags to be flexible
    
    # Ownership
    owner_id = Column(String, nullable=False) # Keycloak User ID
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

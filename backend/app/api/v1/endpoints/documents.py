from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Any
import json

from app.api import deps
from app.core.database import get_db
from app.core.logger import logger
from app.models.document import Document
from app.models.user import User
from app.schemas.document import Document as DocumentSchema, DocumentUpdate
from app.services.mayan import mayan_service
from app.services.ollama import ollama_service

router = APIRouter()

@router.post("/", response_model=DocumentSchema)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Upload a new document.
    1. Upload to Mayan EDMS
    2. Analyze with Ollama (mock/real)
    3. Save metadata to DB
    """
    user_id = str(current_user.id)
    logger.info(f"User {user_id} uploading document: {file.filename}")
    
    try:
        # 1. Upload to Mayan
        logger.debug(f"Uploading {file.filename} to Mayan EDMS")
        mayan_id = await mayan_service.upload_document(file)
        logger.info(f"Document uploaded to Mayan with ID: {mayan_id}")
        
        # 2. Analyze with Ollama (using filename/content stub for now as we don't extract text yet)
        # In a real app, we'd extract text from the file first.
        # For now, we'll just pass the filename to get some mock tags.
        logger.debug(f"Analyzing document with Ollama")
        analysis_json = await ollama_service.analyze_text(f"Document filename: {file.filename}")
        
        try:
            analysis = json.loads(analysis_json)
            logger.debug(f"Ollama analysis result: {analysis}")
        except Exception as e:
            logger.warning(f"Failed to parse Ollama response: {e}")
            analysis = {"summary": "Analysis failed", "tags": []}

        # 3. Save to DB
        logger.debug(f"Saving document metadata to database")
        db_obj = Document(
            title=file.filename,
            filename=file.filename,
            mayan_document_id=str(mayan_id),
            summary=analysis.get("summary"),
            tags=analysis.get("tags"),
            owner_id=user_id,
        )
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        logger.info(f"Document {db_obj.id} created successfully for user {user_id}")
        return db_obj
        
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to upload document: {str(e)}")

@router.get("/", response_model=List[DocumentSchema])
async def read_documents(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve documents.
    """
    query = select(Document)
    
    # If not superuser, only show own documents
    if not current_user.is_superuser:
        query = query.where(Document.owner_id == str(current_user.id))
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    documents = result.scalars().all()
    return documents

@router.get("/{document_id}", response_model=DocumentSchema)
async def read_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get document by ID.
    """
    query = select(Document).where(Document.id == document_id)
    if not current_user.is_superuser:
        query = query.where(Document.owner_id == str(current_user.id))
        
    result = await db.execute(query)
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
        
    return document

@router.delete("/{document_id}", response_model=DocumentSchema)
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete document.
    """
    query = select(Document).where(Document.id == document_id)
    if not current_user.is_superuser:
        query = query.where(Document.owner_id == str(current_user.id))
        
    result = await db.execute(query)
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
        
    await db.delete(document)
    await db.commit()
    return document

@router.put("/{document_id}", response_model=DocumentSchema)
async def update_document(
    document_id: str,
    document_in: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update document metadata.
    """
    query = select(Document).where(Document.id == document_id)
    if not current_user.is_superuser:
        query = query.where(Document.owner_id == str(current_user.id))
        
    result = await db.execute(query)
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Update fields
    if document_in.title is not None:
        document.title = document_in.title
    if document_in.summary is not None:
        document.summary = document_in.summary
    if document_in.tags is not None:
        document.tags = document_in.tags
        
    await db.commit()
    await db.refresh(document)
    return document
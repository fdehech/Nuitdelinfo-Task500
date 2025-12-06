from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Any
import json
import uuid
from pathlib import Path
import glob
import PyPDF2
import io
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image

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
    """
    user_id = str(current_user.id)
    logger.info(f"User {user_id} uploading document: {file.filename}")
    
    # Generate ID upfront so we can use it for filename
    doc_id = uuid.uuid4()
    
    mayan_id = None
    
    try:
        # 1. Try to upload to Mayan, fallback to local storage if unavailable
        try:
            logger.debug(f"Attempting to upload {file.filename} to Mayan EDMS")
            mayan_id = await mayan_service.upload_document(file)
            logger.info(f"Document uploaded to Mayan with ID: {mayan_id}")
        except Exception as mayan_error:
            logger.warning(f"Mayan upload failed, using local storage: {mayan_error}")
            # Fallback: Save file locally using doc_id
            storage_dir = Path("/app/storage/documents")
            storage_dir.mkdir(parents=True, exist_ok=True)
            
            file_extension = Path(file.filename).suffix
            # Use doc_id as filename to link DB to File
            local_filename = f"{doc_id}{file_extension}"
            local_file_path = storage_dir / local_filename
            
            content = await file.read()
            await file.seek(0)
            
            with open(local_file_path, "wb") as f:
                f.write(content)
            
            logger.info(f"Document saved locally at: {local_file_path}")
        
        # 2. Analyze with Ollama
        logger.debug(f"Analyzing document with Ollama")
        try:
            await file.seek(0)
            content_bytes = await file.read()
            
            text_content = ""
            filename_lower = file.filename.lower()
            
            if filename_lower.endswith('.pdf'):
                try:
                    pdf_file = io.BytesIO(content_bytes)
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    # Read first 3 pages for summary
                    for page_num in range(min(len(pdf_reader.pages), 3)):
                        text_content += pdf_reader.pages[page_num].extract_text() + "\n"
                    
                    # If text is empty/short, try OCR
                    if len(text_content.strip()) < 50:
                        logger.info("PDF text empty/short, trying OCR")
                        images = convert_from_bytes(content_bytes, first_page=1, last_page=3)
                        text_content = ""
                        for img in images:
                            text_content += pytesseract.image_to_string(img) + "\n"
                            
                except Exception as pdf_e:
                    logger.warning(f"PDF extraction failed: {pdf_e}")
                    text_content = f"Binary file: {file.filename}"
            
            elif filename_lower.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
                try:
                    image = Image.open(io.BytesIO(content_bytes))
                    text_content = pytesseract.image_to_string(image)
                except Exception as img_e:
                    logger.warning(f"Image OCR failed: {img_e}")
                    text_content = f"Image file: {file.filename}"
            
            else:
                try:
                    text_content = content_bytes.decode('utf-8')
                except:
                    text_content = f"Binary file: {file.filename}"
            
            analysis_json = await ollama_service.analyze_text(f"Document content: {text_content[:4000]}")
            analysis = json.loads(analysis_json)
            logger.debug(f"Ollama analysis result: {analysis}")
        except Exception as e:
            logger.warning(f"Ollama analysis failed: {e}")
            analysis = {"summary": f"Document: {file.filename}", "tags": ["uploaded"]}

        # 3. Save to DB
        logger.debug(f"Saving document metadata to database")
        db_obj = Document(
            id=doc_id, # Use the pre-generated ID
            title=file.filename,
            filename=file.filename,
            mayan_document_id=str(mayan_id) if mayan_id else None,
            summary=analysis.get("summary"),
            tags=analysis.get("tags"),
            owner_id=user_id,
        )
        
        db.add(db_obj)
        logger.debug("Added to DB session, committing...")
        try:
            await db.commit()
            logger.debug("Commit successful")
            await db.refresh(db_obj)
            logger.debug("Refresh successful")
        except Exception as db_e:
            logger.error(f"Database commit failed: {db_e}")
            raise db_e
        
        logger.info(f"Document {db_obj.id} created successfully for user {user_id}")
        return db_obj
        
    except Exception as e:
        import traceback
        traceback.print_exc()
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
    if not current_user.is_superuser:
        query = query.where(Document.owner_id == str(current_user.id))
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
    if document_in.title is not None:
        document.title = document_in.title
    if document_in.summary is not None:
        document.summary = document_in.summary
    if document_in.tags is not None:
        document.tags = document_in.tags
    await db.commit()
    await db.refresh(document)
    return document
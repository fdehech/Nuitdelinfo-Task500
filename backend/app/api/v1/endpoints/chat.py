from fastapi import APIRouter, Depends, HTTPException
from typing import Any, List
from pydantic import BaseModel
import glob
from pathlib import Path
import PyPDF2
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

from app.api import deps
from app.models.user import User
from app.services.ollama import ollama_service
from app.core.logger import logger
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    document_ids: List[str] = []

class ChatResponse(BaseModel):
    response: str

@router.post("/", response_model=ChatResponse)
async def chat_with_documents(
    request: ChatRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Chat with documents using basic context retrieval.
    """
    
    # 1. Retrieve relevant documents
    context_text = ""
    documents = []
    
    if request.document_ids:
        from app.models.document import Document
        from sqlalchemy import select
        
        query = select(Document).where(Document.id.in_(request.document_ids))
        if not current_user.is_superuser:
            query = query.where(Document.owner_id == str(current_user.id))
            
        result = await db.execute(query)
        documents = result.scalars().all()
    else:
        from app.models.document import Document
        from sqlalchemy import select, desc
        
        query = select(Document)
        if not current_user.is_superuser:
            query = query.where(Document.owner_id == str(current_user.id))
        
        query = query.order_by(desc(Document.created_at)).limit(5)
        result = await db.execute(query)
        documents = result.scalars().all()
        
    # 2. Construct Context
    if documents:
        context_text = "Here is some context from the user's documents:\n\n"
        for doc in documents:
            summary = doc.summary or "No summary available."
            tags = ", ".join(doc.tags) if doc.tags else "No tags."
            
            # Try to read file content from local storage
            file_content = ""
            try:
                # Look for file with doc.id as filename (any extension)
                storage_path = Path("/app/storage/documents")
                search_pattern = str(storage_path / f"{doc.id}.*")
                files = glob.glob(search_pattern)
                
                if files:
                    logger.info(f"DEBUG: Found file at {files[0]}")
                    file_path = Path(files[0])
                    suffix = file_path.suffix.lower()
                    
                    if suffix == '.pdf':
                        # Extract text from PDF
                        try:
                            # Try PyPDF2 first (fast)
                            with open(file_path, 'rb') as f:
                                pdf_reader = PyPDF2.PdfReader(f)
                                text = ""
                                # Read first 5 pages max
                                for page_num in range(min(len(pdf_reader.pages), 5)):
                                    text += pdf_reader.pages[page_num].extract_text() + "\n"
                            
                            # If text is too short, try OCR (slow)
                            if len(text.strip()) < 50:
                                logger.info(f"DEBUG: PDF text empty/short, trying OCR for {doc.id}")
                                images = convert_from_path(str(file_path), first_page=1, last_page=3)
                                text = ""
                                for img in images:
                                    text += pytesseract.image_to_string(img) + "\n"
                            
                            file_content = text[:6000] # Limit to 6000 chars
                            logger.info(f"DEBUG: Extracted {len(file_content)} chars from PDF. Snippet: {file_content[:200]}")
                        except Exception as pdf_e:
                            logger.error(f"Error reading PDF {doc.id}: {pdf_e}")
                            file_content = "Could not read PDF content."
                    
                    elif suffix in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                        # Extract text from Image using OCR
                        try:
                            text = pytesseract.image_to_string(Image.open(file_path))
                            file_content = text[:6000]
                            logger.info(f"DEBUG: Extracted {len(file_content)} chars from Image. Snippet: {file_content[:200]}")
                        except Exception as img_e:
                            logger.error(f"Error reading Image {doc.id}: {img_e}")
                            file_content = "Could not read Image content."
                            
                    else:
                        # Assume text file
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            file_content = f.read(6000) # Limit to 6000 chars
                            logger.info(f"DEBUG: Read {len(file_content)} chars from text file")
                else:
                    logger.warning(f"DEBUG: No file found for doc {doc.id} at {search_pattern}")
            except Exception as e:
                logger.error(f"Error reading file content for {doc.id}: {e}")
                file_content = "Could not read file content."

            context_text += f"Document: {doc.title}\nSummary: {summary}\nTags: {tags}\nContent Snippet: {file_content}\n\n"
    else:
        context_text = "No documents found to provide context."

    # 3. Construct Prompt
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant for a Document Vault. Use the provided document context to answer the user's question. If the answer is not in the context, say so, but try to be helpful."},
        {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {request.message}"}
    ]
    
    # 4. Send to Ollama
    try:
        response_text = await ollama_service.chat(messages)
        return {"response": response_text}
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Chat Error: {e}")
        return {"response": f"I'm sorry, I encountered an error: {str(e)}"}

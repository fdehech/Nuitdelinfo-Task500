from fastapi import APIRouter, Depends, HTTPException
from typing import Any, List
from pydantic import BaseModel

from app.api import deps
from app.models.user import User
from app.services.ollama import ollama_service
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
    # If document_ids are provided, use them. Otherwise, fetch recent 5 documents.
    context_text = ""
    
    if request.document_ids:
        # Fetch specific documents
        # Note: In a real app we'd validate ownership here too
        from app.models.document import Document
        from sqlalchemy import select
        
        query = select(Document).where(Document.id.in_(request.document_ids))
        if not current_user.is_superuser:
            query = query.where(Document.owner_id == str(current_user.id))
            
        result = await db.execute(query)
        documents = result.scalars().all()
    else:
        # Fetch recent documents as general context
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
            context_text += f"Document: {doc.title}\nSummary: {summary}\nTags: {tags}\n\n"
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
        print(f"Chat Error: {e}")
        return {"response": "I'm sorry, I encountered an error while processing your request."}

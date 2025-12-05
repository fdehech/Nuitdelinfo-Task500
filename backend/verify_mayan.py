import asyncio
import io
import sys
import os

# Ensure we can import app
sys.path.append(os.getcwd())

from fastapi import UploadFile
from app.services.mayan import mayan_service

async def main():
    print("Starting Mayan EDMS Verification...")
    
    # 1. Check Document Type
    try:
        print("Checking Document Type...")
        doc_type_id = await mayan_service.get_or_create_document_type("VerificationType")
        print(f"Document Type ID: {doc_type_id}")
    except Exception as e:
        print(f"Failed to check/create document type: {e}")
        return

    # 2. Upload Document
    try:
        print("Uploading Document...")
        content = b"This is a test document content."
        file_obj = io.BytesIO(content)
        # Mock UploadFile
        upload_file = UploadFile(file=file_obj, filename="test_doc.txt")
        
        doc_id = await mayan_service.upload_document(upload_file, "VerificationType")
        print(f"Document Uploaded Successfully! ID: {doc_id}")
        
        # 3. Get Document
        print(f"Fetching Document {doc_id}...")
        doc = await mayan_service.get_document(str(doc_id))
        print(f"Document Fetched: {doc}")
        
    except Exception as e:
        print(f"Failed to upload/fetch document: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

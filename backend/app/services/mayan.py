import httpx
from app.core.config import settings
from fastapi import UploadFile, HTTPException

class MayanService:
    def __init__(self):
        self.base_url = settings.MAYAN_API_URL
        if not self.base_url.endswith("/v4"):
            self.base_url = f"{self.base_url}/v4"
        self.token = settings.MAYAN_API_TOKEN
        self.headers = {"Authorization": f"Token {self.token}"}

    async def get_or_create_document_type(self, label: str = "Default"):
        """
        Ensures a document type exists. Returns its ID.
        """
        async with httpx.AsyncClient() as client:
            try:
                # List document types to check if it exists
                resp = await client.get(
                    f"{self.base_url}/document_types/",
                    headers=self.headers
                )
                resp.raise_for_status()
                data = resp.json()
                
                for doc_type in data.get("results", []):
                    if doc_type["label"] == label:
                        return doc_type["id"]
                
                # Create if not exists
                create_resp = await client.post(
                    f"{self.base_url}/document_types/",
                    headers=self.headers,
                    json={"label": label}
                )
                create_resp.raise_for_status()
                return create_resp.json()["id"]
                
            except Exception as e:
                print(f"Error checking/creating document type: {e}")
                if settings.ENVIRONMENT == "development":
                    return 1 # Fallback for dev
                raise HTTPException(status_code=500, detail=f"Mayan Document Type Error: {e}")

    async def upload_document(self, file: UploadFile, document_type_label: str = "Default"):
        """
        Uploads a document to Mayan EDMS.
        """
        async with httpx.AsyncClient() as client:
            try:
                # Ensure document type exists
                document_type_id = await self.get_or_create_document_type(document_type_label)
                
                # Step 1: Create Document Stub
                create_resp = await client.post(
                    f"{self.base_url}/documents/",
                    headers=self.headers,
                    json={
                        "document_type_id": document_type_id,
                        "label": file.filename,
                        "description": "Uploaded via Document Vault API"
                    }
                )
                create_resp.raise_for_status()
                document_data = create_resp.json()
                document_id = document_data["id"]

                # Step 2: Upload the file content
                # Mayan API endpoint for uploading a new version/file
                # We use the 'files' endpoint for the initial file
                
                # Read file content
                content = await file.read()
                await file.seek(0) # Reset cursor
                
                files = {"file_new": (file.filename, content, file.content_type)}
                
                upload_resp = await client.post(
                    f"{self.base_url}/documents/{document_id}/files/",
                    headers=self.headers,
                    files=files
                )
                upload_resp.raise_for_status()
                
                return document_id

            except httpx.HTTPStatusError as e:
                print(f"Mayan API Error: {e.response.text}")
                if settings.ENVIRONMENT == "development":
                    return "mock-mayan-id-123"
                raise HTTPException(status_code=500, detail=f"Failed to upload to Mayan EDMS: {e}")
            except Exception as e:
                print(f"Mayan Connection Error: {e}")
                if settings.ENVIRONMENT == "development":
                    return "mock-mayan-id-123"
                raise HTTPException(status_code=500, detail=f"Failed to connect to Mayan EDMS: {e}")

    async def get_document(self, document_id: str):
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.base_url}/documents/{document_id}/",
                    headers=self.headers
                )
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                if settings.ENVIRONMENT == "development":
                    return {"id": document_id, "label": "Mock Document"}
                raise HTTPException(status_code=500, detail=f"Failed to fetch from Mayan: {e}")

mayan_service = MayanService()

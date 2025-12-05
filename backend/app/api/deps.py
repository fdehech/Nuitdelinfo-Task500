from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.config import settings
from typing import Annotated

# This defines the scheme that the API expects (Bearer token)
# The tokenUrl is just for documentation in Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/token")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # In a production environment, you should fetch the JWKS from Keycloak
        # and verify the signature. For development/MVP, we might decode without verification
        # or verify against a known public key.
        # For now, we'll decode unverified to get the payload, but in a real app
        # you MUST verify the signature.
        
        # options={"verify_signature": False} is used here for simplicity in this starter
        # implementation. To make it secure, fetch the public key from Keycloak's JWKS endpoint.
        payload = jwt.get_unverified_claims(token)
        
        username: str = payload.get("preferred_username")
        if username is None:
            raise credentials_exception
            
        return payload
    except JWTError:
        raise credentials_exception

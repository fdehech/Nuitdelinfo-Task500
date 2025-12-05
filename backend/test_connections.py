"""
Connection Test Script for Document Vault
Tests connectivity to all backend services: PostgreSQL, Mayan EDMS, and Ollama
"""
import asyncio
import sys
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
import httpx
from app.core.config import settings

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

async def test_postgres():
    """Test PostgreSQL connection"""
    print_header("Testing PostgreSQL Connection")
    
    try:
        # Create engine
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        
        # Test connection
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print_success(f"Connected to PostgreSQL")
            print_info(f"Version: {version}")
            
            # Test if tables exist
            result = await conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in result]
            
            if tables:
                print_success(f"Found {len(tables)} tables: {', '.join(tables)}")
            else:
                print_warning("No tables found - database may need initialization")
            
            # Test user table
            if 'users' in tables:
                result = await conn.execute(text("SELECT COUNT(*) FROM users"))
                count = result.scalar()
                print_info(f"Users table has {count} records")
            
            # Test documents table
            if 'documents' in tables:
                result = await conn.execute(text("SELECT COUNT(*) FROM documents"))
                count = result.scalar()
                print_info(f"Documents table has {count} records")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print_error(f"PostgreSQL connection failed: {str(e)}")
        return False

async def test_mayan():
    """Test Mayan EDMS connection"""
    print_header("Testing Mayan EDMS Connection")
    
    try:
        base_url = settings.MAYAN_API_URL
        if not base_url.endswith("/v4"):
            base_url = f"{base_url}/v4"
        
        token = settings.MAYAN_API_TOKEN
        headers = {"Authorization": f"Token {token}"}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test API connectivity
            resp = await client.get(f"{base_url}/document_types/", headers=headers)
            resp.raise_for_status()
            
            data = resp.json()
            print_success("Connected to Mayan EDMS API")
            print_info(f"API URL: {base_url}")
            print_info(f"Found {len(data.get('results', []))} document types")
            
            # List document types
            for doc_type in data.get('results', []):
                print_info(f"  - {doc_type.get('label')} (ID: {doc_type.get('id')})")
            
            # Test documents endpoint
            resp = await client.get(f"{base_url}/documents/", headers=headers)
            resp.raise_for_status()
            doc_data = resp.json()
            print_info(f"Total documents in Mayan: {doc_data.get('count', 0)}")
        
        return True
        
    except httpx.HTTPStatusError as e:
        print_error(f"Mayan API returned error: {e.response.status_code}")
        print_error(f"Response: {e.response.text}")
        return False
    except Exception as e:
        print_error(f"Mayan connection failed: {str(e)}")
        print_warning("Make sure Mayan EDMS is running and MAYAN_API_TOKEN is set correctly")
        return False

async def test_ollama():
    """Test Ollama connection"""
    print_header("Testing Ollama Connection")
    
    try:
        base_url = settings.OLLAMA_API_URL
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test API connectivity
            resp = await client.get(f"{base_url}/api/tags")
            resp.raise_for_status()
            
            data = resp.json()
            models = data.get('models', [])
            
            print_success("Connected to Ollama API")
            print_info(f"API URL: {base_url}")
            print_info(f"Found {len(models)} models")
            
            # List models
            llama_found = False
            for model in models:
                model_name = model.get('name', '')
                print_info(f"  - {model_name}")
                if 'llama3.1' in model_name:
                    llama_found = True
            
            if llama_found:
                print_success("llama3.1 model is available")
            else:
                print_warning("llama3.1 model not found - document analysis may fail")
                print_info("Run: docker exec -it document-vault-ollama ollama pull llama3.1")
            
            # Test generation
            print_info("Testing text generation...")
            resp = await client.post(
                f"{base_url}/api/generate",
                json={
                    "model": "llama3.1",
                    "prompt": "Say 'test successful' and nothing else.",
                    "stream": False
                },
                timeout=30.0
            )
            resp.raise_for_status()
            result = resp.json()
            response_text = result.get('response', '')
            print_success(f"Generation test successful: {response_text[:50]}...")
        
        return True
        
    except httpx.HTTPStatusError as e:
        print_error(f"Ollama API returned error: {e.response.status_code}")
        if e.response.status_code == 404:
            print_warning("Model not found - make sure llama3.1 is pulled")
        return False
    except Exception as e:
        print_error(f"Ollama connection failed: {str(e)}")
        print_warning("Make sure Ollama is running and the model is pulled")
        return False

async def test_backend_api():
    """Test Backend API endpoints"""
    print_header("Testing Backend API")
    
    try:
        base_url = "http://localhost:8000"
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Test health endpoint
            resp = await client.get(f"{base_url}/health")
            resp.raise_for_status()
            data = resp.json()
            
            print_success("Backend API is running")
            print_info(f"Status: {data.get('status')}")
            print_info(f"Environment: {data.get('environment')}")
            
            # Test API docs
            resp = await client.get(f"{base_url}/api/v1/docs")
            if resp.status_code == 200:
                print_success("API documentation is accessible at /api/v1/docs")
            
        return True
        
    except Exception as e:
        print_error(f"Backend API connection failed: {str(e)}")
        print_warning("Make sure the backend service is running")
        return False

async def main():
    """Run all connection tests"""
    print(f"\n{Colors.BOLD}Document Vault - Connection Test Suite{Colors.END}")
    print(f"{Colors.BOLD}Testing all backend services...{Colors.END}")
    
    results = {}
    
    # Test PostgreSQL
    results['postgres'] = await test_postgres()
    
    # Test Mayan EDMS
    results['mayan'] = await test_mayan()
    
    # Test Ollama
    results['ollama'] = await test_ollama()
    
    # Test Backend API
    results['backend'] = await test_backend_api()
    
    # Summary
    print_header("Test Summary")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for service, status in results.items():
        if status:
            print_success(f"{service.upper()}: PASSED")
        else:
            print_error(f"{service.upper()}: FAILED")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} services passed{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All services are operational!{Colors.END}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ Some services failed - check errors above{Colors.END}\n")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

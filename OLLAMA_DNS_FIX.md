# Ollama DNS Issue - Workaround Guide

## Problem

The Ollama container cannot pull models due to DNS resolution failure:
```
Error: pull model manifest: Get "https://registry.ollama.ai/v2/library/llama3.1/manifests/latest": 
dial tcp: lookup registry.ollama.ai on 127.0.0.11:53: server misbehaving
```

## Root Cause

Docker's internal DNS server (127.0.0.11) is failing to resolve external domains. This is a known issue on some Windows systems with Docker Desktop.

## Workarounds

### Option 1: Use Host Network (Temporary)

Pull the model using host network mode:

```bash
# Stop the current Ollama container
docker-compose stop ollama

# Pull the model using a temporary container with host network
docker run --rm --network host -v ollama_models:/root/.ollama ollama/ollama pull llama3.1

# Start Ollama again
docker-compose start ollama
```

### Option 2: Modify Docker Desktop DNS Settings

1. Open Docker Desktop
2. Go to Settings → Docker Engine
3. Add DNS configuration:
```json
{
  "dns": ["8.8.8.8", "1.1.1.1"]
}
```
4. Click "Apply & Restart"
5. Try pulling again:
```bash
docker exec -it document-vault-ollama ollama pull llama3.1
```

### Option 3: Use WSL2 Backend (Windows)

If using Windows:
1. Ensure WSL2 is installed and updated
2. Docker Desktop → Settings → General
3. Enable "Use the WSL 2 based engine"
4. Restart Docker Desktop
5. Try pulling again

### Option 4: Manual Model Download

1. Download the model manually from https://ollama.ai/library/llama3.1
2. Copy it into the Ollama container's volume

### Option 5: Restart Docker Service

Sometimes a full Docker restart helps:

**Windows:**
```powershell
# Restart Docker Desktop from the system tray
# Or restart the service:
Restart-Service docker
```

**Linux:**
```bash
sudo systemctl restart docker
```

Then try pulling again.

## Verification

After trying any workaround, verify the model is available:

```bash
docker exec document-vault-ollama ollama list
```

You should see `llama3.1` in the list.

## Testing Document Analysis

Once the model is pulled, test it:

```bash
docker exec document-vault-ollama ollama run llama3.1 "Say hello"
```

## Alternative: Use a Smaller Model

If the llama3.1 model continues to have issues, you can use a smaller model:

```bash
# Try pulling a smaller model
docker exec -it document-vault-ollama ollama pull llama3.2

# Update backend/app/services/ollama.py to use llama3.2 instead
```

## Current Status

- ✓ Ollama container is running
- ✓ DNS servers configured (8.8.8.8, 1.1.1.1)
- ✗ Docker internal DNS not resolving external domains
- ⚠ Model pull blocked by DNS issue

## Recommended Next Steps

1. Try **Option 1** (host network) - fastest solution
2. If that fails, try **Option 2** (Docker Desktop DNS settings)
3. If still failing, this may be a network/firewall issue - check with system administrator

## Impact on Application

**Without the model:**
- ❌ Document upload will fail (needs Ollama for analysis)
- ❌ Chat/Q&A features won't work
- ✅ User management still works
- ✅ File listing still works
- ✅ Admin dashboard still works

**With the model:**
- ✅ All features fully functional
- ✅ Real AI-powered document analysis
- ✅ Real chat responses
- ✅ No mock data anywhere

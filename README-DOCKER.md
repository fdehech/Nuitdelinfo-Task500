# Secure Document Vault - Docker Deployment Guide

This guide provides comprehensive instructions for deploying the Secure Document Vault system using Docker Compose.

## 🏗️ Architecture Overview

The system consists of the following containerized services:

- **Frontend**: React application served by NGINX
- **Backend API**: Python FastAPI server
- **Mayan EDMS**: Document management with OCR and full-text search
- **Keycloak**: SSO authentication and authorization
- **Ollama**: Local AI inference for document analysis
- **PostgreSQL**: Database for all services
- **Redis**: Caching and session management
- **NGINX**: Reverse proxy and load balancer

## 📋 Prerequisites

- Docker Engine 20.10+ ([Install Docker](https://docs.docker.com/engine/install/))
- Docker Compose 2.0+ ([Install Docker Compose](https://docs.docker.com/compose/install/))
- At least 8GB RAM available for Docker
- 50GB free disk space
- (Optional) NVIDIA GPU with Docker GPU support for AI acceleration

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd c:\Users\Furat\Documents\Nuit

# Copy environment template
cp .env.example .env

# Edit .env with your secure passwords and configuration
notepad .env
```

### 2. Configure Environment Variables

**IMPORTANT**: Update the following in your `.env` file:

- `POSTGRES_PASSWORD`: Strong database password
- `REDIS_PASSWORD`: Strong Redis password
- `KEYCLOAK_ADMIN_PASSWORD`: Keycloak admin password
- `SECRET_KEY`: Long random string (50+ characters)
- `KEYCLOAK_CLIENT_SECRET`: OAuth client secret

### 3. Create Required Directories

```bash
# Create storage directories
mkdir -p storage/documents
mkdir -p storage/uploads
mkdir -p nginx/ssl
```

### 4. Pull Ollama Model (First Time Setup)

```bash
# Start only Ollama service first
docker-compose up -d ollama

# Wait for Ollama to be ready (check with docker-compose logs -f ollama)
# Then pull your preferred model
docker exec -it document-vault-ollama ollama pull llama2

# Or use a smaller model for testing
docker exec -it document-vault-ollama ollama pull mistral
```

### 5. Start All Services

```bash
# Start all services in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
```

### 6. Initialize Keycloak

Once all services are running, configure Keycloak:

1. Access Keycloak admin console: http://localhost:8080
2. Login with credentials from `.env` (default: admin/admin)
3. Create a new realm named `documentvault`
4. Create clients for `backend-api` and `frontend-app`
5. Configure redirect URIs and client secrets
6. Update `.env` with the client secrets

### 7. Access the Application

- **Frontend**: http://localhost
- **Backend API Docs**: http://localhost/api/docs
- **Mayan EDMS**: http://localhost/mayan
- **Keycloak Admin**: http://localhost:8080

## 🔧 Service Management

### Check Service Status

```bash
# View all running containers
docker-compose ps

# Check health status
docker-compose ps | grep healthy
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose down -v
```

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service with tail
docker-compose logs -f --tail=100 backend

# Save logs to file
docker-compose logs > logs.txt
```

### Update Services

```bash
# Pull latest images
docker-compose pull

# Rebuild and restart
docker-compose up -d --build
```

## 🔐 Security Considerations

### Production Deployment Checklist

- [ ] Change all default passwords in `.env`
- [ ] Generate strong `SECRET_KEY` (use: `openssl rand -hex 32`)
- [ ] Configure SSL/TLS certificates in `nginx/ssl/`
- [ ] Enable HTTPS in `nginx/nginx.conf`
- [ ] Set `ENVIRONMENT=production` in `.env`
- [ ] Configure firewall rules (only expose ports 80, 443)
- [ ] Enable Docker secrets for sensitive data
- [ ] Set up regular database backups
- [ ] Configure log rotation
- [ ] Review and restrict CORS settings

### SSL/TLS Setup

1. Obtain SSL certificates (Let's Encrypt, commercial CA, or self-signed)
2. Place certificates in `nginx/ssl/`:
   - `cert.pem` - SSL certificate
   - `key.pem` - Private key
3. Uncomment SSL server block in `nginx/nginx.conf`
4. Restart NGINX: `docker-compose restart nginx`

## 📊 Monitoring and Maintenance

### Database Backups

```bash
# Backup PostgreSQL
docker exec document-vault-postgres pg_dumpall -U postgres > backup.sql

# Restore PostgreSQL
cat backup.sql | docker exec -i document-vault-postgres psql -U postgres
```

### Volume Management

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect nuit_postgres_data

# Backup volume
docker run --rm -v nuit_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
```

### Resource Monitoring

```bash
# View resource usage
docker stats

# View specific container
docker stats document-vault-backend
```

## 🐛 Troubleshooting

### Services Won't Start

```bash
# Check logs for errors
docker-compose logs

# Verify environment variables
docker-compose config

# Check port conflicts
netstat -ano | findstr :80
netstat -ano | findstr :8080
```

### Database Connection Issues

```bash
# Check PostgreSQL is healthy
docker-compose ps postgres

# Test database connection
docker exec -it document-vault-postgres psql -U postgres -c "\l"

# View PostgreSQL logs
docker-compose logs postgres
```

### Ollama Model Issues

```bash
# List installed models
docker exec -it document-vault-ollama ollama list

# Pull model manually
docker exec -it document-vault-ollama ollama pull llama2

# Test model
docker exec -it document-vault-ollama ollama run llama2 "Hello"
```

### NGINX Routing Issues

```bash
# Test NGINX configuration
docker exec document-vault-nginx nginx -t

# Reload NGINX
docker-compose exec nginx nginx -s reload

# Check NGINX logs
docker-compose logs nginx
```

### Reset Everything

```bash
# Stop and remove all containers, networks, and volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Start fresh
docker-compose up -d
```

## 📈 Scaling

### Horizontal Scaling

To scale specific services:

```bash
# Scale backend API to 3 instances
docker-compose up -d --scale backend=3

# Scale with load balancing (NGINX handles this automatically)
docker-compose up -d --scale backend=3 --scale frontend=2
```

### Resource Limits

Edit `docker-compose.yml` to add resource constraints:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## 🔗 Useful Commands

```bash
# Enter container shell
docker exec -it document-vault-backend bash

# Copy files from container
docker cp document-vault-backend:/app/logs ./logs

# View container IP address
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' document-vault-backend

# Prune unused resources
docker system prune -a
```

## 📞 Support

For issues and questions:

1. Check logs: `docker-compose logs -f`
2. Verify configuration: `docker-compose config`
3. Review environment variables in `.env`
4. Check service health: `docker-compose ps`

## 📝 Default Credentials

**⚠️ CHANGE THESE IN PRODUCTION!**

- **Keycloak Admin**: admin / admin
- **PostgreSQL**: postgres / changeme
- **Mayan EDMS**: admin / admin (set on first login)

## 🎯 Next Steps

1. Configure Keycloak realm and clients
2. Set up Mayan EDMS document types and workflows
3. Implement backend API endpoints
4. Build React frontend components
5. Configure AI model prompts for document analysis
6. Set up automated backups
7. Configure monitoring and alerting

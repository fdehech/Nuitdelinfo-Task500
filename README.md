# 🔐 Secure Document Vault

> **⚠️ UNDER ACTIVE DEVELOPMENT** - This project is currently in early development phase. Features are being actively implemented and the API may change.

A modern, AI-powered document management system with enterprise-grade security, built with a microservices architecture. This platform combines document management, SSO authentication, and local AI inference for intelligent document processing.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-19.2-blue.svg)](https://reactjs.org/)
[![Status](https://img.shields.io/badge/Status-Under%20Development-orange.svg)](#)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Services](#-services)
- [Development](#-development)
- [API Documentation](#-api-documentation)
- [Security](#-security)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**Secure Document Vault** is a comprehensive document management platform designed for organizations that need:

- **Secure Document Storage** - Enterprise-grade document management with OCR and full-text search
- **SSO Authentication** - Centralized authentication and authorization via Keycloak
- **AI-Powered Analysis** - Local AI inference for document analysis and intelligent search
- **Microservices Architecture** - Scalable, containerized services with Docker
- **Modern UI** - Responsive React frontend with TypeScript

### Why This Stack?

This project demonstrates modern software architecture principles:
- **Separation of Concerns** - Each service handles a specific domain
- **Security First** - Network isolation, SSO, and encrypted communications
- **Developer Experience** - Hot reload, comprehensive logging, and API documentation
- **Production Ready** - Health checks, graceful shutdowns, and container orchestration

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Host Machine                             │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Frontend   │  │   Backend    │  │   Keycloak   │         │
│  │  React+Vite  │  │   FastAPI    │  │     SSO      │         │
│  │   :3000      │  │   :8000      │  │   :8082      │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                  │
│  ┌──────┴──────────────────┴──────────────────┴────────┐        │
│  │              Frontend Network (Bridge)              │        │
│  └─────────────────────────┬───────────────────────────┘        │
│                            │                                     │
│  ┌─────────────────────────┴───────────────────────────┐        │
│  │              Backend Network (Internal)             │        │
│  │                                                      │        │
│  │  ┌──────────┐  ┌──────┐  ┌────────┐  ┌─────────┐  │        │
│  │  │PostgreSQL│  │Redis │  │ Mayan  │  │ Ollama  │  │        │
│  │  │  :5432   │  │:6379 │  │ EDMS   │  │   AI    │  │        │
│  │  └──────────┘  └──────┘  └────────┘  └─────────┘  │        │
│  └──────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

### Network Topology

- **Frontend Network (Bridge)** - Public-facing services accessible from host
  - Frontend (React + NGINX)
  - Backend API (FastAPI)
  - Keycloak (SSO)
  
- **Backend Network (Internal)** - Isolated internal services
  - PostgreSQL (Database)
  - Redis (Cache/Sessions)
  - Mayan EDMS (Document Management)
  - Ollama (AI Inference)

### Data Flow

1. **User Authentication**
   ```
   User → Frontend → Keycloak → JWT Token → Frontend
   ```

2. **Document Upload**
   ```
   User → Frontend → Backend API → Mayan EDMS → PostgreSQL
   ```

3. **AI Analysis**
   ```
   User → Frontend → Backend API → Ollama → AI Response
   ```

---

## 🛠️ Technology Stack

### Frontend
| Technology | Version | Purpose | Why Chosen |
|------------|---------|---------|------------|
| **React** | 19.2 | UI Framework | Modern, component-based architecture with excellent ecosystem |
| **TypeScript** | 5.9 | Type Safety | Catch errors at compile-time, better IDE support |
| **Vite** | 7.2 | Build Tool | Lightning-fast HMR, optimized builds, modern dev experience |
| **NGINX** | Latest | Web Server | Production-grade static file serving, reverse proxy capabilities |

### Backend
| Technology | Version | Purpose | Why Chosen |
|------------|---------|---------|------------|
| **Python** | 3.11 | Language | Excellent async support, rich ecosystem for AI/ML |
| **FastAPI** | 0.109 | Web Framework | High performance, automatic API docs, async-first design |
| **SQLAlchemy** | 2.0 | ORM | Mature, powerful ORM with async support |
| **Alembic** | 1.13 | Migrations | Industry standard for database versioning |
| **Pydantic** | 2.5 | Validation | Type-safe data validation, perfect FastAPI integration |
| **Uvicorn** | 0.27 | ASGI Server | High-performance async server |

### Infrastructure
| Technology | Version | Purpose | Why Chosen |
|------------|---------|---------|------------|
| **Docker** | Latest | Containerization | Consistent environments, easy deployment |
| **Docker Compose** | Latest | Orchestration | Simple multi-container management |
| **PostgreSQL** | 15 | Database | Robust, ACID-compliant, excellent for document metadata |
| **Redis** | 7 | Cache/Queue | In-memory speed, pub/sub, session management |

### Services
| Technology | Version | Purpose | Why Chosen |
|------------|---------|---------|------------|
| **Keycloak** | 23.0 | SSO/Auth | Enterprise SSO, OIDC/SAML support, user federation |
| **Mayan EDMS** | Latest | Document Management | Open-source DMS with OCR, workflows, metadata |
| **Ollama** | Latest | AI Inference | Local LLM inference, privacy-focused, no external API costs |

### Why This Architecture?

1. **Microservices** - Each service is independently scalable and maintainable
2. **Security** - Network isolation prevents unauthorized access to sensitive services
3. **Performance** - Redis caching, async Python, optimized frontend builds
4. **Developer Experience** - Hot reload, type safety, comprehensive logging
5. **Cost Effective** - Local AI inference, open-source stack, no vendor lock-in
6. **Privacy** - All data stays on-premises, no external API calls for AI

---

## ✨ Features

### Current Features (Implemented)

- ✅ **Containerized Infrastructure** - Full Docker Compose setup
- ✅ **Health Monitoring** - Health check endpoints for all services
- ✅ **API Documentation** - Auto-generated Swagger/OpenAPI docs
- ✅ **Database Migrations** - Alembic-based schema versioning
- ✅ **Logging System** - Comprehensive structured logging
- ✅ **CORS Configuration** - Secure cross-origin resource sharing
- ✅ **Environment Management** - Flexible configuration via environment variables

### In Development

- 🚧 **User Authentication** - Keycloak integration with JWT
- 🚧 **Document Upload** - Multi-format document ingestion
- 🚧 **Document Search** - Full-text search with metadata filtering
- 🚧 **AI Chat Interface** - Document Q&A with Ollama
- 🚧 **Role-Based Access** - Granular permissions system

### Planned Features

- 📋 **Document Versioning** - Track document history
- 📋 **Workflow Automation** - Approval workflows
- 📋 **Audit Logging** - Comprehensive activity tracking
- 📋 **Batch Processing** - Bulk document operations
- 📋 **Advanced AI** - Document summarization, entity extraction
- 📋 **Mobile App** - React Native mobile client

---

## 🚀 Quick Start

### Prerequisites

- **Docker Desktop** - [Download](https://www.docker.com/products/docker-desktop)
- **8GB+ RAM** - For running all services
- **50GB+ Disk Space** - For Docker images and data
- **Available Ports** - 3000, 8000, 8001, 8082, 11434

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/secure-document-vault.git
   cd secure-document-vault
   ```

2. **Configure environment**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit with your secure passwords
   notepad .env  # Windows
   nano .env     # Linux/Mac
   ```

3. **Start services**
   ```bash
   # Start all services
   docker-compose up -d
   
   # View logs
   docker-compose logs -f
   
   # Check status
   docker-compose ps
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/api/v1/docs
   - Keycloak Admin: http://localhost:8082
   - Mayan EDMS: http://localhost:8001

### First-Time Setup

1. **Configure Keycloak**
   - Visit http://localhost:8082
   - Login with admin/admin (change in production!)
   - Create a new realm: `documentvault`
   - Create clients for frontend and backend

2. **Verify Services**
   ```bash
   # Backend health
   curl http://localhost:8000/health
   
   # Ollama status
   curl http://localhost:11434/api/tags
   
   # Keycloak health
   curl http://localhost:8082/health/ready
   ```

---

## 📁 Project Structure

```
secure-document-vault/
├── backend/                    # Python FastAPI Backend
│   ├── app/
│   │   ├── api/v1/            # API routes
│   │   │   ├── api.py         # Router aggregation
│   │   │   └── endpoints/     # Endpoint modules
│   │   │       ├── health.py  # Health checks
│   │   │       ├── documents.py
│   │   │       └── chat.py
│   │   ├── core/              # Core functionality
│   │   │   ├── config.py      # Configuration
│   │   │   ├── database.py    # Database setup
│   │   │   └── logger.py      # Logging
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   └── services/          # Business logic
│   │       ├── keycloak.py    # SSO integration
│   │       ├── mayan.py       # Document management
│   │       └── ollama.py      # AI integration
│   ├── alembic/               # Database migrations
│   ├── main.py                # Application entry point
│   ├── Dockerfile             # Container definition
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── App.tsx            # Main application
│   │   ├── main.tsx           # Entry point
│   │   └── assets/            # Static assets
│   ├── Dockerfile             # Multi-stage build
│   ├── nginx.conf             # NGINX configuration
│   ├── package.json           # Node dependencies
│   └── vite.config.ts         # Vite configuration
│
├── init-scripts/              # Database initialization
│   └── 01-init-databases.sql  # Create databases
│
├── storage/                   # Local file storage
│   └── documents/             # Document files
│
├── docker-compose.yml         # Service orchestration
├── .env.example               # Environment template
├── .gitignore                 # Git exclusions
├── README.md                  # This file
├── README-DOCKER.md           # Docker deployment guide
└── PROJECT-SUMMARY.md         # Detailed project summary
```

---

## 🔧 Services

### Backend API (Port 8000)

**FastAPI** application providing REST API for all operations.

**Key Features:**
- Async request handling
- Automatic API documentation
- JWT authentication (in development)
- Service orchestration (Keycloak, Mayan, Ollama)

**Endpoints:**
- `GET /health` - Health check
- `GET /api/v1/docs` - Swagger UI
- `GET /api/v1/documents` - Document operations
- `POST /api/v1/chat` - AI chat interface

### Frontend (Port 3000)

**React + TypeScript** SPA with production NGINX server.

**Features:**
- Modern component architecture
- TypeScript type safety
- Vite HMR for development
- Optimized production builds

### Keycloak (Port 8082)

**SSO Authentication** server for centralized identity management.

**Capabilities:**
- User management
- Role-based access control
- OAuth 2.0 / OpenID Connect
- Social login integration

**Default Credentials:**
- Username: `admin`
- Password: `admin` (⚠️ Change in production!)

### Mayan EDMS (Port 8001)

**Document Management System** with advanced features.

**Features:**
- OCR processing
- Full-text search
- Metadata management
- Workflow automation
- Document versioning

### Ollama (Port 11434)

**Local AI Inference** engine for privacy-focused AI operations.

**Capabilities:**
- LLM inference (llama3.1)
- No external API calls
- GPU acceleration support
- Model persistence

**Pre-loaded Models:**
- llama3.1 (auto-pulled on startup)

### PostgreSQL (Internal)

**Database** for all services.

**Databases:**
- `keycloak` - Keycloak data
- `mayan` - Mayan EDMS data
- `backend` - Application data

### Redis (Internal)

**Cache and Message Broker**

**Usage:**
- Session management
- API response caching
- Celery task queue (Mayan)
- Pub/sub messaging

---

## 💻 Development

### Local Development

1. **Backend Development**
   ```bash
   # Hot reload is enabled by default
   docker-compose logs -f backend
   
   # Edit files in backend/app/
   # Changes are reflected immediately
   ```

2. **Frontend Development**
   ```bash
   # Rebuild frontend after changes
   docker-compose up -d --build frontend
   
   # Or develop locally
   cd frontend
   npm install
   npm run dev
   ```

3. **Database Migrations**
   ```bash
   # Create migration
   docker-compose exec backend alembic revision --autogenerate -m "description"
   
   # Apply migrations
   docker-compose exec backend alembic upgrade head
   ```

### Testing

```bash
# Backend tests (when implemented)
docker-compose exec backend pytest

# Frontend tests (when implemented)
cd frontend && npm test
```

### Debugging

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Access container shell
docker-compose exec backend bash
docker-compose exec frontend sh
```

---

## 📚 API Documentation

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

### Example API Calls

```bash
# Health check
curl http://localhost:8000/health

# Get documents (when implemented)
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/documents

# Upload document (when implemented)
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -F "file=@document.pdf" \
  http://localhost:8000/api/v1/documents/upload
```

---

## 🔐 Security

### Network Security

- ✅ **Network Isolation** - Backend services not exposed to host
- ✅ **Internal Communication** - Services communicate via Docker DNS
- ✅ **No External Database Access** - PostgreSQL/Redis are internal-only

### Authentication & Authorization

- 🚧 **SSO via Keycloak** - Centralized authentication
- 🚧 **JWT Tokens** - Stateless authentication
- 🚧 **Role-Based Access** - Granular permissions

### Data Security

- ✅ **Environment Variables** - Secrets not in code
- ✅ **Volume Encryption** - Docker volume encryption support
- 📋 **TLS/SSL** - HTTPS for production (planned)

### Best Practices

1. **Change Default Passwords** - Update all passwords in `.env`
2. **Use Strong Secrets** - Generate secure random keys
3. **Regular Updates** - Keep Docker images updated
4. **Audit Logging** - Monitor access patterns (planned)

---

## 🗺️ Roadmap

### Phase 1: Authentication (Current)
- [ ] Keycloak realm configuration
- [ ] JWT middleware implementation
- [ ] Protected route decorators
- [ ] Login/logout endpoints
- [ ] User registration

### Phase 2: Document Management
- [ ] Document upload API
- [ ] Metadata extraction
- [ ] Full-text search
- [ ] Document versioning
- [ ] Access control

### Phase 3: AI Integration
- [ ] Document analysis endpoints
- [ ] Batch processing
- [ ] Streaming responses
- [ ] Custom prompts
- [ ] Result caching

### Phase 4: Frontend Development
- [ ] Authentication UI
- [ ] Document upload interface
- [ ] Document viewer
- [ ] AI chat interface
- [ ] Admin dashboard

### Phase 5: Production Readiness
- [ ] Unit tests
- [ ] Integration tests
- [ ] Performance optimization
- [ ] Monitoring & alerting
- [ ] Production deployment guide

---

## 🤝 Contributing

Contributions are welcome! This project is under active development.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards

- **Python**: Follow PEP 8, use type hints
- **TypeScript**: Use strict mode, proper typing
- **Commits**: Use conventional commits format
- **Documentation**: Update README for significant changes

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

- **Documentation**: See [PROJECT-SUMMARY.md](PROJECT-SUMMARY.md) for detailed setup
- **Docker Guide**: See [README-DOCKER.md](README-DOCKER.md) for deployment
- **Issues**: [GitHub Issues](https://github.com/yourusername/secure-document-vault/issues)

---

## 🙏 Acknowledgments

- **FastAPI** - Modern Python web framework
- **React** - UI library
- **Keycloak** - Identity and access management
- **Mayan EDMS** - Document management system
- **Ollama** - Local AI inference
- **Docker** - Containerization platform

---

<div align="center">

**⚠️ This project is under active development**

Built with ❤️ using modern open-source technologies

</div>

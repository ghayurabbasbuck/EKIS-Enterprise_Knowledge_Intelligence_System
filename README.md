# EKIS Backend — Enterprise Knowledge Intelligence System

> **High-performance, asynchronous REST API & RAG Engine** powering enterprise semantic document search, multi-tenant RBAC access control, and grounded conversational intelligence using FastAPI, PostgreSQL + pgvector, LangChain, and Google Gemini.

---

## Table of Contents

1. [Architectural Overview](#architectural-overview)
2. [Core Capabilities](#core-capabilities)
3. [Technology Stack](#technology-stack)
4. [Backend Directory Structure](#backend-directory-structure)
5. [Prerequisites](#prerequisites)
6. [Getting Started](#getting-started)
   - [1. Infrastructure Provisioning (PostgreSQL + pgvector)](#1-infrastructure-provisioning-postgresql--pgvector)
   - [2. Virtual Environment & Dependencies](#2-virtual-environment--dependencies)
   - [3. Environment Configuration](#3-environment-configuration)
   - [4. Schema Migrations (Alembic)](#4-schema-migrations-alembic)
   - [5. Superuser Creation (CLI)](#5-superuser-creation-cli)
   - [6. Running the API Service](#6-running-the-api-service)
7. [Environment Variables Reference](#environment-variables-reference)
8. [RAG Pipeline Deep Dive](#rag-pipeline-deep-dive)
9. [API Specification & Endpoints](#api-specification--endpoints)
10. [Security & Enterprise Hardening](#security--enterprise-hardening)
11. [Testing & Quality Assurance](#testing--quality-assurance)
12. [Docker Deployment](#docker-deployment)

---

## Architectural Overview

EKIS Backend implements a strictly layered, asynchronous architecture:

```
                      ┌─────────────────────────────────────────┐
                      │            HTTP / REST Clients          │
                      │       (React Web App, SDKs, CLI)       │
                      └────────────────────┬────────────────────┘
                                           │
                                           │  JSON / JWT Bearer
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                     FASTAPI CORE                                       │
│                                                                                        │
│   ├── SecurityHeadersMiddleware (HSTS, X-Frame-Options, NoSniff, ReferrerPolicy)       │
│   ├── CORSMiddleware (Configurable Origin Whitelist)                                   │
│   └── Global Exception Handlers (Standardized JSON Error Payloads)                     │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                             API ROUTING LAYER (/api/v1)                                │
│                                                                                        │
│   /health_check      /auth              /chat              /documents                  │
│   /search            /analytics         /users             /companies                  │
│   /departments                                                                         │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   SERVICES LAYER                                       │
│                                                                                        │
│   ├── AuthService: Argon2 hashing + PyJWT issuer/audience binding                      │
│   ├── DocumentPipeline: Ingestion, parsing (PDF/TXT/CSV/DOCX), metadata tagging        │
│   ├── ChunkingService: Recursive text splitting                                        │
│   ├── EmbeddingService: SentenceTransformers ('all-MiniLM-L6-v2') on CPU/GPU           │
│   ├── RetrievalService: Cosine distance vector retrieval via pgvector                  │
│   ├── RAGService: Strict grounding prompt assembly + Google Gemini orchestration       │
│   └── AnalyticsService: Aggregations, topic extraction, and query usage analytics      │
└──────────────────────┬─────────────────────────────────────────┬───────────────────────┘
                       │                                         │
                       ▼                                         ▼
         ┌──────────────────────────┐             ┌──────────────────────────────┐
         │     DATABASE LAYER       │             │       EXTERNAL AI APIS       │
         │                          │             │                              │
         │ PostgreSQL 16 + pgvector │             │ Google Gemini (LLM)          │
         │ (SQLAlchemy AsyncEngine) │             │ HuggingFace (Model Hub)      │
         └──────────────────────────┘             └──────────────────────────────┘
```

---

## Core Capabilities

- **Strict Multi-Tenant Isolation:** Complete contextual separation by `company_id` and `department_id`. Ingestion, search, and retrieval pipelines enforce boundaries directly at the database query layer.
- **RAG Without Hallucinations:** Questions are resolved exclusively using context fetched from authorized documents. The system prompt forces the LLM to explicitly report when information is absent.
- **Asynchronous Ingestion Pipeline:** Accepts PDF, TXT, CSV, and DOCX files up to 50 MB, normalizes text, splits into contextual chunks, embeds with local/hosted models, and persists to pgvector.
- **Role-Based Access Control (RBAC):** Granular permissions supporting `SUPERUSER`, `ADMIN`, and standard tenant users.
- **Full Observability & Analytics:** Tracks query latency, request frequency, per-department utilization, and keyword trends over customizable time windows.

---

## Technology Stack

| Component | Technology | Specification / Role |
|---|---|---|
| **Web Framework** | FastAPI | `0.115+` — ASGI async REST framework |
| **ASGI Server** | Uvicorn | `0.30+` — High-concurrency async server |
| **Language Runtime**| Python | `3.11` (Strictly pinned `>=3.11,<3.12`) |
| **Relational Database** | PostgreSQL 16 | Relational entities, foreign keys, constraints |
| **Vector Engine** | pgvector | `0.3+` — HNSW / IVFFlat vector indexing & cosine similarity |
| **Database Driver** | asyncpg | High-performance asynchronous PostgreSQL client |
| **ORM / Query Builder**| SQLAlchemy | `2.0+` Async with `select()` and declarative mappings |
| **Migrations** | Alembic | Version-controlled database schema management |
| **LLM Orchestration** | LangChain Core | `0.3+` — Prompt templating & pipeline execution |
| **LLM Provider** | Google Gemini | `langchain-google-genai` (Gemini Pro models) |
| **Embeddings** | HuggingFace | `sentence-transformers/all-MiniLM-L6-v2` |
| **Password Security** | pwdlib[argon2] | Modern memory-hard hashing standard |
| **Token Auth** | PyJWT | `2.9+` — Cryptographically signed JSON Web Tokens |
| **Config Validation** | Pydantic v2 | `pydantic-settings` strictly validated environment loader |
| **Linting & Format** | Ruff | Lightning-fast Python linter and formatter |
| **Test Runner** | pytest | `pytest-asyncio` with `asyncio_mode = "auto"` |

---

## Backend Directory Structure

```
backend/
├── alembic/                         # Database schema migrations
│   ├── versions/                    # Versioned migration scripts
│   └── env.py                       # Async Alembic execution environment
├── app/
│   ├── api/                         # Endpoint definitions & routing
│   │   ├── v1/                      # Version 1 API routes
│   │   │   ├── analytics.py         # Dashboards, trends, popular topics
│   │   │   ├── auth.py              # Login and registration
│   │   │   ├── chat.py              # Conversational RAG queries
│   │   │   ├── companies.py         # Multi-tenant company management
│   │   │   ├── departments.py       # Department provisioning
│   │   │   ├── document.py          # Upload, status, deletion
│   │   │   ├── router.py            # Master v1 API aggregator
│   │   │   ├── search.py            # Direct semantic vector search
│   │   │   └── users.py             # User administration & RBAC
│   │   └── ...
│   ├── core/                        # Global configurations & system setup
│   │   ├── config.py                # Pydantic Settings instance
│   │   ├── database.py              # Async engine & session factories
│   │   ├── exceptions.py            # Global exception handling & error mappers
│   │   ├── logging.py               # Structured log formatting
│   │   ├── roles.py                 # RBAC role definitions
│   │   └── security.py              # Cryptographic password hashing & checks
│   ├── dependencies/                # Reusable FastAPI dependency injections
│   │   ├── auth.py                  # JWT validation & current user context
│   │   └── ...
│   ├── models/                      # SQLAlchemy ORM database models
│   │   ├── base.py                  # Declarative base class
│   │   ├── company.py               # Enterprise organization entity
│   │   ├── department.py            # Departmental segregation entity
│   │   ├── document.py              # Document metadata & tracking
│   │   ├── document_chunk.py        # Segmented text chunks
│   │   ├── embedding.py             # Vector records (pgvector mapped)
│   │   ├── query_log.py             # Audit trail & analytics metrics
│   │   └── user.py                  # User credentials and RBAC roles
│   ├── repositories/                # Clean data access layer abstractions
│   ├── schemas/                     # Pydantic validation request/response schemas
│   ├── services/                    # Business logic & AI workflow domain
│   │   ├── analytics_service.py     # Aggregation algorithms & trends
│   │   ├── auth_service.py          # Session and JWT token generation
│   │   ├── chunking.py              # Chunk splitting logic
│   │   ├── document_pipeline.py     # End-to-end ingestion orchestrator
│   │   ├── document_processor.py    # Multi-format document parsers
│   │   ├── embedding_service.py     # SentenceTransformer embeddings engine
│   │   ├── llm_service.py           # Gemini Chat model interface
│   │   ├── rag_service.py           # Grounding prompts & context synthesis
│   │   └── retrieval_service.py     # Cosine vector retrieval with isolation
│   ├── utils/                       # Generic helpers
│   └── main.py                      # FastAPI application factory & lifespan
├── scripts/
│   └── create_superuser.py          # Interactive CLI for creating root admin
├── storage/                         # Local uploaded file storage staging
├── tests/                           # Async test suite
│   ├── test_health.py               # Service and DB connectivity tests
│   └── test_multitenancy_rbac.py    # Multi-tenancy isolation validation
├── alembic.ini                      # Alembic configuration
├── Dockerfile                       # Production container build definition
├── docker-compose.yml               # PostgreSQL + pgvector configuration
├── pyproject.toml                   # Project metadata, dependencies, and tooling config
└── requirements.txt                 # Legacy reference dependency manifest
```

---

## Prerequisites

Ensure the following tools are installed on your host system:

- **Python 3.11** (Required: `>=3.11,<3.12`)
- **Docker Desktop** or **Docker Engine** (with Compose v2)
- **Google Gemini API Key** ([Google AI Studio](https://aistudio.google.com/app/apikey))
- **Hugging Face Access Token** *(Optional, for higher rate limits or private models)*

---

## Getting Started

### 1. Infrastructure Provisioning (PostgreSQL + pgvector)

Start the containerized vector database:

```bash
cd backend
docker compose up -d
```

Verify that the container is healthy:

```bash
docker ps --filter "name=ekis-postgres"
```

The database initializes with the `vector` extension enabled on port `5432`.

### 2. Virtual Environment & Dependencies

Initialize an isolated Python 3.11 virtual environment and install dependencies in editable mode:

#### Windows (PowerShell)
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

#### Linux / macOS
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
```

### 3. Environment Configuration

Create your `.env` configuration file from the template:

```bash
cp .env.example .env
```

Open `.env` and verify your settings (see [Environment Variables Reference](#environment-variables-reference) below).

### 4. Schema Migrations (Alembic)

Execute database migrations to generate tables, relational constraints, and vector columns:

```bash
alembic upgrade head
```

### 5. Superuser Creation (CLI)

Run the interactive administrative CLI script to create your initial superuser:

```bash
python scripts/create_superuser.py
```

Follow the prompts to configure the email, full name, and password.

### 6. Running the API Service

Start the local development server with auto-reload:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- **Base URL:** `http://127.0.0.1:8000`
- **Health Check:** `http://127.0.0.1:8000/api/v1/health_check`
- **Swagger Documentation:** `http://127.0.0.1:8000/docs` *(development mode only)*
- **ReDoc:** `http://127.0.0.1:8000/redoc` *(development mode only)*

---

## Environment Variables Reference

| Variable | Type | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | `string` | *(Required)* | Async database DSN: `postgresql+asyncpg://user:pass@host:5432/dbname` |
| `JWT_SECRET_KEY` | `string` | *(Required)* | High-entropy secret key for signing JWTs (HMAC-SHA256) |
| `JWT_ALGORITHM` | `string` | `HS256` | Algorithm used for token generation |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `int` | `60` | Lifespan of generated access tokens in minutes |
| `JWT_ISSUER` | `string` | `ekis-backend` | Claims validator: rejects tokens issued by foreign services |
| `JWT_AUDIENCE` | `string` | `ekis-client` | Claims validator: targets designated clients |
| `GEMINI_API_KEY` | `string` | *(Required)* | Google Gemini AI API key |
| `HUGGINGFACE_API_TOKEN` | `string` | `""` | Hugging Face user access token for model downloads |
| `EMBEDDING_MODEL` | `string` | `sentence-transformers/all-MiniLM-L6-v2` | Model identifier for HuggingFace embeddings |
| `APP_NAME` | `string` | `EKIS Backend` | Identifier used in application metadata |
| `APP_ENV` | `string` | `development` | Deployment environment (`development`, `staging`, `production`) |
| `DEBUG` | `bool` | `false` | Enables debug traces (disable in production) |
| `LOG_LEVEL` | `string` | `INFO` | Logging threshold (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `MAX_UPLOAD_SIZE_MB` | `int` | `50` | Maximum allowed payload size for document uploads |
| `CORS_ORIGINS` | `string` | `http://localhost:3000` | Comma-delimited list of permitted CORS origins |
| `API_V1_PREFIX` | `string` | `/api/v1` | URL prefix for version 1 API routes |

---

## RAG Pipeline Deep Dive

```
1. Ingestion Stage
   File Upload (PDF/TXT/CSV/DOCX)
       │
       ▼
   Document Processor (Extract text & page streams)
       │
       ▼
   Metadata Injection (Attach document_id, department_id, filename)
       │
       ▼
   Text Splitter (Recursive chunking: chunk_size=800, overlap=100)
       │
       ▼
   HuggingFace Embedding Engine (Vectorize chunks to float32 dimensions)
       │
       ▼
   pgvector Storage (Write Document, DocumentChunk & Embedding entities)

2. Query & Generation Stage
   User Query + JWT Token Context
       │
       ▼
   Filter Resolution (Extract company_id & department_id from auth context)
       │
       ▼
   Query Vectorization (Generate embedding via SentenceTransformers)
       │
       ▼
   Cosine Distance Retrieval (Query pgvector with strict tenant/dept SQL WHERE)
       │
       ▼
   Context Assembled (Ordered by similarity score, bounded by Top-K)
       │
       ▼
   Grounded Prompt Synthesis (Strict instructions: no assumptions, cite sources)
       │
       ▼
   Google Gemini Invocations (Streaming / synchronous response generation)
       │
       ▼
   Audit Logging (Record response time, query, and citations to QueryLog)
```

---

## API Specification & Endpoints

All application routes are served under prefix `/api/v1`.

### Health Check

```http
GET /api/v1/health_check
```
Checks database connectivity and confirms system status.
- **Response:** `200 OK`
```json
{
  "status": "ok",
  "service": "ekis-backend",
  "database": "Success"
}
```

---

### Authentication

```http
POST /api/v1/auth/register
POST /api/v1/auth/login
```
- **Login Payload:** `{"email": "user@company.com", "password": "password123"}`
- **Login Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

### Conversational RAG & Search

```http
POST /api/v1/chat/query
```
Executes a grounded RAG query scoped to the caller's organizational access.
- **Payload:**
```json
{
  "question": "What is our company's refund policy?",
  "top_k": 5
}
```
- **Response:** Returns synthesized answer along with list of `RetrievedChunk` references (filenames, relevance score, chunk indices).

```http
POST /api/v1/search/semantic
```
Direct vector retrieval returning raw ranked chunks without LLM synthesis.

---

### Document Management

```http
POST   /api/v1/documents/upload    # multipart/form-data: file, department_id
GET    /api/v1/documents/list      # Lists documents scoped to company/department
DELETE /api/v1/documents/{id}      # Cascades deletion across chunks & embeddings
```

---

### Analytics & Reporting

```http
GET /api/v1/analytics/dashboard?days=30
```
Returns comprehensive metrics:
- Overall document count & query volume
- Mean response latency (`average_response_time_ms`)
- Daily query volume trends over `days`
- Department query volume breakdown
- Top-10 popular topics extracted from natural language queries

---

### Administration (RBAC Protected)

```http
GET    /api/v1/admin/users          # Superuser/Admin user listing
GET    /api/v1/companies            # Company listing & management
POST   /api/v1/companies
GET    /api/v1/departments          # Department listing & management
POST   /api/v1/departments
```

---

## Security & Enterprise Hardening

1. **Password Encryption:** Passwords are hashed using the **Argon2** algorithm through `pwdlib`, featuring resistant memory-hard properties against brute-force attacks.
2. **JWT Claims Binding:** Generated tokens are signed using HMAC-SHA256 and strictly embed `iss` (issuer) and `aud` (audience) claims. Any token lacking matching claims is rejected before reaching controller logic.
3. **HTTP Security Headers Middleware:** Applied to every outbound response:
   - `X-Content-Type-Options: nosniff`
   - `X-Frame-Options: DENY`
   - `X-XSS-Protection: 1; mode=block`
   - `Strict-Transport-Security: max-age=31536000; includeSubDomains`
   - `Referrer-Policy: strict-origin-when-cross-origin`
4. **Information Leakage Prevention:** In production (`APP_ENV=production`), interactive API documentation routes (`/docs`, `/redoc`, `/openapi.json`) are disabled automatically.
5. **Multi-Tenant Isolation:** Retrieval logic explicitly incorporates company and department IDs directly into SQL queries to prevent multi-tenant data contamination.

---

## Testing & Quality Assurance

### Running Unit & Integration Tests

The test suite validates health status, database operations, and multi-tenant access control:

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run a specific test module
pytest tests/test_multitenancy_rbac.py
```

### Linting and Code Formatting

We use **Ruff** for high-speed static analysis and linting:

```bash
# Check for lint violations
ruff check .

# Automatically apply safe fixes
ruff check . --fix

# Format code according to repository standards
ruff format .
```

---

## Docker Deployment

### Building the Production Image

The backend includes a multistage-ready production `Dockerfile`:

```bash
# Build Docker image
docker build -t ekis-backend:latest .
```

### Running the Container

```bash
docker run -d \
  --name ekis-backend-service \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql+asyncpg://postgres:123@host.docker.internal:5432/ekis" \
  -e JWT_SECRET_KEY="<strong-random-key>" \
  -e GEMINI_API_KEY="<your-gemini-key>" \
  -e APP_ENV="production" \
  ekis-backend:latest
```

---

*EKIS Backend — Engineered for secure enterprise retrieval and conversational intelligence.*

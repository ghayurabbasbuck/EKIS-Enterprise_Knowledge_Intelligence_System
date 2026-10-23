# EKIS Frontend — Enterprise Knowledge Intelligence System

> **Modern, reactive enterprise web interface** built with React 19, Vite, and Lucide Icons. Provides corporate users with conversational AI document chat, semantic search, document ingestion workflows, real-time analytics visualizations, and multi-tenant administrative controls.

---

## Table of Contents

1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Prerequisites](#prerequisites)
6. [Getting Started](#getting-started)
   - [1. Installation](#1-installation)
   - [2. Environment Configuration](#2-environment-configuration)
   - [3. Running the Development Server](#3-running-the-development-server)
   - [4. Production Build & Preview](#4-production-build--preview)
7. [Application Architecture](#application-architecture)
   - [State & Authentication Context](#state--authentication-context)
   - [Axios HTTP Client & Interceptors](#axios-http-client--interceptors)
   - [Route Protection & RBAC Guards](#route-protection--rbac-guards)
8. [Page Directory & Feature Modules](#page-directory--feature-modules)
9. [API Integration Reference](#api-integration-reference)
10. [Document Upload Specifications](#document-upload-specifications)
11. [Styling & UI Guidelines](#styling--ui-guidelines)
12. [Troubleshooting & FAQ](#troubleshooting--faq)

---

## Overview

EKIS Frontend provides an intuitive, high-performance user experience for organizations managing internal knowledge bases. It connects seamlessly with the FastAPI backend over REST APIs, authenticating requests via JSON Web Tokens (JWT) and presenting grounded RAG responses, citations, interactive trend charts, and role-restricted management dashboards.

---

## Key Features

- **Conversational RAG Assistant (`/chat`):** Chat directly with enterprise documents. Responses cite source files and relevance scores with strict anti-hallucination indicators.
- **Semantic Vector Search (`/search`):** Query document knowledge via vector similarity directly, inspecting matched snippets and cosine distances.
- **Document Management Hub (`/documents`):** View processing status (`processing`, `processed`, `failed`), manage departmental files, and upload new documents via a drag-and-drop modal.
- **Analytics Dashboard (`/`):** Visualizes system utilization, query volume trends, department usage, and top discussion topics using Recharts.
- **Role-Based Access Control (RBAC):** Hierarchical view states supporting `SUPERUSER`, `ADMIN`, and `EMPLOYEE` roles with fine-grained route guards.
- **Administrative Suites (`/admin/*`):** User management, role elevation, activation toggles, and department structure configuration.
- **Zero-Friction Dev Experience:** Built-in Vite reverse-proxy eliminates CORS issues during local development.

---

## Technology Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **Core Framework** | React | `^19.0.0` | UI component architecture and reactivity |
| **DOM Engine** | React DOM | `^19.0.0` | React web rendering engine |
| **Build Tool & Bundler** | Vite | `^6.1.0` | Instant HMR development server & production bundler |
| **Routing** | React Router DOM | `^7.1.5` | Declarative client-side routing & nested route protection |
| **HTTP Client** | Axios | `^1.8.4` | Promise-based HTTP client with request/response interceptors |
| **Data Visualization** | Recharts | `^3.10.1` | Composable SVG charts for analytical trends and metrics |
| **Iconography** | Lucide React | `^0.468.0` | Clean, modern iconography system |
| **Styling** | Vanilla CSS | Modern CSS | Modular design system with dark/light corporate palettes |

---

## Project Structure

```
frontend/
├── public/                          # Static assets and favicon
├── src/
│   ├── api/                         # Axios client instances and endpoint abstractions
│   │   ├── admin.js                 # Admin user and permissions APIs
│   │   ├── analytics.js             # Dashboard metrics and telemetry APIs
│   │   ├── auth.js                  # Login and user registration APIs
│   │   ├── chat.js                  # RAG conversational query APIs
│   │   ├── client.js                # Base Axios instance, interceptors, error parsers
│   │   ├── departments.js           # Department management APIs
│   │   ├── documents.js             # Upload, listing, and deletion APIs
│   │   └── search.js                # Direct semantic search APIs
│   ├── auth/                        # RBAC mappings and permission policies
│   │   └── permissions.js           # Role normalization (SUPERUSER, ADMIN, EMPLOYEE)
│   ├── components/                  # Reusable presentation and guard components
│   │   ├── AdminRoute.jsx           # Guard component for ADMIN / SUPERUSER routes
│   │   ├── AppShell.jsx             # Top bar, sidebar navigation, and user menu layout
│   │   ├── EmptyState.jsx           # Standardized zero-data placeholders
│   │   ├── ErrorState.jsx           # User-facing error notification boxes
│   │   ├── LoadingState.jsx         # Async loading spinners and skeletons
│   │   ├── PermissionRoute.jsx      # Fine-grained capability guard (e.g., 'use_ai')
│   │   ├── ProtectedRoute.jsx       # Authentication guard for authenticated sessions
│   │   └── UploadModal.jsx          # File drag-and-drop upload modal with progress
│   ├── context/                     # Global state providers
│   │   └── AuthContext.jsx          # User state, token lifecycle, and session management
│   ├── pages/                       # Application view controllers
│   │   ├── AdminUsers.jsx           # User management, role assignment, status toggling
│   │   ├── Analytics.jsx            # Detailed query logs and department utilization
│   │   ├── Chat.jsx                 # Conversational AI assistant interface
│   │   ├── Dashboard.jsx            # KPI cards and Recharts analytical trends
│   │   ├── Documents.jsx            # Document repository table and status indicators
│   │   ├── Login.jsx                # Corporate authentication portal
│   │   ├── Register.jsx             # New employee/tenant registration portal
│   │   ├── Search.jsx               # Vector semantic query tester
│   │   ├── Settings.jsx             # User preferences and profile view
│   │   └── departments.jsx          # Department directory & management
│   ├── App.jsx                      # Route manifest and providers orchestration
│   ├── main.jsx                     # Application bootstrap entry point
│   └── styles.css                   # Global stylesheet and UI design tokens
├── .env.example                     # Environment template
├── index.html                       # HTML5 entry template
├── package.json                     # Dependency definitions and scripts
└── vite.config.js                   # Vite configuration and backend API proxy setup
```

---

## Prerequisites

Ensure the following tools are installed:

- **Node.js**: `18.0.0` or higher (Node 20+ recommended)
- **npm**: `9.0.0` or higher (bundled with Node.js)
- **EKIS Backend**: Running locally on `http://127.0.0.1:8000` (see `backend/README.md`)

---

## Getting Started

### 1. Installation

Navigate to the frontend directory and install dependencies:

```bash
cd EKIS_React_Frontend/ekis-react-frontend/frontend
npm install
```

### 2. Environment Configuration

Copy the example environment file:

```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# Linux / macOS
cp .env.example .env
```

The default `.env` is pre-configured for local development with Vite's proxy:

```env
VITE_API_BASE_URL=/api/v1
```

> **Why `/api/v1`?**  
> Vite's development server proxies requests beginning with `/api` to `http://127.0.0.1:8000`. This ensures browser requests remain same-origin, avoiding CORS preflight failures.

### 3. Running the Development Server

Start Vite's live-reloading development server:

```bash
npm run dev
```

- **Local URL:** `http://127.0.0.1:5173/`
- Vite will automatically proxy API calls to the running backend service.

### 4. Production Build & Preview

Compile and minify the application for production deployment:

```bash
# Generate production bundle in dist/
npm run build

# Preview production build locally
npm run preview
```

---

## Application Architecture

### State & Authentication Context

Authentication state is managed globally through `AuthContext.jsx`:

- **Token Storage:** JWT tokens are persisted in `localStorage` under key `ekis_token`.
- **User Identity:** User profile data is stored under key `ekis_user`.
- **Automatic Session Expiry:** If the backend returns `401 Unauthorized`, an `ekis:logout` event triggers automatically, clearing storage and redirecting the user to `/login`.

### Axios HTTP Client & Interceptors

All network communications pass through a centralized Axios instance in `src/api/client.js`:

```javascript
// Automatically attaches Bearer token from localStorage
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("ekis_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

- **Multipart Form Boundaries:** The interceptor detects `FormData` payloads and automatically strips default `Content-Type: application/json` headers, allowing the browser to calculate the correct boundary string.
- **Normalized Error Messages:** Includes `getApiErrorMessage(error)` to parse FastAPI Pydantic validation errors (array format, location path, and nested strings) into human-readable notifications.

### Route Protection & RBAC Guards

The application implements three levels of security guards:

1. `<ProtectedRoute>`: Blocks unauthenticated sessions and redirects to `/login`.
2. `<AdminRoute>`: Restricts access to users holding `ADMIN` or `SUPERUSER` privileges.
3. `<PermissionRoute permission="...">`: Evaluates granular capabilities (e.g., verifying `use_ai` authorization before accessing the Chat interface).

```
Role Hierarchy:
SUPERUSER  ──► Full access across all companies, departments, users & AI
ADMIN      ──► Tenant-level administrative access (users, departments, docs)
EMPLOYEE   ──► Standard access (assigned department docs, search, permitted AI)
```

---

## Page Directory & Feature Modules

| Route | Component | Access Level | Description |
|---|---|---|---|
| `/login` | `Login.jsx` | Public | Email and password authentication portal |
| `/register` | `Register.jsx` | Public | Account registration |
| `/` | `Dashboard.jsx` | Authenticated | KPI metric cards, document totals, response latency, Recharts trends |
| `/chat` | `Chat.jsx` | Permission (`use_ai`) | Conversational AI interface with document citation cards and source references |
| `/documents` | `Documents.jsx` | Authenticated | Document table, status chips (`processed`, `failed`), upload trigger |
| `/search` | `Search.jsx` | Authenticated | Direct semantic vector search with cosine similarity scoring |
| `/settings` | `Settings.jsx` | Authenticated | Profile overview and appearance controls |
| `/admin/users` | `AdminUsers.jsx` | Admin / Superuser | User table, role modification, account activation / deactivation |
| `/admin/departments` | `departments.jsx` | Admin / Superuser | Department creation, listing, and organizational grouping |

---

## API Integration Reference

The frontend interacts with the following backend endpoints:

| Endpoint | Method | Frontend Client Module | Payload / Params |
|---|---|---|---|
| `/auth/login` | `POST` | `src/api/auth.js` | `{ email, password }` |
| `/auth/register` | `POST` | `src/api/auth.js` | `{ email, password, full_name, company_id, department_id }` |
| `/chat/query` | `POST` | `src/api/chat.js` | `{ question, top_k }` |
| `/search/semantic` | `POST` | `src/api/search.js` | `{ query, top_k }` |
| `/documents/upload` | `POST` | `src/api/documents.js` | `FormData: { file, department_id }` |
| `/documents/list` | `GET` | `src/api/documents.js` | Query parameters for pagination / filtering |
| `/documents/{id}` | `DELETE`| `src/api/documents.js` | Document identifier parameter |
| `/analytics/dashboard`| `GET` | `src/api/analytics.js` | `?days=30` |
| `/admin/users` | `GET` | `src/api/admin.js` | None (Bearer Token required) |
| `/departments` | `GET/POST`| `src/api/departments.js`| Department payload / listing |

---

## Document Upload Specifications

File ingestion is handled by `UploadModal.jsx` using `multipart/form-data`:

- **Supported Formats:**
  - PDF (`application/pdf`, `.pdf`)
  - Plain Text (`text/plain`, `.txt`)
  - CSV (`text/csv`, `.csv`)
  - Word Documents (`.docx`)
- **Size Limit:** 50 MB maximum (validated on client side; enforced strictly by backend).
- **Required Metadata:** Every file must be assigned an associated `department_id` during upload.
- **Processing Cycle:** Upon upload, files transition from `uploaded` ➔ `processing` ➔ `processed` (or `failed`).

---

## Styling & UI Guidelines

All styling is consolidated in `src/styles.css` using modern CSS custom properties and utility classes:

- **Typography:** Uses clean sans-serif system font stacks for optimal cross-platform legibility.
- **Color Tokens:** Curated corporate palettes for dark and light UI surfaces, active badges, and status chips:
  - Success / Processed: Vibrant Emerald
  - Processing / Warning: Amber
  - Failed / Danger: Crimson Red
  - Accent / Primary: Indigo / Blue
- **Responsive Layout:** CSS Grid and Flexbox layouts maintain fluid usability across high-resolution desktop monitors and laptop screens.

---

## Troubleshooting & FAQ

### 1. API calls fail with 401 Unauthorized immediately after logging in
Ensure that your system clock is accurate. JWT tokens include an `exp` expiration timestamp. If the token is expired or malformed, the Axios response interceptor will clear `localStorage` and trigger `ekis:logout`.

### 2. File uploads fail with "Unsupported Media Type" or 422 Unprocessable Entity
Verify that the uploaded file matches one of the supported extensions (`.pdf`, `.txt`, `.csv`, `.docx`) and does not exceed 50 MB. Ensure a valid department is selected in the upload modal dropdown.

### 3. Vite development proxy is not forwarding requests
Confirm that the FastAPI backend is running on `http://127.0.0.1:8000`. Check that `vite.config.js` contains the `/api` proxy definition targeting port `8000`.

---

*EKIS Frontend — Engineered for intuitive, intelligent corporate knowledge discovery.*

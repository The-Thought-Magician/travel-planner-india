---
phase: 1
plan: travel-planner-india
name: "travel-planner-india"
type: implementation
duration: "2-3 days"
autonomous: true
requirements: []
tags: [backend, database, deployment, rust, postgresql]
---

# Phase 1: travel-planner-india

## Objective

Build a complete full-stack application for travel-planner-india. Includes PostgreSQL database, Rust/Axum backend with authentication, Next.js 16 frontend, Docker development environment, comprehensive testing, and Fly.io production deployment.

## Steps

### 1. Database Schema Design & Setup
**Description:** Design PostgreSQL schema for travel-planner-india. Create tables for core entities with proper indexes, foreign keys, and JSONB fields for flexible data.

**Duration:** 0.5 days

**Acceptance criteria:**
[ ] All core tables created
[ ] Primary keys and foreign keys configured
[ ] B-tree indexes on frequently queried columns
[ ] JSONB indexes (GIN) on config/metadata fields
[ ] Created_at/updated_at timestamps on all tables
[ ] Migration files versioned with timestamps

---

### 2. Backend Project Initialization
**Description:** Initialize Rust backend with Axum 0.8, Tokio 1.40, SQLx 0.8, and core middleware stack.

**Duration:** 0.5 days

**Acceptance criteria:**
[ ] Cargo project created with correct dependencies
[ ] Health check endpoint (/api/health) working
[ ] Database connection pooling configured
[ ] CORS middleware enabled for frontend
[ ] Error handling middleware implemented
[ ] Structured logging (tracing) configured

---

### 3. Authentication & Authorization System
**Description:** Implement JWT-based authentication with RS256 tokens, refresh token rotation, and role-based access control.

**Duration:** 1 day

**Acceptance criteria:**
[ ] POST /api/v1/auth/register - User registration with bcrypt password hashing
[ ] POST /api/v1/auth/login - Returns JWT access token (15 min expiry) and refresh token
[ ] POST /api/v1/auth/refresh - Refresh access token using valid refresh token
[ ] POST /api/v1/auth/logout - Invalidate refresh token
[ ] Authorization middleware validates JWT in Authorization header
[ ] Role-based endpoint protection working
[ ] HttpOnly cookies for refresh tokens (secure flag set)

---

### 4. Core Resource APIs - CRUD Operations
**Description:** Implement main resource endpoints with pagination, filtering, and sorting support.

**Duration:** 1.5 days

**Acceptance criteria:**
[ ] GET /api/v1/resources?page=1&per_page=20 - List with pagination
[ ] POST /api/v1/resources - Create new resource with validation
[ ] GET /api/v1/resources/:id - Fetch single resource
[ ] PUT /api/v1/resources/:id - Full update with ownership check
[ ] PATCH /api/v1/resources/:id - Partial update
[ ] DELETE /api/v1/resources/:id - Soft or hard delete
[ ] Pagination metadata returned (total, page, per_page, total_pages)
[ ] Input validation using Zod schemas on frontend

---

### 5. Advanced Search & Filtering
**Description:** Implement full-text search, filtering by multiple fields, and sorting for resource discovery.

**Duration:** 1 day

**Acceptance criteria:**
[ ] Full-text search on text columns using PostgreSQL FTS
[ ] Filter by status, date range, user-owned resources
[ ] Sort by created_at, updated_at, custom fields
[ ] Composite indexes for common WHERE + JOIN patterns
[ ] Query performance monitored (EXPLAIN ANALYZE)
[ ] N+1 query problem eliminated via joins/eager loading

---

### 6. Rate Limiting & Request Middleware
**Description:** Implement per-user and per-IP rate limits, request logging, and security headers.

**Duration:** 0.5 days

**Acceptance criteria:**
[ ] Per-user rate limit: 100 requests/min (for authenticated users)
[ ] Per-IP rate limit: 1000 requests/min (for unauthenticated)
[ ] Rate limit headers returned (X-RateLimit-Remaining, X-RateLimit-Reset)
[ ] 429 Too Many Requests response when exceeded
[ ] Request logging middleware logs method, path, status, duration
[ ] Security headers set (Content-Type, X-Content-Type-Options, etc.)

---

### 7. Frontend Project Setup (Next.js 16)
**Description:** Initialize Next.js 16 app with TypeScript, TailwindCSS 4, shadcn/ui, and API client configuration.

**Duration:** 0.5 days

**Acceptance criteria:**
[ ] Next.js 16 project with App Router
[ ] TypeScript 5.3+ configured
[ ] TailwindCSS 4 and PostCSS configured
[ ] shadcn/ui components available
[ ] Environment variables for API URL set
[ ] ESLint and Prettier configured
[ ] API client factory (fetch wrapper) created

---

### 8. Authentication UI Components
**Description:** Build login/signup/logout UI with form validation using shadcn/ui and Zod schemas.

**Duration:** 1 day

**Acceptance criteria:**
[ ] Login form with email and password fields
[ ] Signup form with email, password, name validation
[ ] Password strength indicator
[ ] Form error messages displayed
[ ] Zod schema validation on client-side
[ ] Tokens stored securely (access in memory, refresh in HttpOnly cookie)
[ ] Logout clears tokens and redirects
[ ] Protected routes redirect unauthenticated users to login

---

### 9. Resource List View with Pagination & Filtering
**Description:** Build UI for browsing resources with pagination controls, filters, and sorting.

**Duration:** 1 day

**Acceptance criteria:**
[ ] Resource list displayed in table or cards
[ ] Pagination controls (prev/next, page numbers)
[ ] Filter UI for status, date range, owner
[ ] Sort dropdown for common fields
[ ] Loading states and error handling shown
[ ] TanStack React Query for data fetching and caching
[ ] Search field with debounced API calls
[ ] Empty state message when no results

---

### 10. Create/Edit/Delete Resource Forms
**Description:** Build forms for creating and editing resources with validation and success feedback.

**Duration:** 1 day

**Acceptance criteria:**
[ ] Create resource form with all required fields
[ ] Edit form pre-populates current values
[ ] Form validation with error messages
[ ] Submit button disabled during submission
[ ] Success toast after create/update/delete
[ ] Error toast with user-friendly message on failure
[ ] Delete confirmation modal
[ ] Optimistic updates via TanStack Query mutation

---

### 11. Docker Setup & Local Development Environment
**Description:** Create docker-compose.yml for PostgreSQL, backend, and frontend with health checks.

**Duration:** 0.5 days

**Acceptance criteria:**
[ ] docker-compose.yml with postgres, backend, frontend services
[ ] Health checks configured for postgres and backend
[ ] Environment variables passed via .env file
[ ] Volumes for code hot-reloading
[ ] Backend runs on port 3000, frontend on port 3001
[ ] Database migrations run automatically on startup
[ ] Services depend on healthchecks (correct order)

---

### 12. Backend Unit & Integration Tests
**Description:** Write unit tests for business logic and integration tests for API endpoints with database.

**Duration:** 1 day

**Acceptance criteria:**
[ ] Unit tests for authentication logic (password hashing, JWT generation)
[ ] Integration tests for each API endpoint (happy path + error cases)
[ ] Database tests use test transaction rollback (no fixtures left)
[ ] Mock external dependencies (email service, payment provider)
[ ] Test coverage >70% for critical paths
[ ] Tests run via cargo test with deterministic results
[ ] Test data factory for common objects

---

### 13. Frontend Component & Integration Tests
**Description:** Write tests for React components and API integration using Vitest and React Testing Library.

**Duration:** 1 day

**Acceptance criteria:**
[ ] Component tests for forms, buttons, modals
[ ] Mock API responses for testing without backend
[ ] Test user interactions (clicks, form submissions)
[ ] Verify error states displayed correctly
[ ] Test conditional rendering based on props/state
[ ] Tests run via npm test with coverage reporting
[ ] E2E tests for critical user flows (auth, create, edit, delete)

---

### 14. Production Deployment Setup (Fly.io)
**Description:** Configure Fly.io deployment for backend and frontend with database backup and monitoring.

**Duration:** 1 day

**Acceptance criteria:**
[ ] fly.toml configured for backend with health check
[ ] fly.toml configured for frontend (or use Vercel)
[ ] Environment secrets set via flyctl secrets
[ ] Database managed by Fly Postgres or external provider
[ ] Automated daily backups enabled with 7+ day retention
[ ] Connection pooling configured (pgBouncer)
[ ] Custom domain configured with TLS certificate
[ ] Monitoring dashboard set up (response times, error rates)

---

### 15. Documentation & Final Polish
**Description:** Write API documentation, setup guide, and deployment runbook.

**Duration:** 0.5 days

**Acceptance criteria:**
[ ] README.md with project description and tech stack
[ ] SETUP.md with local development instructions
[ ] API.md documenting all endpoints with curl examples
[ ] DEPLOYMENT.md with production deployment steps
[ ] .env.example provided with all required variables
[ ] Code comments on complex business logic
[ ] No console.logs or debug prints left in production code

---


## Success Criteria

- All 15 implementation steps completed
- Backend builds without errors and passes all tests
- Frontend builds without errors and passes component tests
- Docker compose environment runs successfully
- Deployed to production (Fly.io) with health checks passing
- API documentation complete and accurate
- Code coverage >70% for critical paths

# Research: travel-planner-india - Technical Architecture & Implementation Guide

## Project Overview

**Idea Summary**: Based on project concept for travel-planner-india.

**Use Cases**: 
- Primary use case from project description

**Target Market**: Development teams, B2B SaaS, $20-200/mo

---

## 1. Framework & Library Choices with Versions

### Backend (Rust + Axum)
- **Axum**: 0.8.x (async web framework, type-safe routing)
- **Tokio**: 1.40+ (async runtime with full features)
- **SQLx**: 0.8.x (compile-time checked SQL with PostgreSQL support)
- **Serde**: 1.0+ (serialization/deserialization)
- **Uuid**: 1.10+ (UUID generation)
- **Chrono**: 0.4.38+ (datetime handling, timezone support)
- **Tower**: 0.4+ (middleware and utilities)
- **Tower-http**: 0.5+ (HTTP-specific middleware: CORS, tracing)
- **Tracing**: 0.1+ (structured logging and observability)
- **Tracing-subscriber**: 0.3+ (tracing implementation)
- **Anyhow** / **Thiserror**: Error handling with context
- **Dotenv**: 0.15+ (environment variable management)

### Frontend (Next.js 16 Stack)
- **Next.js**: 16 (App Router, Server Components, latest stable)
- **React**: 19+ (component library, hooks, latest features)
- **TypeScript**: 5.3+ (type safety and tooling)
- **TailwindCSS**: 4 (utility-first CSS framework)
- **shadcn/ui**: Latest (pre-built accessible components)
- **Zod**: 3.22+ (schema validation for runtime safety)
- **Tanstack React Query**: 5.x (data fetching, caching, sync)
- **Zustand**: 4.4+ (lightweight state management, if needed)

### Database
- **PostgreSQL**: 15+ (primary relational data store)
- **PostGIS**: (optional, for location-based queries)
- **pgvector**: (optional, for AI/embedding features)

---

## 2. Key Crates/Packages with Exact Versions

### Backend Dependencies (Cargo.toml)
```toml
[dependencies]
axum = "0.8"
tokio = { version = "1.40", features = ["full"] }
sqlx = { version = "0.8", features = ["postgres", "runtime-tokio-native-tls", "uuid", "chrono"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
uuid = { version = "1.10", features = ["v4", "serde"] }
chrono = { version = "0.4.38", features = ["serde"] }
tower = "0.4"
tower-http = { version = "0.5", features = ["cors", "trace"] }
tracing = "0.1"
tracing-subscriber = "0.3"
anyhow = "1.0"
thiserror = "1.0"
dotenv = "0.15"

[dev-dependencies]
tokio-test = "0.4"
```

### Frontend Dependencies (package.json)
```json
{
  "dependencies": {
    "next": "16.0.0",
    "react": "19.0.0",
    "react-dom": "19.0.0",
    "typescript": "5.3.0",
    "tailwindcss": "4.0.0",
    "@shadcn/ui": "latest",
    "zod": "3.22.0",
    "@tanstack/react-query": "5.0.0",
    "zustand": "4.4.0"
  },
  "devDependencies": {
    "@types/react": "^19.0.0",
    "@types/node": "^20.0.0",
    "autoprefixer": "^10.4",
    "postcss": "^8.4",
    "eslint": "^8.0",
    "eslint-config-next": "16.0.0"
  }
}
```

---

## 3. PostgreSQL Schema Design

### Core Tables Pattern
- **users**: user_id (UUID pk), email (unique), name, password_hash (bcrypt), created_at, updated_at
- **organizations**: org_id (UUID pk), name, owner_id (fk → users), settings (jsonb), created_at, updated_at
- **audit_logs**: log_id (UUID pk), entity_type, entity_id, action, user_id (fk), timestamp, changes (jsonb)
- **api_keys**: key_id (UUID pk), user_id/org_id (fk), key_hash, name, last_used, created_at, expires_at

### Indexing Strategy
- **Primary Keys**: B-tree (default) on UUID
- **Email Fields**: Unique indexes for constraint enforcement
- **Foreign Keys**: Indexes for join performance (required)
- **Timestamp Columns**: B-tree indexes for range queries (created_at, updated_at)
- **JSONB Fields**: GIN indexes for complex object queries (settings, changes)
- **Search Fields**: Full-text search indexes on text columns
- **Composite Indexes**: For common WHERE + JOIN patterns

### Schema Evolution Best Practices
- Backward-compatible migrations (add columns, don't remove)
- SQLx prepared statements provide compile-time safety
- Migration versioning with timestamp prefixes (001_initial_schema.sql, 002_add_column.sql)
- Test migrations in staging before production
- Use explicit transaction control for safety

---

## 4. API Design Patterns

### RESTful Conventions (Axum Routes)
```rust
GET    /api/v1/resources      → List with pagination
POST   /api/v1/resources      → Create new resource
GET    /api/v1/resources/:id  → Read single resource
PUT    /api/v1/resources/:id  → Full update
PATCH  /api/v1/resources/:id  → Partial update
DELETE /api/v1/resources/:id  → Delete resource
```

### Standard Request/Response Format
```json
{
  "success": true,
  "data": { /* resource or array of resources */ },
  "meta": { "total": 100, "page": 1, "per_page": 20 },
  "error": null
}
```

**Error Response**:
```json
{
  "success": false,
  "data": null,
  "meta": null,
  "error": {
    "code": "INVALID_INPUT",
    "message": "Email already exists",
    "details": {"field": "email"}
  }
}
```

### HTTP Status Codes
- **200 OK**: Successful request
- **201 Created**: Resource created
- **204 No Content**: Successful delete/update with no body
- **400 Bad Request**: Invalid input, schema validation failed
- **401 Unauthorized**: Missing/invalid authentication token
- **403 Forbidden**: Insufficient permissions (authenticated but not authorized)
- **404 Not Found**: Resource not found
- **409 Conflict**: Business logic conflict (duplicate email, constraint violation)
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Unexpected server error

### Authentication Strategy
- **JWT Tokens**: RS256 or HS256 in Authorization header (Bearer <token>)
- **Access Tokens**: 15-minute expiry for security
- **Refresh Tokens**: 7-day expiry, stored in HttpOnly cookies (secure, cannot be accessed by JavaScript)
- **Stateless Validation**: No session store required, verify signature using secret key
- **Token Refresh Flow**: Client uses refresh token to get new access token without re-authentication

### Pagination Implementation
- Query parameters: ?page=1&per_page=20&sort_by=created_at&sort_order=desc
- Response includes metadata: total, page, per_page, total_pages
- Cursor-based pagination (optional) for large datasets using encoded cursor tokens
- Default page size: 20, max page size: 100

---

## 5. Deployment Architecture

### Local Development (Docker Compose)
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: app_dev
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: dev_password_123
      POSTGRES_INITDB_ARGS: "--encoding=UTF8"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./migrations:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dev"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://dev:dev_password_123@postgres:5432/app_dev
      RUST_LOG: info,app=debug
      PORT: 3000
    ports:
      - "3000:3000"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./backend/src:/app/src

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:3000
      NEXT_PUBLIC_ENV: development
    ports:
      - "3001:3000"
    depends_on:
      - backend
    volumes:
      - ./frontend/src:/app/src
```

### Production Deployment (Fly.io)

**Backend Deployment**:
- Deploy Rust binary compiled in Docker multi-stage build
- Run on Fly.io VM with 1GB RAM minimum (scale to 2GB+ for high traffic)
- Configure health checks to /api/health endpoint
- Use Fly Postgres managed database or external PostgreSQL provider
- Store secrets via flyctl secrets set DATABASE_URL=...

**Database Management**:
- PostgreSQL 15+ managed by Fly Postgres or external provider (AWS RDS, Supabase, Neon)
- Enable automated daily backups with 7+ day retention
- Use connection pooling (pgBouncer) for high-concurrency scenarios
- Monitor connection count and query performance

**Frontend Deployment**:
- Deploy Next.js on Fly.io VM or use Vercel (faster edge deployments)
- Set environment variables: NEXT_PUBLIC_API_URL=https://api.yourdomain.com
- Enable ISR (Incremental Static Regeneration) for static pages
- Use CDN for static assets (Fly's built-in or Cloudflare)

**Monitoring & Logging**:
- Stream logs to Fly Logs dashboard or external provider (Datadog, LogRocket)
- Monitor uptime, response times, error rates
- Set up alerts for error spikes or downtime
- Use structured logging (JSON format) for easier parsing

### Docker Images

**Rust Backend (Multi-stage)**:
```dockerfile
# Build stage
FROM rust:1.76-slim as builder
WORKDIR /app
COPY Cargo.toml Cargo.lock ./
COPY src ./src
RUN cargo build --release

# Runtime stage
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=builder /app/target/release/app /usr/local/bin/app
EXPOSE 3000
CMD ["app"]
```

**Next.js Frontend**:
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY --from=builder /app/.next ./.next
EXPOSE 3000
CMD ["npm", "start"]
```

---

## 6. Risk Analysis & Mitigation

### Authentication & Security Risks

**Risk**: Password storage vulnerability
- **Mitigation**: Use bcrypt (cost=12) or Argon2 for password hashing, never store plaintext
- **Implementation**: Use bcrypt or argon2 crate in Rust

**Risk**: JWT token leakage
- **Mitigation**: Use HttpOnly cookies for refresh tokens, short-lived access tokens (15 min)
- **Mitigation**: Implement token revocation list (blacklist) for logout

**Risk**: CORS misconfiguration
- **Mitigation**: Use tower-http CORS middleware, explicitly list allowed origins (no wildcards)
- **Mitigation**: Set credentials policy carefully (allow_credentials only with explicit origins)

### Database Risks

**Risk**: SQL Injection
- **Mitigation**: SQLx uses parameterized queries, compile-time checking prevents injection
- **Mitigation**: Never build SQL strings with string concatenation

**Risk**: N+1 Query Problem
- **Mitigation**: Use SQLx joins for eager loading, profile with EXPLAIN ANALYZE
- **Mitigation**: Implement query result caching (Redis optional for distributed systems)

**Risk**: Connection Pool Exhaustion
- **Mitigation**: Set pool size based on expected concurrency (8-32 typically)
- **Mitigation**: Monitor active connections, implement connection timeout

**Risk**: Data Loss/Corruption
- **Mitigation**: Enable automated daily backups with 7+ day retention
- **Mitigation**: Test restore procedures in staging regularly
- **Mitigation**: Use transactions for multi-step operations

### Application Risks

**Risk**: Rate Limiting & DOS
- **Mitigation**: Implement per-user rate limits (e.g., 100 requests/min)
- **Mitigation**: Implement per-IP rate limits (e.g., 1000 requests/min)
- **Mitigation**: Use sliding window algorithm with Redis for distributed rate limiting

**Risk**: API Versioning
- **Mitigation**: Plan for backward compatibility early (v1, v2 endpoints)
- **Mitigation**: Deprecate old versions with 6+ month notice
- **Mitigation**: Document breaking changes clearly

**Risk**: Error Disclosure
- **Mitigation**: Log detailed errors server-side, return generic messages to clients
- **Mitigation**: Never expose database/file paths in error responses
- **Mitigation**: Sanitize user input in error contexts

### Deployment Risks

**Risk**: Database Migrations
- **Mitigation**: Test migrations in staging before production
- **Mitigation**: Create rollback plan for each migration
- **Mitigation**: Use explicit transaction control, avoid concurrent long-running migrations

**Risk**: Secrets Management
- **Mitigation**: Never commit .env files to version control
- **Mitigation**: Use Fly Secrets or external vault for production secrets
- **Mitigation**: Rotate database passwords regularly

**Risk**: Downtime During Deployments
- **Mitigation**: Use blue-green deployments or rolling updates
- **Mitigation**: Implement health checks (/api/health endpoint)
- **Mitigation**: Use database connection pooling to handle temporary disconnects

### Domain-Specific Risks (Customize per project)

**For SaaS/Multi-tenant Projects**:
- Implement tenant isolation at database level (schema or row-level security)
- Ensure audit logs capture all data access
- Implement encryption for sensitive data (PII, financial info)

**For Payment/Financial Projects**:
- Use idempotency keys to prevent duplicate charges
- Implement transaction rollback and reconciliation
- Log all financial transactions for compliance

**For High-Traffic Projects**:
- Implement caching layer (Redis) for frequently accessed data
- Use read replicas for read-heavy workloads
- Monitor database query performance and optimize slow queries

**For Real-time Projects**:
- Use WebSockets instead of long polling
- Implement message queuing (Redis Pub/Sub, RabbitMQ) for event distribution
- Handle disconnection/reconnection gracefully

---

## 7. Development Workflow & Best Practices

### Local Setup
1. Clone repository
2. Copy .env.example to .env and fill in values
3. Run docker compose up to start services
4. Run sqlx migrate run to initialize database
5. Run tests: cargo test (backend), npm test (frontend)

### Git Workflow
- Create feature branches for each task: git checkout -b feature/task-name
- Commit frequently with descriptive messages
- Open pull requests for code review before merging to main
- Merge to main only after all checks pass and code is reviewed

### Code Standards
- **Rust**: Follow Cargo clippy guidelines, format with cargo fmt
- **TypeScript**: ESLint configuration, format with Prettier
- **SQL**: Use SQLx migrations for schema changes, version with timestamps
- **Commits**: Use conventional commits (feat:, fix:, docs:, test:)

### Testing Strategy
- **Unit Tests**: Test individual functions/components in isolation
- **Integration Tests**: Test API endpoints end-to-end with real database
- **E2E Tests**: Test complete user workflows (optional, for critical paths)
- **Performance Tests**: Monitor response times and database query performance

---

## 8. Technology Stack Summary

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Backend Framework | Axum | 0.8 | Type-safe async web framework |
| Async Runtime | Tokio | 1.40+ | Async task execution |
| Database Driver | SQLx | 0.8 | Type-safe database queries |
| Frontend Framework | Next.js | 16 | Full-stack React framework |
| UI Library | React | 19 | Component library |
| Styling | TailwindCSS | 4 | Utility-first CSS |
| Component System | shadcn/ui | Latest | Pre-built accessible components |
| Type Safety | TypeScript | 5.3+ | Static type checking (frontend) |
| Validation | Zod | 3.22+ | Schema validation |
| Data Fetching | TanStack Query | 5.x | Async state management |
| Database | PostgreSQL | 15+ | Relational database |
| Container | Docker Compose | - | Local development environment |
| Deployment | Fly.io | - | Production hosting |

---

**Prepared**: 2026-04-27
**Last Updated**: 2026-04-27
**Status**: Ready for implementation planning

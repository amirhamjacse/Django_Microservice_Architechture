# Simple Blog Platform (Django Microservices)

Fully working initial microservices setup for a blog platform using Django + DRF + JWT auth.

## Services

- `api-gateway` (port `8000`): aggregated health and merged blog feed
- `user-service` (port `8001`): registration, login, user profile APIs
- `post-service` (port `8002`): post CRUD, validates authors against user-service
- `comment-service` (port `8003`): comment CRUD, validates users + posts against upstream services

Each service runs in an isolated Django project with a dedicated PostgreSQL database.

## Architecture Diagram

```mermaid
flowchart LR
  C[Client / Frontend]

  G[API Gateway\nport 8000]
  U[User Service\nport 8001]
  P[Post Service\nport 8002]
  M[Comment Service\nport 8003]

  UDB[(user-db)]
  PDB[(post-db)]
  MDB[(comment-db)]
  GDB[(gateway-db)]

  C -->|health + feed| G
  C -->|register/login/me/users| U
  C -->|posts CRUD| P
  C -->|comments CRUD| M

  G -->|GET /health| U
  G -->|GET /health| P
  G -->|GET /health| M

  G -->|GET /api/posts| P
  G -->|GET /api/comments| M

  P -->|validate author\nGET /api/users/{id}| U
  M -->|validate author\nGET /api/users/{id}| U
  M -->|validate post\nGET /api/posts/{id}| P

  U --> UDB
  P --> PDB
  M --> MDB
  G --> GDB

  C -. Bearer JWT .-> P
  C -. Bearer JWT .-> M
  U -. issues JWT .-> C
  U -. shared secret .-> P
  U -. shared secret .-> M
```

## Quick Start

1. Create env file:
   - `cp .env.example .env`
2. Start all services:
   - `docker compose up --build`
3. Verify gateway health:
   - `GET http://localhost:8000/health/`

## API Overview

### User Service (`http://localhost:8001`)

- `GET /health/`
- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/refresh/`
- `GET /api/users/me/` (Bearer token)
- `GET /api/users/`
- `GET /api/users/{id}/`
- `PATCH /api/users/{id}/` (owner only)

### Post Service (`http://localhost:8002`)

- `GET /health/`
- `GET /api/posts/`
- `GET /api/posts/{id}/`
- `POST /api/posts/` (Bearer token)
- `PATCH /api/posts/{id}/` (owner only)
- `DELETE /api/posts/{id}/` (owner only)

### Comment Service (`http://localhost:8003`)

- `GET /health/`
- `GET /api/comments/`
- `GET /api/comments/{id}/`
- `POST /api/comments/` (Bearer token)
- `PATCH /api/comments/{id}/` (owner only)
- `DELETE /api/comments/{id}/` (owner only)

### API Gateway (`http://localhost:8000`)

- `GET /health/` (aggregates all service health)
- `GET /api/feed/` (returns posts merged with comments)

## End-to-End Flow (Example)

1. Register user:

```bash
curl -X POST http://localhost:8001/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"secret123"}'
```

2. Login and copy `access` token:

```bash
curl -X POST http://localhost:8001/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret123"}'
```

3. Create post:

```bash
curl -X POST http://localhost:8002/api/posts/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title":"My first post","content":"Hello microservices"}'
```

4. Create comment:

```bash
curl -X POST http://localhost:8003/api/comments/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"post_id":1,"body":"Nice post!"}'
```

5. Read merged feed:

```bash
curl http://localhost:8000/api/feed/
```

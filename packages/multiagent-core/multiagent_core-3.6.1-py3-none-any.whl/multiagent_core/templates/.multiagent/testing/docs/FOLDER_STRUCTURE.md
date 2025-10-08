# REQUIRED Test Folder Structure Template

## IMPORTANT: Only TWO directories at root level

```
tests/
├── backend/           # ALL Python/API/Server tests go here
│   ├── api/          # API endpoints, routes, FastAPI
│   ├── auth/         # Authentication, security, tokens
│   ├── services/     # External services, integrations
│   ├── models/       # Database models, schemas
│   ├── middleware/   # Request/response middleware
│   ├── workers/      # Background tasks, queues
│   └── utils/        # Utilities, helpers
└── frontend/         # ALL JavaScript/UI tests go here
    ├── components/   # React/Vue components
    ├── pages/        # Page components, views
    ├── hooks/        # Custom React hooks
    ├── services/     # API clients, frontend services
    └── utils/        # Frontend utilities
```

## RULES - MUST FOLLOW:

1. **NO OTHER DIRECTORIES AT ROOT** - Only `backend/` and `frontend/`
2. **NO FILES IN ROOT OF backend/ or frontend/** - Always use subdirectories
3. **NO contract/, unit/, integration/, e2e/ AT ROOT** - These go inside backend/frontend as needed

## Categorization Rules:

### Goes in backend/:
- Any `.py` file
- Anything with: API, endpoint, FastAPI, Flask, Django
- Anything with: webhook, HMAC, authentication, token, security
- Anything with: database, model, schema, ORM
- Anything with: queue, worker, background task, Celery
- Anything with: AgentSwarm, integration (server-side)

### Goes in frontend/:
- Any `.js`, `.jsx`, `.ts`, `.tsx` file
- Anything with: component, UI, React, Vue, Angular
- Anything with: page, view, screen, route (client-side)
- GitHub Actions workflows (`.yml` files)
- Configuration files, documentation tasks

## Example Task Mapping:

- T020 (FastAPI endpoint) → `backend/api/`
- T021 (Webhook validation) → `backend/auth/` or `backend/utils/`
- T024 (Authentication) → `backend/auth/`
- T029 (AgentSwarm integration) → `backend/services/`
- T001 (GitHub Actions) → `frontend/utils/` or `frontend/pages/`
- T003 (Review automation) → `frontend/services/`

## File Naming Convention:

`{TASK_ID}_{short_description}.test.{ext}`

Examples:
- `T020_fastapi_feedback_endpoint.test.py`
- `T001_github_actions_setup.test.js`
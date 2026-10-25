# Car Dealership Inventory System

Full-stack dealership inventory: customers browse, search and buy vehicles; admins add, edit, delete and restock them.

![CI](https://github.com/rreeynaa/Car-Dealership-Inventory-System/actions/workflows/ci.yml/badge.svg)


![Login page](docs/screenshots/login.png)
![Register page](docs/screenshots/register.png)
![Admin Dashboard](docs/screenshots/admindashboard.png)
![User Dashboard](docs/screenshots/userdashboard.png)

## Stack

FastAPI · PostgreSQL · SQLAlchemy 2 + Alembic · JWT auth · React + TypeScript + Vite · Tailwind · TanStack Query · pytest · Vitest · Docker Compose · GitHub Actions

## Run locally

```bash
docker compose up --build -d      # PostgreSQL + API on :8000 (migrates and seeds on start)
cd frontend && cp .env.example .env && npm install && npm run dev   # app on :5173
```

Backend only: `cd backend && pip install -r requirements-dev.txt && alembic upgrade head && python -m app.seed && uvicorn app.main:app --reload`

| Role | Email | Password |
|---|---|---|
| Admin | admin@dealership.com | Admin#12345 |
| User | user@dealership.com | Shopper#12345 |

Key settings (see `backend/.env.example`): `DATABASE_URL`, `JWT_SECRET` (must be set in production), `CORS_ORIGINS`, `SEED_ON_STARTUP`, `VITE_API_URL`.

## API

Interactive docs at `/docs`.

| Endpoint | Access |
|---|---|
| `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me` | public / user |
| `GET /api/vehicles`, `GET /api/vehicles/search`, `GET /api/vehicles/{id}` | user |
| `POST /api/vehicles/{id}/purchase` | user |
| `POST /api/vehicles`, `PUT /api/vehicles/{id}`, `DELETE /api/vehicles/{id}`, `POST /api/vehicles/{id}/restock` | admin |

## Design decisions

- **Layers:** router → service → repository.
- **No overselling:** purchase is one atomic `UPDATE ... WHERE quantity >= 1`. A test runs 10 simultaneous buyers against 3 cars and asserts exactly 3 succeed.
- **Admins cannot self-register:** the `role` field is ignored on registration; admins come from the seed script.
- **Role comes from the database,** not the token, so demotions apply immediately.
- **Login errors are identical** for unknown emails and wrong passwords.
- **Rate limits** on login, register and purchase (per IP, in memory).
- **Create/update are admin-only,** matching the kata's admin forms.
- **Token in `localStorage`:** simple, but readable by XSS; httpOnly cookies are the alternative.

## Testing

Tests were written first; the history shows red/green pairs.

```bash
cd backend && pytest --cov=app --cov-report=term-missing
cd frontend && npm test && npm run coverage
```

**Results:*
CI (ruff, pytest against Postgres, frontend lint/test/build) runs on every push.


## My AI Usage

**Tool:** Claude (Anthropic). 

**How AI helped:** I gave it the kata and asked for plan, a test-first commit plan, and drafts of the tests and implementation for each step, plus boilerplate (Docker, Alembic, CI, React structure). I also asked it to explain design choices, such as atomic updates and why login errors are identical.

**What I did:**
- Built the repo step by step, running every command and keeping the red → green → commit order.
- Worked on the REST API endpoints
- Ran each generated snippet and debugged what broke, reporting the real errors back: `StrEnum` failing on my Python 3.10, ruff `B008`/`B904` failures in CI, a duplicate-argument `CORSMiddleware` error, rate-limit tests that never returned 429, and running pytest from the wrong directory.
- Got the backend suite and CI to green, then tested the running API by hand in Swagger, including the 403 for normal users, the 409 on a sold-out car and the 429 on repeated bad logins.
- Made the scope and design calls: FastAPI + PostgreSQL, which extras to include, and admin-only create/update.

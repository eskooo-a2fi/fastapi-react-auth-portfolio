# FastAPI + React Auth Portfolio

An end-to-end, **production-minded learning scaffold** showing Python, FastAPI, Pydantic v2, PostgreSQL, SQLAlchemy 2, Alembic migrations, JWT authentication, Argon2 hashing via passlib, React and TypeScript. This is not a fully audited or deployed production identity service.

## Prerequisites
- Python 3.11+ and pip
- Docker with Compose (or local PostgreSQL 17)
- Node.js 20.19+ / 22.12+ and npm for the React client

## Start the API

```bash
cd fastapi-react-auth-portfolio
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
cp .env.example .env
# Replace JWT_SECRET_KEY in .env with a random value: python -c "import secrets; print(secrets.token_urlsafe(48))"
docker compose up -d postgres
alembic upgrade head
uvicorn app.main:app --reload
```

The demo Postgres credentials in Compose are for **local development only**. Set a strong, different password and properly managed secrets for all non-local deployments. The API runs at <http://localhost:8000>; Swagger UI is at <http://localhost:8000/docs>.

PowerShell alternative to `cp`: `Copy-Item .env.example .env`.

## Start the React client

```bash
cd client
npm install
npm run dev
```

Visit <http://localhost:5173>. The browser holds the token in React memory only (it resets on reload). The API's `CORS_ORIGINS` allows this local origin. In a real system consider secure HttpOnly cookies with explicit CSRF protections and a stronger session management model.

## API endpoints

| Endpoint | Request | Response |
| --- | --- | --- |
| `GET /health` | none | `{"status":"ok"}` |
| `POST /auth/register` | JSON: `email`, `password` (12–128 characters) | HTTP 201 public user |
| `POST /auth/login` | JSON: `email`, `password` | JWT bearer token + expiry |
| `POST /auth/token` | OAuth2 form: `username` (email), `password` | JWT for Swagger Authorize |
| `GET /auth/me` | `Authorization: Bearer TOKEN` | public active user |

Email is normalised to lowercase; passwords are hashed; the unique email index protects concurrent registrations. The token verifies signature, algorithm, issuer, audience and expiration. JWT does **not** support instant logout/revocation in this scaffold.

## Tests and quality gates

```bash
python -m pytest -q
ruff check app tests
cd client && npm run build
```

Unit tests use SQLite in memory for fast isolation. They are **not PostgreSQL integration tests**. For production, add a dedicated integration test container, migrations smoke tests, rate limiting, observability, TLS, revocation/refresh strategy, email verification, account recovery, secret rotation, abuse detection and dependency/security auditing.

## AI-assisted review

See [`CLAUDE_CODE_REVIEW.md`](CLAUDE_CODE_REVIEW.md) for three exact Claude Code review/test prompts and curl examples. Example review comments also appear in `app/main.py`.

## Repository setup

```bash
git init
git add .
git commit -m "Build FastAPI PostgreSQL React auth portfolio"
gh repo create fastapi-react-auth-portfolio --public --source=. --remote=origin --push
```

Authenticate GitHub CLI (`gh auth login`) before the final command. **Never commit `.env` or real user records.**

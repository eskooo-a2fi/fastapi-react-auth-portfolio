# AI-assisted code review workflow · Claude Code

Use Claude Code only if you have installed and authenticated it yourself. Run it from the repository directory. **Human review of authentication and security decisions remains necessary.**

## Prompt 1 — threat-model the auth code

> Review `app/main.py`, `app/auth.py`, `app/models.py`, `app/schemas.py`, and `app/database.py`. Explain potential authentication bypasses, JWT claim validation weaknesses, password policy gaps, timing attacks, SQL injection, race conditions, CORS mistakes, token storage concerns, and database transaction risks. Prioritise by impact. Do not change code yet.

## Prompt 2 — test generation and verification

> Read `tests/test_auth.py`. Add tests for malformed tokens, expired JWT, wrong audience, inactive users, duplicate email race behaviour, password validation and failure modes. Run `python -m pytest -q` and report the exact results. Use an in-memory SQLite database only for unit tests; do not infer that SQLite proves PostgreSQL compatibility.

## Prompt 3 — focused refactor

> Implement the three highest-impact safe improvements using small diffs. Keep the route contracts intact, do not introduce secrets, update README instructions and rerun `python -m pytest -q`. Show a diff for human approval.

## Manual API review

```bash
curl http://127.0.0.1:8000/health
curl -i http://127.0.0.1:8000/auth/register -H 'Content-Type: application/json' -d '{"email":"demo@example.com","password":"very-long-test-password"}'
curl -i http://127.0.0.1:8000/auth/login -H 'Content-Type: application/json' -d '{"email":"demo@example.com","password":"very-long-test-password"}'
```

Copy the `access_token` from the second response and run:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://127.0.0.1:8000/auth/me
```

These demo credentials must never be reused on a real service. No personal or confidential data should be pasted into AI tools.

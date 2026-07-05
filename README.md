# Sentra

**Secure AI. Build with Confidence.**

Sentra is a modern AI Agent security testing platform. Paste a deployed AI agent URL and simulate 13 real-world attack scenarios spanning 6 OWASP LLM Top 10 categories to discover vulnerabilities before attackers do.

## Features

- **13 Attack Scenarios** — Covering 6 OWASP categories: LLM01 (Prompt Injection), LLM02 (Sensitive Information Disclosure), LLM05 (Improper Output Handling), LLM06 (Excessive Agency), LLM07 (System Prompt Leakage), LLM10 (Unbounded Consumption)
- **Demo Agent** — Built-in sandboxed agent with 3 tools (read file, send email, search web) for instant testing
- **Custom Agent Testing** — Test your own deployed agent via webhook
- **OWASP-Aligned Scoring** — 0–100 security score with breakdown by OWASP categories with per-scenario tagging
- **Export** — Professional PDF reports (cover page, donut gauge, OWASP bar charts, executive summary, per-scenario findings with mitigations), CSV, or JSON
- **Scan Comparison** — Compare two scans side by side to track regressions
- **Authentication** — JWT-based login/registration with admin panel and password reset
- **User Isolation** — Scans are owned per user; admins can see all, users see only their own
- **SSRF Protection** — Webhook connector blocks requests to internal network ranges
- **Sanitized Errors** — Error messages never leak API keys or stack traces
- **CLI Mode** — Run scans from CI/CD pipelines
- **Rate Limiting** — Built-in API rate limiting with slowapi on auth and admin endpoints
- **Tests** — Backend unit tests (pytest) and frontend component tests (vitest)

## Quick Start

```bash
docker compose up --build
```

Visit `http://localhost:8000`

## Screenshots

| Dashboard | Results | PDF Export |
|---|---|---|
| ![Dashboard](screenshots/dashboard.png) | ![Results](screenshots/results.png) | ![PDF Export](screenshots/pdf-report.png) |

## CLI Usage

Run a scan against the demo agent:

```bash
docker compose exec sentra python -m app.cli --agent-type demo --iterations 5
```

Run against a custom agent:

```bash
docker compose exec sentra python -m app.cli --agent-type custom --url https://your-agent.example.com --iterations 3
```

## Project Structure

```
sentra/
├── backend/
│   ├── app/
│   │   ├── agents/          # Demo and custom agent connectors
│   │   ├── routers/         # API endpoints (auth, scans, admin)
│   │   ├── reporting/       # Vulnerability data & OWASP metadata
│   │   ├── scoring/         # Scoring and OWASP breakdown
│   │   ├── test_engine/     # 13 attack scenario implementations
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── auth.py          # JWT authentication
│   │   └── report_generator.py  # Professional PDF reports with OWASP charts
│   ├── tests/               # Backend tests (pytest)
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Route pages (Dashboard, Results, Admin, etc.)
│   │   └── __tests__/       # Frontend tests (vitest)
│   └── package.json
└── docker-compose.yml
```

## Configuration

Copy `backend/.env.example` to `backend/.env` and adjust:

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | No | `sqlite:///./agent_auditor.db` | SQLAlchemy database URL |
| `JWT_SECRET` | Yes (prod) | auto-generated (warning) | 32+ character random secret for JWT signing |
| `OPENAI_API_KEY` | No | — | OpenAI API key (omit for demo/mock mode) |
| `OPENAI_MODEL` | No | `gpt-4o-mini` | OpenAI model name |
| `RATE_LIMIT` | No | `10/minute` | Request rate limit string (slowapi format) |
| `CORS_ORIGINS` | No | `http://localhost:5173,http://localhost:8000` | Comma-separated allowed CORS origins |
| `CUSTOM_AGENT_TIMEOUT` | No | `15` | Webhook request timeout in seconds |

## Running Tests

```bash
# Backend
docker compose exec sentra python -m pytest backend/tests/ -v

# Frontend
cd frontend && npm test
```

## OWASP LLM Top 10 Mapping

Each attack scenario is mapped to its corresponding OWASP category based on the actual behavior being tested:

| OWASP Category | Scenarios |
|----------------|-----------|
| **LLM01: Prompt Injection** | Goal Deviation, Indirect Injection, Multi-Step Chain, Role-Play Jailbreak, Token Smuggling, Context Window Overflow |
| **LLM02: Sensitive Information Disclosure** | System Prompt Extraction |
| **LLM05: Improper Output Handling** | Tool Output Injection |
| **LLM06: Excessive Agency** | Excessive Agency, Permission Boundary, Tool Abuse |
| **LLM07: System Prompt Leakage** | Prompt Boundary Probing |
| **LLM10: Unbounded Consumption** | Tool Loop Exploit |

## Tech Stack

- **Backend:** Python 3.12, FastAPI, SQLAlchemy, SQLite, ReportLab
- **Frontend:** React 18, Vite, Tailwind CSS, Chart.js, Framer Motion
- **Infra:** Docker, docker-compose

## API Reference

### Auth (`/api/auth`)

| Method | Path | Description |
|---|---|---|
| POST | `/api/auth/register` | Register a new user (rate-limited) |
| POST | `/api/auth/login` | Login, returns JWT token (rate-limited) |
| GET | `/api/auth/me` | Get current user profile |

### Scans (`/api/scans`)

| Method | Path | Description |
|---|---|---|
| POST | `/api/scans` | Create and launch a new scan (rate-limited) |
| GET | `/api/scans` | List recent scans (user-scoped) |
| POST | `/api/scans/{id}/cancel` | Cancel a running scan |
| GET | `/api/scans/{id}` | Get scan status |
| GET | `/api/scans/{id}/results` | Get full scan results |
| GET | `/api/scans/{id}/export` | Download JSON export |
| GET | `/api/scans/{id}/export/pdf` | Download PDF report |
| GET | `/api/scans/{id}/export/csv` | Download CSV export |

### Admin (`/api/admin`)

| Method | Path | Description |
|---|---|---|
| GET | `/api/admin/users` | List all users (rate-limited) |
| GET | `/api/admin/stats` | System statistics (rate-limited) |
| POST | `/api/admin/users/{id}/reset-password` | Reset user password (rate-limited) |

### Other

| Method | Path | Description |
|---|---|---|
| GET | `/api/payloads` | List all test payloads |

### CLI

Run scans from CI/CD without a browser:

```bash
# Run all 13 scenarios against the demo agent
python -m app.cli --agent-type demo --iterations 5

# Run against your own agent
python -m app.cli --agent-type custom --webhook-url https://your-agent.example.com --iterations 5

# Fail CI if score is below 70
python -m app.cli --agent-type demo --iterations 5 --threshold 70
```

## License

MIT

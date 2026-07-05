# Sentra

**Secure AI. Build with Confidence.**

Sentra is a modern AI Agent security testing platform. Paste a deployed AI agent URL and simulate 13 real-world attack scenarios spanning 6 OWASP LLM Top 10 categories to discover vulnerabilities before attackers do.

## Features

- **13 Attack Scenarios** — Covering 6 OWASP categories: LLM01 (Prompt Injection), LLM02 (Sensitive Information Disclosure), LLM05 (Improper Output Handling), LLM06 (Excessive Agency), LLM07 (System Prompt Leakage), LLM10 (Unbounded Consumption)
- **Demo Agent** — Built-in sandboxed agent with 3 tools (read file, send email, search web) for instant testing
- **Custom Agent Testing** — Test your own deployed agent via webhook
- **OWASP-Aligned Scoring** — 0–100 security score with breakdown by OWASP categories with per-scenario tagging
- **Export** — Download scan reports as PDF, CSV, or JSON
- **Scan Comparison** — Compare two scans side by side to track regressions
- **Authentication** — JWT-based login/registration with admin panel and password reset
- **CLI Mode** — Run scans from CI/CD pipelines
- **Rate Limiting** — Built-in API rate limiting with slowapi
- **Tests** — Backend unit tests (pytest) and frontend component tests (vitest)

## Quick Start

```bash
docker compose up --build
```

Visit `http://localhost:8000`

Default credentials: `admin` / `admin123`

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
│   │   ├── scoring/         # Scoring and OWASP breakdown
│   │   ├── test_engine/     # 9 attack scenario implementations
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── auth.py          # JWT authentication
│   │   └── report_generator.py  # PDF report generation
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

## License

MIT

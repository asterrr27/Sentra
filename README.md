# Agent Action Auditor

Security testing tool for AI agents — detects excessive agency, prompt injection, and goal manipulation vulnerabilities mapped to OWASP LLM Top 10.

## Quick Start

```bash
docker compose up --build
```

Visit `http://localhost:8000`

## Features

- 5 attack scenarios mapped to OWASP LLM01 & LLM06
- Built-in demo agent with 3 sandboxed tools
- Custom agent testing via webhook
- Scoring system (0-100) with per-scenario breakdown
- SQLite scan history
- CLI mode for CI/CD

## CLI Usage

```bash
python -m app.cli --agent-type demo --iterations 5
```

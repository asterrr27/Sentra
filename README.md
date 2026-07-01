# Sentra

**Secure AI. Build with Confidence.**

Modern AI Agent Security Platform. Stress test your deployed AI agents against real-world attacks before attackers do.

## Quick Start

```bash
docker compose up --build
```

Visit `http://localhost:8000`

## Features

- 5 attack scenarios (Goal Deviation, Excessive Agency, Indirect Injection, Permission Boundary, Multi-step Chain)
- Built-in demo agent with 3 sandboxed tools
- Custom agent testing via webhook
- Scoring system (0-100) with OWASP-aligned breakdown
- SQLite scan history
- CLI mode for CI/CD
- Beautiful React dashboard with live attack visualization

## CLI Usage

```bash
python -m app.cli --agent-type demo --iterations 5
```

## Deployment

```bash
docker compose up -d --build
```

Access at `https://sentra.7.jugaar.ai`

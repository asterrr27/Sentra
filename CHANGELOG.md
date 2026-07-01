# Changelog

## [2.1.0] - 2026-07-01
### Added
- 4 new attack types: role_play_jailbreak, token_smuggling, context_window_overflow, tool_abuse (5 payloads each)
- User authentication: register/login/me endpoints with JWT + bcrypt
- Login and Register pages with dark theme
- Admin panel: stats endpoint, users endpoint, admin page with cards + user table
- AuthContext, ProtectedRoute, admin badge in navbar
- CSV export endpoint (`/api/scans/{id}/export/csv`) + export button on Results page
- Compare button on Dashboard (select 2 scans → /compare page)
- Shield monogram logo (hexagon + center dot) replacing S-curve
- Category icons for all 9 scenarios on Payloads page
- `agents/` package with base connector + demo connector

### Fixed
- Demo blank screen: `multi_step_chain` `payload_used` objects → strings
- CLI import bug: `demo_agent.agent` → `agents.get_connector`
- Demo animation shows 9/9 scenarios instead of 5/5
- Removed dead `DEMO_RESULTS` + `get_demo_results()` endpoint
- Frontend assets deployment cleaned up

### Changed
- Updated SCENARIO_LIST and SCENARIO_LABELS to 9 scenarios across Dashboard, Results, Demo, Payloads pages
- Updated `payloads.py`, `runner.py`, `calculator.py` for 9 scenarios
- `agent-auditor.7.jugaar.ai` decommissioned (default_server 444 drop)

## [2.0.0] - 2026-06-30
### Added
- Complete rebrand to Sentra
- React + Vite + Tailwind + Framer Motion frontend
- Landing page with hero, trust stats, features, platform support
- Dashboard with live AttackFlow visualization and terminal output
- Results page with animated gauge, radar chart, vulnerability cards
- Demo mode with simulated scan
- Custom "S" monogram logo
- Multi-stage Docker build

## [0.1.0] - 2026-06-30
### Added
- Initial project scaffold
- Project structure, config, database models, schemas
- `.gitignore`, `CHANGELOG.md`, `README.md`

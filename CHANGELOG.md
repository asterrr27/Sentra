# Changelog

## [2.2.0] - 2026-07-05
### Security
- JWT secret now auto-generates a random 48-char value if missing from `.env`; warns on startup
- Admin user list masks email addresses (PII leak fix)
- Added Content-Security-Policy meta tag to frontend HTML
- Added CORS middleware with configurable origins

### Fixed
- **Critical:** Admin panel shared password state — per-user password state prevents cross-user password reset bug
- **Critical:** Hardcoded JWT secret in config — now reads from env with strong random fallback
- Stale closures in `startScan` polling — uses refs for mutable values instead of closure capture
- 401 interceptor hard reload — uses React Router navigation via callback instead of `window.location`
- Fake URL validation — now performs actual HTTP HEAD request with timeout
- SQLite-specific `check_same_thread` only applied for SQLite URLs
- `utcnow` deprecation — replaced with `datetime.now(timezone.utc)`
- `passed` column type changed from `Integer` to `Boolean`
- Gauge color now animates with `displayScore`, not final score
- Logo gradient ID uses `useId()` instead of `Math.random()`
- Clipboard copy fallback when clipboard API unavailable
- ResizeObserver no longer disconnects after first canvas resize
- `cycleInterval` in Demo no longer runs while paused
- AuthContext cleanup on unmount via `mountedRef`
- Empty catch blocks now log errors
- Component-internal `Card` extracted outside `Compare` function
- Forgot password link changed to disabled text (no reset flow exists)
- Compare button no longer generates empty `id2=` param

### Changed
- Access token expiry reduced from 24h to 60min (configurable)
- Added `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `CORS_ORIGINS` to config
- TrustSection stats replaced fake numbers with real platform capabilities
- 404 catch-all route added to frontend router
- Canvas elements now have `aria-label` attributes

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

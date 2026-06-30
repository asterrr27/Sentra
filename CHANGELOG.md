# Changelog

## [0.1.0] - 2026-06-30
### Added
- Initial project scaffold
- Project structure, config, database models, schemas
- `.gitignore`, `CHANGELOG.md`, `README.md`

## [0.2.0] - 2026-06-30
### Added
- Docker deployment with docker-compose
- Nginx reverse proxy for agent-auditor.7.jugaar.ai
- Fixed background task DB session handling


## [1.0.0] - 2026-06-30
### Added
- All 5 attack scenarios working (goal_deviation, excessive_agency, indirect_injection, permission_boundary, multi_step_chain)
- Fixed None content bug in mock agent
- Template fix for None score comparison
- HTTPS via Let's Encrypt for agent-auditor.7.jugaar.ai


## [1.1.0] - 2026-06-30
### Added
- Dark theme UI with custom CSS (navy/teal/purple palette)
- Animated SVG score gauge on results page
- Light/dark theme toggle persisted in localStorage
- Skeleton loaders during scan progress
- Scan filter/search on dashboard
- Auto-poll for scan completion with redirect
- Re-run scan button on results page
- Share results link button
- Payload library  Test This Scenario quick-action
- Hover tooltips on OWASP categories
- Fade-in animations throughout
- Custom scrollbars

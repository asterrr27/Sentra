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


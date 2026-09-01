# Changelog

Purpose: Records user-visible and foundation-level changes to MediKiosk; read before preparing a release or recording a material change.

This project follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) style and uses semantic-version intent where releases are defined.

## [Unreleased]

### Added

- Foundation documentation for architecture, clinical safety, AI, security/privacy, integrations, API/database, product, and operations.
- Empty `docs/product/FUTURE.md` template for explicitly out-of-scope future ideas.
- AI project context and durable memory workflow.
- **Phase 0:** Project directory structure (`backend/`, `frontend/`, etc.), `docker-compose.yml` for Redis/Postgres, `requirements.txt`, and basic MedGemma connectivity checks.
- **Phase 1:** `PatientDataObject` Pydantic schemas (identity, consent, history, ayush, provenance, patch) and basic FastAPI session routing with a mock repository.
- **Retrospectives:** Added auto-generating retrospective files for Phase 0 and Phase 1.
- **Phase 2:** Dynamic rule-based question engine (`backend/app/engine/`), interview state machine with SOCRATES branching, red-flag scanner (13 rules), `questions_general_intake.json` (12 questions, 6 sections, 6 languages), and session API endpoints (`/next-question`, `/answer`, `/alerts`).

### Changed

- Documentation now defines the four-module scope, PatientDataObject/plugin boundaries, and ModelService requirement.

## Open Questions

- First release version, release cadence, and release owner are pending.

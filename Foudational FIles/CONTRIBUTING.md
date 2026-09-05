# Contributing to MediKiosk

Purpose: Defines the proposed contribution discipline for MediKiosk; read before opening a change or review.

## Contribution rules

- Keep changes scoped to one concern and preserve the four-module product boundary.
- Do not add a `FUTURE.md` idea to implementation unless it has been approved into `PRD.md`.
- Read `AGENTS.md` and relevant documentation before changing a clinical, privacy, architecture, API, data, or integration boundary.
- Never commit credentials, patient data, raw documents/audio, production URLs, or generated secret files.
- Use synthetic/de-identified data in development and tests unless a separately approved process allows otherwise.

## Proposed workflow

1. Create a focused feature branch.
2. Make the smallest coherent change and update focused documentation/contracts.
3. Add/adjust validation and tests appropriate to the risk.
4. Request review before merge; clinical, privacy, security, or integration changes need the relevant owner’s approval.
5. Use Conventional Commits where practical, for example: `feat: add document timeline plugin`.

## Required review checks

- Scope and `FUTURE.md` boundary preserved.
- PatientDataObject/plugin/ModelService architecture followed.
- No direct route-to-database/provider calls.
- Consent, authorization, provenance, uncertainty, and safe failure considered.
- No autonomous clinical decision behavior introduced.
- No secrets/PHI in code, tests, logs, fixtures, or documentation.

## Open Questions

- Final branch naming, merge permissions, required reviewers, CI checks, license, and release workflow are pending repository setup.

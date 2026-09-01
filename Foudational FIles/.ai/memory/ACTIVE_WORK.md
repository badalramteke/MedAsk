# Active Work

## Current session focus
- Phase 3 execution COMPLETE.
- MedGemma 1.5 4B-IT verified LIVE on Colab GPU via `/api/v1/clinical-infer`.
- Ready for Phase 4 (LangGraph Clinical Workflow & Safety Rules).

## File-level focus
- `backend/app/services/model_service.py` — Central ModelService orchestrator.
- `backend/app/services/adapters/` — Colab MedGemma, Gemini, Mock adapters.
- `backend/app/models/ai.py` — AI contracts and structured schemas.
- `backend/app/api/endpoints/sessions.py` — `/ai/structure-narration`, `/ai/generate-summary`, `/ai/health`.

## Current task status
- [x] Phase 0: Foundation Setup
- [x] Phase 1: Core Data Contract
- [x] Phase 2: Question Engine Skeleton (rule-based, no AI)
- [x] Phase 3: MedGemma and ModelService integration
- [ ] Phase 4: LangGraph clinical workflow and safety rules

## Next session should begin with
- Reading `HANDOFF.md` first.
- Reading `PS.md` and `docs/product/PRD.md` (mandatory per RULES.md).
- Reviewing `CURRENT_STATE.md`, `DECISIONS.md`, and `RULES.md`.

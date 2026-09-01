# Known Issues & Blockers

# Known Issues & Blockers

## Current Phase: Phase 6 (API Layer Completion)

### Blocking Issues
- None currently blocking Phase 6.

### Active Issues
- **ABDM Integration (Pending Phase 9):** We currently use `coronasafe.net/abdm` models as structural mocks. Actual API integration is deferred to Phase 9.
- **Ahara-Vihara Dataset:** The actual question JSONs for the AYUSH Ahara-Vihara diet module are missing. Currently, the AYUSH workflow uses a structural placeholder that skips to the end of the Dashavidha Pariksha after standard parameters are complete.
- **Colab Ngrok Tunnel Lifecycle:** Free-tier ngrok tunnels cycle URLs upon reconnecting. In development, the active URL must be verified in `.env` before live Colab testing sessions.

### Resolved Issues
- `ROADMAP.md` stub conflict resolved in Phase 0.
- Missing `backend/requirements.txt` and `.gitignore` resolved in Phase 0.
- Colab MedGemma connection verified LIVE in Phase 3.
- MedGemma 1.5 4B-IT summary synthesis and multimodal chest X-ray image analysis verified LIVE in Phase 5.
- Fixed `answered_questions` state key mapping between LangGraph and summary generator endpoint in Phase 5.
- Fixed schema completeness (added missing family, personal, and ROS sections) per FHIR / PHASES.md requirements in Phase 5.

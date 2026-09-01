# TODO

## Current phase focus
- [x] Phase 0: Foundation setup and audit
- [x] Phase 1: Core data contract and session foundation
- [x] Phase 2: Question Engine Skeleton (rule-based, no AI)
- [x] Phase 3: MedGemma and ModelService integration
- [ ] Phase 4: LangGraph clinical workflow and safety rules

## Phase 4 Tasks (Next Up)
- [ ] Implement LangGraph stateful interview graph (`backend/app/engine/langgraph_workflow.py`).
- [ ] Define state nodes: `ChiefComplaintNode`, `SocratesNode`, `GeneralHistoryNode`, `MenstrualHistoryNode`, `RedFlagMonitorNode`, `InterviewCompleteNode`.
- [ ] Integrate cyclic edge branching and completeness verification.
- [ ] Connect ModelService narration structuring to graph state updates.
- [ ] Ensure non-breaking backwards compatibility with existing `PatientDataObject` patch flow.

## Future Phases
- [ ] Phase 4: LangGraph clinical workflow and safety rules (cyclic branching, SOCRATES state graph)
- [ ] Phase 5: Summary generator (Module C, bilingual patient confirmation + clinician draft)
- [ ] Phase 6: API layer completion (typed REST contracts, WebSockets)
- [ ] Phase 7: Voice module (Bhashini ASR/TTS integration with continuous touch fallback)
- [ ] Phase 8: Document digitization module (Module B, OCR + MedGemma multimodal)
- [ ] Phase 9: Consent, FHIR, ABDM, and HIS integration (Module D)

## Notes
- Update this file immediately when a task is completed or a new blocker is found.

# Phase 2 Retrospective: Question Engine Skeleton

## 1. What Was Done
- **Interview Flow Models:** Created `interview.py` with `InterviewState`, `QuestionResponse`, `AnswerSubmission`, `RedFlagAlert`, and `AnswerResult` — the complete data contract for the interview API.
- **General Intake Dataset:** Created `questions_general_intake.json` with 12 questions across 6 clinical sections (past medical, surgical, medications, allergies, family, social history), all in 6 Indian languages, all with dynamic `followup_triggers` for conditional branching.
- **QuestionBank Engine:** Loads and indexes both SOCRATES (17 Qs) and general intake (12 Qs) = **29 total questions** at startup. Provides localization, domain lookup, and trigger-based next-question routing.
- **FlowController:** The core dynamic state machine — chief complaint determines SOCRATES routing (chest_pain, headache), then general history, with every step driven by `followup_triggers` from JSON data.
- **AnswerValidator:** Validates all answer submissions against the allowed option codes in the JSON datasets. Rejects invalid codes.
- **RedFlagScanner:** Evaluates 13 deterministic clinical rules (from `red_flags_rules.json`) against accumulated patient answers using `structured_fact_pattern` matching. Produces localized alerts without diagnosing.
- **Session API Endpoints:** Added `GET /next-question`, `POST /answer`, and `GET /alerts` to the sessions router.

## 2. Why It Was Done
- **Dynamic Branching = Clinical Realism:** A real doctor doesn't ask the same questions to every patient. If someone says "chest pain", the doctor probes SOCRATES. If someone says "fever", the doctor takes a different path. Our engine mirrors this clinical reasoning by using `followup_triggers` to dynamically route questions based on previous answers.
- **Red Flags Save Lives:** The deterministic red-flag scanner runs after EVERY answer, catching critical patterns (e.g., chest pain radiating to left arm → suspected ACS) and silently alerting triage staff. It never stops the interview or diagnoses — it just flags.
- **AYUSH Separation:** Per PS.md (Ministry of AYUSH/AIIA), AYUSH hospitals are completely separate institutions. Phase 2 intentionally builds only the allopathic/general hospital engine.

## 3. What Technologies Were Used & Why
- **JSON-Driven Question Datasets:** All questions, options, translations, and branching logic live in JSON files (`data/clinical/`), not hardcoded Python. This means clinical teams can add new symptom domains or questions by editing JSON alone — no code changes needed.
- **Singleton Pattern (QuestionBank, FlowController, RedFlagScanner):** Each engine component loads once at startup and is reused across requests. This avoids re-reading JSON files on every API call.
- **FastAPI Dependency Injection:** The session endpoints use the repository pattern and engine singletons, keeping route handlers thin and delegating all logic to the engine layer.

## 4. How to Prepare a Presentation (PPT) for Phase 2

**Slide 1: The Question Engine (Title)**
- **Hook:** "MediKiosk doesn't ask every patient the same questions. Like a real doctor, it listens to your first answer and decides what to ask next."

**Slide 2: Dynamic Branching in Action**
- **Talking Points:** Show the flow diagram — chief complaint → SOCRATES deep-dive (if chest pain or headache) → general history. Emphasize that the same engine can support ANY number of symptom domains by just adding JSON entries.
- **Visual:** The ASCII flow graph from the implementation plan, or a cleaner mermaid diagram.

**Slide 3: Red Flag Detection — Saving Lives Silently**
- **Talking Points:** After every single answer, the engine scans 13 clinical rules. If someone says "chest pain radiates to left arm", rule `RF_CARD_001` fires immediately. The patient continues the interview unaware, but triage staff see an urgent alert.
- **Visual:** A mock alert notification showing the localized Hindi/English red-flag message.
- **Why this matters for SIH:** This is the "Automated Triage Bypassing" innovation differentiator from the PRD.

**Slide 4: Multilingual by Default**
- **Talking Points:** Every question and every option is available in 6 languages (English, Hindi, Marathi, Bengali, Tamil, Telugu). The engine automatically localizes based on the patient's preferred language. Show a side-by-side of a question in English and Hindi.
- **Visual:** A JSON snippet showing `text_by_language` for a question.

**Slide 5: Data-Driven, Not Code-Driven**
- **Talking Points:** All clinical logic lives in JSON files, not Python code. This means a doctor or clinical team can review, approve, and modify the question bank without touching the codebase. Show the `followup_triggers` mechanism.
- **Why this matters for SIH:** Judges value extensibility. MediKiosk can add dermatology, gastroenterology, or any new symptom domain by adding a JSON file.

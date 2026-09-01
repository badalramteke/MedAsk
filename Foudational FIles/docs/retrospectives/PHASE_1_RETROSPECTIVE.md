# Phase 1 Retrospective: Core Data Contract

## 1. What Was Done
- **Pydantic Model Translation:** We translated the theoretical `PatientDataObject` markdown file into strict, enforceable Python classes using Pydantic.
- **Clinical Data Integration:** We imported standard concepts from our JSON datasets (`ayush_dashavidha_pariksha.json` and `questions_socrates.json`) directly into the Python models to ensure type-safety (e.g., creating schemas for Dashavidha Pariksha and the SOCRATES symptom framework).
- **Session Repository (Mock):** Built a mock `SessionRepository` to hold active patient sessions in-memory for immediate API testing.
- **FastAPI Routing Setup:** Created the `main.py` entry point and the `/sessions` API endpoints to create, fetch, and patch patient data objects.

## 2. Why It Was Done
- **Single Source of Truth:** The `PatientDataObject` is the heart of MediKiosk. The frontend, the AI, and the database all need to agree on exactly what a "Patient Session" looks like. By coding it in Pydantic, we force the entire application to follow the rules mathematically.
- **Clinical Safety:** By hardcoding the exact allowed structures for things like `SOCRATES` and `Dashavidha Pariksha`, we ensure the AI cannot invent random clinical parameters. If the AI tries to output a parameter that isn't in our schema, Pydantic will throw a validation error and block it.
- **FastAPI Prototyping:** We set up the API and mock repository so that when we build the Question Engine in Phase 2, we already have a place to save the answers.

## 3. What Technologies Were Used & Why
- **Pydantic (Python):** Pydantic is the industry standard for data validation in Python. It automatically converts JSON payloads into Python objects and validates data types (e.g., ensuring a timestamp is actually a timestamp, not just a random string).
- **FastAPI:** FastAPI natively integrates with Pydantic. When a user sends data to a FastAPI route, FastAPI uses our Pydantic models to automatically validate the data and generate interactive API documentation (Swagger UI) for free.
- **JSON-Patch Mechanism:** We designed a `patch.py` schema based on RFC 6902. This allows modules (like an AI plugin) to send *only* the data that changed (e.g., "add headache to symptoms") rather than resending the entire patient file every time.

## 4. How to Prepare a Presentation (PPT) for Phase 1

**Slide 1: Core Data Contract (Title)**
- **Hook:** "How do we ensure an AI doesn't hallucinate patient data? We put it in a mathematical straightjacket."

**Slide 2: The PatientDataObject (PDO)**
- **Talking Points:** Introduce the PDO. Explain that it is the single source of truth for the entire platform. Every module reads from it and writes to it.
- **Visual:** A diagram showing the PDO in the center, with the Frontend, AI Engine, and Database all connecting to it.

**Slide 3: Enforcing Clinical Standards through Code**
- **Talking Points:** We took established clinical frameworks (SOCRATES for pain, Dashavidha Pariksha for AYUSH) and hardcoded them into `Pydantic` schemas. 
- **Why this matters for SIH:** This proves to the judges that MediKiosk is not just a generic ChatGPT wrapper. It is a strictly structured clinical tool that forces the AI to output standardized, medically recognized data formats.

**Slide 4: API & Provenance**
- **Talking Points:** Show how we track *Provenance* (who added the data? The patient, the doctor, or the AI?). Explain the `/sessions` API endpoints we built using FastAPI to rapidly prototype the data flow.
- **Visual:** A screenshot of a JSON payload showing the `provenance` field (e.g., `"source_type": "AI_EXTRACTED", "confidence": 0.95`).

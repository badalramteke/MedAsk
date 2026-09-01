import asyncio
import json
import os
import sys

# Add backend to path so we can import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from pprint import pprint
from app.api.endpoints.sessions import (
    create_session,
    get_next_question,
    submit_answer,
    generate_summary_endpoint
)
from app.models.core import PatientDataObject, IdentityContext, ConsentContext
from app.models.interview import AnswerSubmission
from app.models.ai import ClinicalSummaryDraft

os.environ["MEDIKIOSK_FACILITY_ID"] = "GENERAL"

async def run_test():
    print("--- 1. Creating Session ---")
    pdo = PatientDataObject(
        identity=IdentityContext(
            session_id="test_session_999",
            facility_id="GENERAL",
            preferred_language="en",
            gender="MALE",
            age=45
        ),
        consent=ConsentContext(
            consent_granted=True,
            consent_timestamp="2024-05-10T10:00:00Z",
            granted_by="PATIENT"
        )
    )
    # Using the router function directly requires catching errors or just trusting the mock
    try:
        session = create_session(pdo)
        print("Session created.")
    except Exception as e:
        print("Session error:", e)

    print("\n--- 2. Starting Interview ---")
    q1 = get_next_question("test_session_999")
    print("Q1:", q1.question_id, "-", q1.question_text)

    print("\n--- 3. Submitting Answers ---")
    ans1 = submit_answer("test_session_999", AnswerSubmission(question_id="__CHIEF_COMPLAINT__", free_text="I have severe chest pain and headache", answer_state="ANSWERED", selected_value_codes=[]))
    print("Next after CC:", ans1.next_question.question_id if ans1.next_question else "Done")
    
    ans2 = submit_answer("test_session_999", AnswerSubmission(question_id="socrates_onset", free_text="It started 3 hours ago", answer_state="ANSWERED", selected_value_codes=[]))
    print("Next after onset:", ans2.next_question.question_id if ans2.next_question else "Done")

    ans3 = submit_answer("test_session_999", AnswerSubmission(question_id="socrates_character", selected_value_codes=["sharp", "crushing"], answer_state="ANSWERED"))
    print("Next after character:", ans3.next_question.question_id if ans3.next_question else "Done")

    print("\n--- 4. Generating Summary (Phase 5) ---")
    res = await generate_summary_endpoint("test_session_999")
    
    print("\nSummary Result Success:", res.success)
    if not res.success:
        print("Error:", res.error_message)
        return
        
    print("\nRaw Payload:")
    pprint(res.structured_payload)
    
    print("\n--- 5. Validating Pydantic Schema ---")
    try:
        draft = ClinicalSummaryDraft(**res.structured_payload)
        print("Validation Successful! The generated draft matches the Phase 5 schema.")
    except Exception as e:
        print("VALIDATION FAILED:", e)

if __name__ == "__main__":
    asyncio.run(run_test())

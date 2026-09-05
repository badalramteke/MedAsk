import sys
import os

# Add backend directory to sys path so we can import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from app.engine.langgraph_workflow import workflow_manager

def test_allopathic_chest_pain():
    print("=== TESTING ALLOPATHIC PATH (MALE, CHEST PAIN) ===")
    session_id = "test_sess_001"
    
    # 1. Start workflow
    next_q, state = workflow_manager.start_workflow(session_id, "GENERAL", "MALE", "en")
    print(f"Step 1 (Start): Should ask CC. Q: {next_q['question_id']}")
    assert next_q['question_id'] == '__CHIEF_COMPLAINT__'
    
    # 2. Answer CC with chest pain
    next_q, state = workflow_manager.process_step(session_id, "GENERAL", "__CHIEF_COMPLAINT__", "chest pain")
    print(f"Step 2 (Answer CC): Should route to SOCRATES. Next Q: {next_q['question_id']}")
    assert next_q['phase'] == 'SOCRATES_DEEP_DIVE'
    
    # 3. Answer SOCRATES
    next_q, state = workflow_manager.process_step(session_id, "GENERAL", next_q['question_id'], ["CHEST_LEFT_SUBSTERNAL"])
    print(f"Step 3 (Answer SOCRATES): Should route to next SOCRATES question. Next Q: {next_q['question_id']}")
    assert next_q['phase'] == 'SOCRATES_DEEP_DIVE'
    
def test_ayush_path():
    print("\n=== TESTING AYUSH PATH ===")
    session_id = "test_sess_002"
    
    # 1. Start workflow
    next_q, state = workflow_manager.start_workflow(session_id, "AYUSH", "FEMALE", "en")
    print(f"Step 1 (Start): Should ask CC. Q: {next_q['question_id']}")
    assert next_q['question_id'] == '__CHIEF_COMPLAINT__'
    
    # 2. Answer CC 
    next_q, state = workflow_manager.process_step(session_id, "AYUSH", "__CHIEF_COMPLAINT__", "joint pain")
    print(f"Step 2 (Answer CC): Should route to AYUSH Dashavidha Pariksha. Next Q: {next_q['question_id']}")
    assert next_q['phase'] == 'AYUSH_DASHAVIDHA'

if __name__ == "__main__":
    test_allopathic_chest_pain()
    test_ayush_path()
    print("\nALL TESTS PASSED!")

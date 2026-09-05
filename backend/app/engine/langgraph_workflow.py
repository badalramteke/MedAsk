"""
Clinical Workflow Manager using LangGraph.
Builds the clinical interview cyclic state machines and provides an API
for the session router to process answers.
"""
from typing import Dict, Any, Tuple
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.engine.workflow_state import ClinicalInterviewState
from app.engine.nodes.chief_complaint import chief_complaint_node
from app.engine.nodes.socrates_node import socrates_node
from app.engine.nodes.general_history_node import general_history_node
from app.engine.nodes.menstrual_history_node import menstrual_history_node
from app.engine.nodes.ayush_node import ayush_node
from app.engine.nodes.validator_node import validator_node
from app.engine.nodes.red_flag_node import red_flag_node

# Non-blocking red-flag scanner wrapper
def wrap_with_red_flag(node_func):
    """Wraps a clinical node to automatically scan for red flags after it runs."""
    def wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
        node_update = node_func(state)
        # Apply the node update to the state copy to feed into red flag scanner
        updated_state = {**state, **node_update}
        red_flag_update = red_flag_node(updated_state)
        
        # Merge both updates
        return {**node_update, **red_flag_update}
    return wrapper

# Conditional edges
def route_from_chief_complaint(state: Dict[str, Any]) -> str:
    """Route after chief complaint capture."""
    print("ROUTER RECEIVES:", state.get("active_symptom_domain"))
    if state.get("pending_question_id"):
        return END
    
    if state.get("active_symptom_domain"):
        return "socrates"
    
    # Check facility type to branch between Allopathic (general) and AYUSH
    if state.get("facility_type", "GENERAL") == "AYUSH":
        return "ayush"
    
    return "general_history"

def route_from_socrates(state: Dict[str, Any]) -> str:
    if state.get("pending_question_id"):
        return END
    if state.get("socrates_completed"):
        return "general_history"
    return "socrates"

def route_from_ayush(state: Dict[str, Any]) -> str:
    if state.get("pending_question_id"):
        return END
    if state.get("ayush_completed"):
        return "general_history"
    return "ayush"

def route_from_general_history(state: Dict[str, Any]) -> str:
    if state.get("pending_question_id"):
        return END
    if state.get("general_history_completed"):
        return "menstrual_history"
    return "general_history"

def route_from_menstrual(state: Dict[str, Any]) -> str:
    if state.get("pending_question_id"):
        return END
    if state.get("menstrual_completed"):
        return "validator"
    return "menstrual_history"


def build_allopathic_graph() -> StateGraph:
    """Build the state graph for general hospitals."""
    workflow = StateGraph(ClinicalInterviewState)
    
    workflow.add_node("chief_complaint", wrap_with_red_flag(chief_complaint_node))
    workflow.add_node("socrates", wrap_with_red_flag(socrates_node))
    workflow.add_node("general_history", wrap_with_red_flag(general_history_node))
    workflow.add_node("menstrual_history", wrap_with_red_flag(menstrual_history_node))
    workflow.add_node("validator", validator_node)
    
    workflow.set_entry_point("chief_complaint")
    
    workflow.add_conditional_edges("chief_complaint", route_from_chief_complaint, {
        "chief_complaint": "chief_complaint",
        "socrates": "socrates",
        "general_history": "general_history",
        END: END
    })
    
    workflow.add_conditional_edges("socrates", route_from_socrates, {
        "socrates": "socrates",
        "general_history": "general_history",
        END: END
    })
    
    workflow.add_conditional_edges("general_history", route_from_general_history, {
        "general_history": "general_history",
        "menstrual_history": "menstrual_history",
        END: END
    })
    
    workflow.add_conditional_edges("menstrual_history", route_from_menstrual, {
        "menstrual_history": "menstrual_history",
        "validator": "validator",
        END: END
    })
    
    workflow.add_edge("validator", END)
    
    return workflow.compile(checkpointer=MemorySaver())


def build_ayush_graph() -> StateGraph:
    """Build the state graph for AYUSH hospitals."""
    workflow = StateGraph(ClinicalInterviewState)
    
    workflow.add_node("chief_complaint", wrap_with_red_flag(chief_complaint_node))
    workflow.add_node("ayush", wrap_with_red_flag(ayush_node))
    workflow.add_node("general_history", wrap_with_red_flag(general_history_node))
    workflow.add_node("menstrual_history", wrap_with_red_flag(menstrual_history_node))
    workflow.add_node("validator", validator_node)
    
    workflow.set_entry_point("chief_complaint")
    
    workflow.add_conditional_edges("chief_complaint", route_from_chief_complaint, {
        "chief_complaint": "chief_complaint",
        "ayush": "ayush",
        "general_history": "general_history",
        END: END
    })
    
    workflow.add_conditional_edges("ayush", route_from_ayush, {
        "ayush": "ayush",
        "general_history": "general_history",
        END: END
    })
    
    workflow.add_conditional_edges("general_history", route_from_general_history, {
        "general_history": "general_history",
        "menstrual_history": "menstrual_history",
        END: END
    })
    
    workflow.add_conditional_edges("menstrual_history", route_from_menstrual, {
        "menstrual_history": "menstrual_history",
        "validator": "validator",
        END: END
    })
    
    workflow.add_edge("validator", END)
    
    return workflow.compile(checkpointer=MemorySaver())


class ClinicalWorkflowManager:
    def __init__(self):
        self.allopathic_graph = build_allopathic_graph()
        self.ayush_graph = build_ayush_graph()
        
    def _get_graph(self, facility_type: str):
        if facility_type.upper() == "AYUSH":
            return self.ayush_graph
        return self.allopathic_graph

    def start_workflow(self, session_id: str, facility_type: str, gender: str, language: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Initialize the graph state and trigger the first step."""
        graph = self._get_graph(facility_type)
        config = {"configurable": {"thread_id": session_id}}
        
        initial_state = {
            "session_id": session_id,
            "facility_type": facility_type,
            "patient_gender": gender,
            "preferred_language": language,
            "chief_complaint_recorded": False,
            "socrates_completed": False,
            "general_history_completed": False,
            "menstrual_completed": False,
            "ayush_completed": False,
            "answered_questions": {},
            "active_red_flags": [],
            "validation_issues": [],
            "is_completed": False,
        }
        
        # Run graph from start
        result = graph.invoke(initial_state, config=config)
        return result.get("pending_question_response"), result

    def process_step(self, session_id: str, facility_type: str, answered_question_id: str, answer_value: Any) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Update state with answer and advance the graph to the next node."""
        graph = self._get_graph(facility_type)
        config = {"configurable": {"thread_id": session_id}}
        
        # Get current state from checkpointer
        current_state = graph.get_state(config).values
        if not current_state:
            raise ValueError(f"No active workflow found for session {session_id}")
            
        # Manually construct the patch to apply
        answered_questions = dict(current_state.get("answered_questions", {}))
        
        if current_state.get("current_step") == "chief_complaint":
            # For chief complaint, answer is free text mapped to chief_complaint property
            chief_complaint = answer_value if isinstance(answer_value, str) else str(answer_value)
            update = {
                "chief_complaint": chief_complaint,
                "chief_complaint_recorded": True
            }
            answered_questions["__CHIEF_COMPLAINT__"] = chief_complaint
            
            from app.engine.nodes.chief_complaint import CHIEF_COMPLAINT_TO_DOMAIN
            from app.engine.question_bank import question_bank
            cc_lower = chief_complaint.strip().lower()
            domain = None
            for pattern, matched_domain in CHIEF_COMPLAINT_TO_DOMAIN.items():
                if pattern in cc_lower:
                    domain = matched_domain
                    break
            if domain and question_bank.has_socrates_domain(domain):
                update["active_symptom_domain"] = domain
        else:
            # For normal questions
            answered_questions[answered_question_id] = answer_value
            update = {}

        update["answered_questions"] = answered_questions
        update["pending_question_id"] = None
        update["pending_question_response"] = None
        
        # Inject state update and run the graph to advance
        graph.update_state(config, update)
        result = graph.invoke(None, config=config)
        
        return result.get("pending_question_response"), result

    def get_state(self, session_id: str, facility_type: str) -> Dict[str, Any]:
        """Fetch the current state from the checkpointer."""
        graph = self._get_graph(facility_type)
        config = {"configurable": {"thread_id": session_id}}
        return graph.get_state(config).values

# Global instance
workflow_manager = ClinicalWorkflowManager()

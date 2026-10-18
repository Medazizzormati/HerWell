from typing import TypedDict
from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session
from .llm import generate_response
from .rag import retrieve_resources, retrieve_project_documents
from .safety import safety_precheck, safety_postcheck

class ChatState(TypedDict, total=False):
    message: str
    intent: str
    resources: list[dict]
    response: str
    degraded: bool
    safety: bool
    project_id: int  # Optional project ID for Technical PFE Assistant

def classify_intent(message: str) -> str:
    text = message.lower()
    if any(word in text for word in ["planning", "schedule", "study", "exam", "devoir", "révision", "قراية", "امتحان"]):
        return "study_planning"
    if any(word in text for word in ["sleep", "stress", "anx", "burnout", "fatigue", "قلق", "تعب", "متوترة"]):
        return "wellbeing"
    return "general_support"

def build_graph(db: Session):
    async def precheck(state: ChatState):
        if safety_precheck(state["message"]):
            return {"safety": True, "response": (
                "Je suis désolé que vous traversiez cela. Je ne peux pas évaluer votre sécurité à distance. "
                "Si vous êtes en danger immédiat, contactez les services d'urgence locaux vérifiés ou une personne "
                "de confiance qui peut rester avec vous. Les contacts locaux doivent être vérifiés et configurés par l'équipe."
            )}
        return {"safety": False, "intent": classify_intent(state["message"])}

    async def retrieve(state: ChatState):
        # If project_id is provided, retrieve project documents + general resources
        if state.get("project_id"):
            project_docs = retrieve_project_documents(db, state["project_id"], state["message"])
            general_resources = retrieve_resources(db, state["message"])
            # Extract results from the dict if present
            general_results = general_resources.get("results", general_resources) if isinstance(general_resources, dict) else general_resources
            # Combine results, prioritizing project documents
            combined = project_docs + general_results
            return {"resources": combined}
        # Otherwise, just general resources
        return {"resources": retrieve_resources(db, state["message"])}

    async def respond(state: ChatState):
        answer, degraded = await generate_response(state["message"], state.get("resources", []), state.get("intent", "general_support"))
        return {"response": safety_postcheck(answer), "degraded": degraded}

    graph = StateGraph(ChatState)
    graph.add_node("precheck", precheck)
    graph.add_node("retrieve", retrieve)
    graph.add_node("respond", respond)
    graph.set_entry_point("precheck")
    graph.add_conditional_edges("precheck", lambda s: END if s.get("safety") else "retrieve")
    graph.add_edge("retrieve", "respond")
    graph.add_edge("respond", END)
    return graph.compile()

async def run_chat(db: Session, message: str, project_id: int = None) -> dict:
    graph = build_graph(db)
    result = await graph.ainvoke({"message": message, "project_id": project_id})
    
    # Ensure result is a dict
    if not isinstance(result, dict):
        result = {"response": str(result), "intent": "general_support", "resources": [], "degraded": True, "safety": False}
    
    # Handle different resource formats (keyword vs semantic retrieval)
    sources = []
    for r in result.get("resources", []):
        if isinstance(r, dict):
            title = r.get('title', r.get('resource_title', 'Unknown'))
            source = r.get('source', r.get('source_label', 'Unknown'))
            sources.append({"title": title, "source": source})
    
    return {
        "response": result.get("response", ""),
        "intent": result.get("intent", "safety_support" if result.get("safety") else "general_support"),
        "sources": sources,
        "degraded_mode": result.get("degraded", False),
        "safety_routed": result.get("safety", False),
    }

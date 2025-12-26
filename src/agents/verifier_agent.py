from dotenv import load_dotenv
load_dotenv()

from src.utils.state import LeaseAnalysisState
from src.chains.corrective_rag import RetrievalGrader

def verifier_agent_node(state: LeaseAnalysisState):
    """
    Grade retrieval quality and decide if requery needed.

    Evaluates retrieval from appropriate agents based on query scope:
    - "lease_only": Only grades lease documents
    - "law_only": Only grades law documents
    - "both": Grades combined lease + law documents

    If quality < 7/10, triggers requery with refined query.
    """

    print("[✓] Verifier Agent: Grading retrieval quality...")

    # Get query scope to determine what to grade
    scope = state.get("query_scope", "both")

    # Combine documents based on scope
    combined_docs = []

    if scope in ["lease_only", "both"] and state.get("lease_context"):
        combined_docs.extend(state["lease_context"])
        print(f"   Grading {len(state['lease_context'])} lease documents")

    if scope in ["law_only", "both"] and state.get("law_context"):
        combined_docs.extend(state["law_context"])
        print(f"   Grading {len(state['law_context'])} law documents")

    print(f"   Scope: {scope}, Total docs: {len(combined_docs)}")

    # Grade retrieval quality
    grader = RetrievalGrader()

    grade_result = grader.grade(
        query=state["user_query"],
        retrieved_docs=combined_docs
    )

    grade = grade_result["grade"]
    reasoning = grade_result["reasoning"]

    print(f"   Grade: {grade}/10")
    print(f"   Requery needed: {grade < 7}")
    print(f"   Reason: {reasoning}")

    # Increment counter for next iteration
    current_count = state.get("requery_count", 0)

    # Update state
    return {
        "retrieval_quality_grade": grade,
        "needs_requery": grade < 7,
        "requery_reasoning": reasoning,
        "requery_count": current_count + 1,
        "agent_logs": [f"Verifier: Grade {grade}/10, requery={grade < 7}, scope={scope}"]
    }
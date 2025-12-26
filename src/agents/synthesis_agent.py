from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from src.utils.state import LeaseAnalysisState
from src.utils.prompts import (
    SYNTHESIS_PROMPT,
    SYNTHESIS_LEASE_ONLY_PROMPT,
    SYNTHESIS_LAW_ONLY_PROMPT,
    SYNTHESIS_COMPARISON_PROMPT
)

def synthesis_agent_node(state: LeaseAnalysisState):
    """
    Synthesize lease and law findings into final answer.

    Uses scope-aware synthesis prompts:
    - "lease_only": Focus on lease document analysis only
    - "law_only": Focus on legal requirements only
    - "both": Compare lease vs. law and identify conflicts

    Args:
        state: Current analysis state with lease_finding and law_finding

    Returns:
        Updated state with final_answer and confidence level
    """

    print("[Synthesizer] Synthesizer: Generating final answer...")

    # Get query scope to determine synthesis strategy
    scope = state.get("query_scope", "both")
    print(f"   Synthesis scope: {scope}")

    # Use best model for synthesis
    llm = ChatOpenAI(
        model="gpt-4o",  # Best model for complex synthesis
        temperature=0.3   # Slight creativity for natural language
    )

    # Choose appropriate prompt based on scope
    if scope == "lease_only":
        prompt_template = SYNTHESIS_LEASE_ONLY_PROMPT
        synthesis_input = prompt_template.format(
            user_query=state["user_query"],
            lease_finding=state.get("lease_finding", "No lease information found.")
        )
    elif scope == "law_only":
        prompt_template = SYNTHESIS_LAW_ONLY_PROMPT
        synthesis_input = prompt_template.format(
            user_query=state["user_query"],
            law_finding=state.get("law_finding", "No law information found."),
            state=state["state_location"].title()
        )
    else:  # "both"
        prompt_template = SYNTHESIS_COMPARISON_PROMPT
        synthesis_input = prompt_template.format(
            user_query=state["user_query"],
            lease_finding=state.get("lease_finding", "No lease information found."),
            law_finding=state.get("law_finding", "No law information found."),
            state=state["state_location"].title()
        )

    # Generate final answer
    response = llm.invoke(synthesis_input)
    final_answer = response.content
    
    # Determine confidence based on retrieval quality
    quality_grade = state.get("retrieval_quality_grade", 0)
    
    if quality_grade >= 8:
        confidence = "HIGH"
        confidence_emoji = "[HIGH]"
    elif quality_grade >= 6:
        confidence = "MEDIUM"
        confidence_emoji = "[MEDIUM]"
    else:
        confidence = "LOW"
        confidence_emoji = "[LOW]"
    
    print(f"   [✓] Synthesis complete")
    print(f"   [✓] Confidence: {confidence_emoji} {confidence} (quality: {quality_grade}/10)")
    
    # Update state with final results
    state["final_answer"] = final_answer
    state["confidence"] = confidence
    
    # Add metadata for display
    state["agent_logs"] = {
        "lease_score": state.get("lease_retrieval_score", 0),
        "law_score": state.get("law_retrieval_score", 0),
        "quality_grade": quality_grade,
        "iterations": state.get("requery_count", 1),
        "final_query": state.get("current_query", state["user_query"])
    }
    
    # CRITICAL: Return state for LangGraph
    return state
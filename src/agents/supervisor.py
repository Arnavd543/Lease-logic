from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, END
from src.utils.state import LeaseAnalysisState
from src.agents.classifier_agent import classifier_node
from src.agents.lease_agent import lease_agent_node
from src.agents.law_agent import law_agent_node
from src.agents.verifier_agent import verifier_agent_node
from src.agents.synthesis_agent import synthesis_agent_node

# CRITICAL: Maximum iterations to prevent infinite loops
MAX_ITERATIONS = 3

def route_after_classifier(state: LeaseAnalysisState) -> str:
    """
    Route to appropriate agent(s) based on query classification.

    Routes:
    - "lease_only" -> lease_agent only
    - "law_only" -> law_agent only
    - "both" -> lease_agent (then law_agent)

    Args:
        state: Current analysis state

    Returns:
        Next node name
    """

    scope = state.get("query_scope", "both")

    if scope == "lease_only":
        print(f"\n-> Router: Lease-only question, skipping law search\n")
        return "lease_agent"
    elif scope == "law_only":
        print(f"\n-> Router: Law-only question, skipping lease search\n")
        return "law_agent"
    else:
        print(f"\n-> Router: Comparison question, searching both sources\n")
        return "lease_agent"

def should_requery(state: LeaseAnalysisState) -> str:
    """
    Decide whether to requery or proceed to synthesis.
    
    Implements two critical checks:
    1. Hard iteration limit (prevents infinite loops)
    2. Quality threshold (grade >= 7 means proceed)
    
    Args:
        state: Current analysis state
        
    Returns:
        "requery" - Loop back to lease agent for another attempt
        "synthesize" - Proceed to final synthesis
    """
    
    current_iteration = state.get("requery_count", 0)
    quality_grade = state.get("retrieval_quality_grade", 0)
    needs_requery = state.get("needs_requery", False)
    
    # CRITICAL CHECK 1: Hard limit on iterations
    if current_iteration >= MAX_ITERATIONS:
        print(f"\n[WARNING]  Maximum iterations ({MAX_ITERATIONS}) reached.")
        print(f"   Current quality: {quality_grade}/10")
        print(f"   Proceeding to synthesis with best available results...\n")
        return "synthesize"
    
    # CRITICAL CHECK 2: Quality threshold
    if needs_requery:
        print(f"\n[Requery] Supervisor: Quality insufficient ({quality_grade}/10), requerying...")
        print(f"   Iteration {current_iteration}/{MAX_ITERATIONS}\n")
        return "requery"
    
    # Quality is good enough, proceed to synthesis
    print(f"\n[OK] Supervisor: Quality sufficient ({quality_grade}/10), proceeding to synthesis...\n")
    return "synthesize"

def route_after_lease(state: LeaseAnalysisState) -> str:
    """
    Route after lease agent based on query scope.

    If scope is "lease_only", go straight to verifier.
    If scope is "both", go to law_agent next.

    Args:
        state: Current analysis state

    Returns:
        Next node name
    """

    scope = state.get("query_scope", "both")

    if scope == "lease_only":
        print(f"\n-> Router: Lease-only, proceeding to verifier\n")
        return "verifier"
    else:
        print(f"\n-> Router: Need law analysis, proceeding to law_agent\n")
        return "law_agent"

def build_graph():
    """
    Build the LangGraph state machine for lease analysis.

    Graph structure with intelligent routing:
        START
          ↓
        classifier (determine query scope)
          ↓
        [CONDITIONAL ROUTING]
          ↓
        lease_only? -> lease_agent -> verifier
        law_only? -> law_agent -> verifier
        both? -> lease_agent -> law_agent -> verifier
          ↓
        verifier (grade quality)
          ↓
        [CONDITIONAL ROUTING]
          ↓
        Quality < 7? -> YES: Loop back to appropriate agent (max 3 times)
          ↓
        Quality >= 7? -> YES: synthesizer
          ↓
        END

    Returns:
        Compiled LangGraph application
    """

    # Initialize state graph
    graph = StateGraph(LeaseAnalysisState)

    # Add all agent nodes
    graph.add_node("classifier", classifier_node)
    graph.add_node("lease_agent", lease_agent_node)
    graph.add_node("law_agent", law_agent_node)
    graph.add_node("verifier", verifier_agent_node)
    graph.add_node("synthesizer", synthesis_agent_node)

    # Define the flow
    # Entry point: Start with classifier
    graph.set_entry_point("classifier")

    # CONDITIONAL ROUTING after classifier
    graph.add_conditional_edges(
        "classifier",
        route_after_classifier,
        {
            "lease_agent": "lease_agent",
            "law_agent": "law_agent"
        }
    )

    # CONDITIONAL ROUTING after lease agent
    # If lease_only, skip law_agent and go to verifier
    # If both, go to law_agent
    graph.add_conditional_edges(
        "lease_agent",
        route_after_lease,
        {
            "law_agent": "law_agent",
            "verifier": "verifier"
        }
    )

    # After law agent, always go to verifier
    graph.add_edge("law_agent", "verifier")

    # CONDITIONAL ROUTING after verifier
    # This is where corrective RAG iteration happens
    graph.add_conditional_edges(
        "verifier",
        should_requery,  # Decision function
        {
            "requery": "lease_agent",      # Loop back for another attempt
            "synthesize": "synthesizer"    # Quality good, proceed to final answer
        }
    )

    # Synthesis is the final step
    graph.add_edge("synthesizer", END)

    # Compile and return
    return graph.compile()

def run_analysis(
    user_query: str,
    lease_collection_name: str,
    state_location: str = "california"
):
    """
    Convenience function to run complete lease analysis.
    
    Args:
        user_query: User's question about their lease
        lease_collection_name: Name of ChromaDB collection for user's lease
        state_location: State for law lookup (default: california)
        
    Returns:
        Final state with answer and metadata
    """
    
    print("=" * 60)
    print("Starting LeaseLogic analysis...")
    print(f"Query: {user_query}")
    print("=" * 60)
    
    # Build the graph
    app = build_graph()
    
    # Initialize state
    initial_state = {
        "user_query": user_query,
        "current_query": user_query,  # Will be refined if needed
        "lease_collection_name": lease_collection_name,
        "state_location": state_location,
        "requery_count": 0,
        "needs_requery": False
    }
    
    # Run the graph
    final_state = app.invoke(initial_state)
    
    print("=" * 60)
    print("Analysis complete!")
    print("=" * 60)
    
    return final_state


# For testing
if __name__ == "__main__":
    # Test with sample query
    result = run_analysis(
        user_query="Can my landlord charge a $300 late fee?",
        lease_collection_name="test_lease_phase1",
        state_location="california"
    )
    
    print("\n" + "=" * 60)
    print("FINAL ANSWER:")
    print("=" * 60)
    print(result["final_answer"])
    print()
    print(f"Confidence: {result['confidence']}")
    print(f"Quality Grade: {result['retrieval_quality_grade']}/10")
    print(f"Iterations: {result['requery_count']}")
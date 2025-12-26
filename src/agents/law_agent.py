from dotenv import load_dotenv
load_dotenv()

from src.utils.state import LeaseAnalysisState
from src.chains.rag_chain import LawRAG
from src.chains.corrective_rag import CorrectiveRAG
from src.chains.query_refiner import QueryRefiner

def law_agent_node(state: LeaseAnalysisState):
    """
    Search state laws with corrective RAG and query refinement.
    
    Searches state-specific laws + federal laws for the selected state.
    Supports query refinement across iterations.
    
    Args:
        state: Current analysis state
        
    Returns:
        Updated state with law findings
    """
    
    print("[Law Agent]  Law Agent: Analyzing state law...")
    
    # Get current query (or use original if first iteration)
    original_query = state["user_query"]
    query = state.get("current_query", original_query)
    iteration = state.get("requery_count", 0)
    
    # If this is a requery (iteration > 0), refine the query
    if iteration > 0:
        refiner = QueryRefiner()
        query = refiner.refine(
            query=original_query,
            iteration=iteration,
            failure_reason=state.get("requery_reasoning", "")
        )
        print(f"   [Requery] Refined query (iteration {iteration}): '{query}'")
        state["current_query"] = query
    else:
        print(f"   [Synthesizer] Original query: '{query}'")
    
    # Initialize law RAG for user's state
    law_rag = LawRAG(
        state=state["state_location"]
    )
    
    corrective_rag = CorrectiveRAG(base_rag=law_rag)
    
    # Run corrective RAG (single iteration within this agent)
    result = corrective_rag.run(
        query=query,
    )
    
    # Update state with results
    state["law_context"] = result["retrieved_docs"]
    state["law_finding"] = result["analysis"]
    state["law_retrieval_score"] = result["retrieval_score"]
    
    print(f"   [✓] Retrieved {len(result['retrieved_docs'])} law sections")
    print(f"   [✓] Retrieval score: {result['retrieval_score']:.2f}")
    
    # Check if any federal laws were retrieved
    federal_count = sum(
        1 for doc in result["retrieved_docs"]
        if doc['metadata'].get("jurisdiction") == "federal"
    )
    if federal_count > 0:
        print(f"   [✓] Includes {federal_count} federal law(s)")
    
    # CRITICAL: Return state for LangGraph
    return state
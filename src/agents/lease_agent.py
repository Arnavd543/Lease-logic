from dotenv import load_dotenv
load_dotenv()

from src.utils.state import LeaseAnalysisState
from src.chains.rag_chain import LeaseRAG
from src.chains.corrective_rag import CorrectiveRAG
from src.chains.query_refiner import QueryRefiner

def lease_agent_node(state: LeaseAnalysisState):
    """
    Search user's lease with corrective RAG and query refinement.
    
    On first iteration: Uses original query
    On subsequent iterations: Refines query based on previous failure
    
    Args:
        state: Current analysis state
        
    Returns:
        Updated state with lease findings
    """
    
    print("[Classifier] Lease Agent: Analyzing lease document...")
    
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
    
    # Initialize lease RAG with corrective capabilities
    lease_rag = LeaseRAG(
        collection_name=state["lease_collection_name"]
    )
    
    corrective_rag = CorrectiveRAG(base_rag=lease_rag)
    
    # Run corrective RAG (single iteration within this agent)
    result = corrective_rag.run(
        query=query,
    )
    
    # Update state with results
    state["lease_context"] = result["retrieved_docs"]
    state["lease_finding"] = result["analysis"]
    state["lease_retrieval_score"] = result["retrieval_score"]
    
    print(f"   [✓] Retrieved {len(result['retrieved_docs'])} lease chunks")
    print(f"   [✓] Retrieval score: {result['retrieval_score']:.2f}")
    
    # CRITICAL: Return state for LangGraph
    return state
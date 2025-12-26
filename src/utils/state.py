from typing import TypedDict, List, Optional, Dict, Any

class LeaseAnalysisState(TypedDict):
    """
    State object passed between LangGraph nodes.
    
    Each agent reads from and writes to this state object.
    LangGraph automatically manages the flow between agents.
    """
    
    # ========== INPUT FIELDS ==========
    # Set by user at the start
    
    user_query: str
    """Original question from user (never changes)"""
    
    current_query: str
    """Current query being searched (may be refined across iterations)"""
    
    state_location: str
    """State for law lookup (e.g., 'california', 'new_york')"""
    
    lease_collection_name: str
    """Name of ChromaDB collection containing user's lease"""


    # ========== CLASSIFIER OUTPUTS ==========
    # Written by classifier_node

    query_scope: Optional[str]
    """Query classification: 'lease_only', 'law_only', or 'both'"""

    classification_reasoning: Optional[str]
    """Explanation of why query was classified this way"""


    # ========== LEASE AGENT OUTPUTS ==========
    # Written by lease_agent_node
    
    lease_context: Optional[List[Any]]
    """Documents retrieved from user's lease"""
    
    lease_finding: Optional[str]
    """AI analysis of what the lease says"""
    
    lease_retrieval_score: Optional[float]
    """Quality score of lease retrieval (0-10)"""
    
    
    # ========== LAW AGENT OUTPUTS ==========
    # Written by law_agent_node
    
    law_context: Optional[List[Any]]
    """Documents retrieved from state law database"""
    
    law_finding: Optional[str]
    """AI analysis of what the law requires"""
    
    law_retrieval_score: Optional[float]
    """Quality score of law retrieval (0-10)"""
    
    
    # ========== VERIFIER OUTPUTS ==========
    # Written by verifier_agent_node
    
    retrieval_quality_grade: Optional[float]
    """Overall quality grade of combined retrieval (0-10)"""
    
    needs_requery: Optional[bool]
    """Whether retrieval quality requires another iteration"""
    
    requery_count: Optional[int]
    """Number of retrieval iterations performed"""
    
    requery_reasoning: Optional[str]
    """Explanation of why requery is needed (or why not)"""
    
    
    # ========== SYNTHESIS OUTPUTS ==========
    # Written by synthesis_agent_node
    
    final_answer: Optional[str]
    """Final synthesized answer combining lease + law analysis"""
    
    confidence: Optional[str]
    """Confidence level: 'HIGH', 'MEDIUM', or 'LOW'"""
    
    
    # ========== METADATA ==========
    # Additional tracking information
    
    messages: Optional[List[str]]
    """Log of agent actions (optional for debugging)"""
    
    agent_logs: Optional[Dict[str, Any]]
    """Metadata about the analysis process"""


# Example of how state flows through the system:
"""
INITIAL STATE (from user):
{
    "user_query": "Can landlord charge $300 late fee?",
    "current_query": "Can landlord charge $300 late fee?",
    "state_location": "california",
    "lease_collection_name": "my_lease",
    "requery_count": 0
}

AFTER LEASE AGENT:
{
    ... (all previous fields)
    "lease_context": [<Document objects>],
    "lease_finding": "The lease states a $300 late fee...",
    "lease_retrieval_score": 8.5
}

AFTER LAW AGENT:
{
    ... (all previous fields)
    "law_context": [<Document objects>],
    "law_finding": "California law limits late fees to 5%...",
    "law_retrieval_score": 9.0
}

AFTER VERIFIER:
{
    ... (all previous fields)
    "retrieval_quality_grade": 8.5,
    "needs_requery": False,
    "requery_count": 1,
    "requery_reasoning": "Documents directly answer the question"
}

AFTER SYNTHESIZER:
{
    ... (all previous fields)
    "final_answer": "Your lease allows $300, but CA law limits...",
    "confidence": "HIGH"
}
"""
from typing import TypedDict, List, Dict, Optional, Annotated
from langchain_core.messages import BaseMessage
import operator

class LeaseAnalysisState(TypedDict):
    """
    State that flows through the multi-agent system.
    
    Each agent reads from and writes to specific fields.
    LangGraph handles merging updates from different agents.
    """
    
    user_query: str                      # The question user asked
    state_location: str                  # e.g., "california"
    lease_collection_name: str           # ChromaDB collection name for user's lease
    
    lease_context: Optional[List[Dict]]  # Retrieved lease chunks
    lease_retrieval_score: Optional[float]  # Average relevance score
    lease_finding: Optional[str]         # What lease says (from analysis)
    
    law_context: Optional[List[Dict]]    # Retrieved law sections
    law_retrieval_score: Optional[float]
    law_finding: Optional[str]           # What law says (from analysis)
    
    retrieval_quality_grade: Optional[int]  # 0-10 score from grader
    needs_requery: Optional[bool]        # Should we refine and search again?
    requery_count: int                   # Track how many times we've requeried
    requery_reasoning: Optional[str]     # Why quality was insufficient
    
    final_answer: Optional[str]          # Plain-language answer for user
    confidence: Optional[str]            # "high", "medium", or "low"
    
    # Use Annotated with operator.add to accumulate messages
    messages: Annotated[List[BaseMessage], operator.add]
    
    agent_logs: Annotated[List[str], operator.add]  # Track which agents ran
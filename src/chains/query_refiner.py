"""
Query Refiner - Improves search queries for better retrieval

Used in corrective RAG to refine queries when initial retrieval
quality is insufficient. Uses different strategies based on iteration.
"""

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class QueryRefiner:
    """Refines queries to improve retrieval quality"""
    
    def __init__(self):
        """Initialize query refiner with LLM"""
        
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3  # Some creativity for rephrasing
        )
        
        # Prompt template for query refinement
        self.prompt = ChatPromptTemplate.from_template("""
You are refining a search query that didn't retrieve good results.

Original query: {original_query}
Current iteration: {iteration}
Why previous search failed: {failure_reason}

Refine the query based on the iteration number:

**Iteration 1 strategy**: Add specific legal/lease keywords
- Add terms like "clause", "section", "provision", "Civil Code"
- Be more specific about what's being asked

**Iteration 2 strategy**: Simplify to core concept
- Remove unnecessary words
- Focus on the main topic (e.g., "late fee", "security deposit")
- Use synonyms

**Iteration 3+ strategy**: Completely rephrase
- Ask the question differently
- Use alternative terminology
- Focus on the outcome/impact

Examples:
Original: "What does California law say about maximum security deposits?"
Iteration 1: "California Civil Code security deposit maximum limit residential lease"
Iteration 2: "security deposit maximum California"
Iteration 3: "how much can landlord charge deposit California"

Return ONLY the refined query as a single line, no explanation.

Refined query:""")
    
    def refine(
        self, 
        query: str, 
        iteration: int, 
        failure_reason: str = ""
    ) -> str:
        """
        Refine query based on iteration and failure reason.
        
        Args:
            query: Original user query
            iteration: Which iteration (1, 2, 3, etc.)
            failure_reason: Why the previous search failed (from verifier)
            
        Returns:
            Refined query string
        """
        
        # For very first iteration, no refinement needed
        if iteration == 0:
            return query
        
        # Use LLM to refine query
        try:
            response = self.llm.invoke(
                self.prompt.format(
                    original_query=query,
                    iteration=iteration,
                    failure_reason=failure_reason or "Retrieved documents not relevant"
                )
            )
            
            refined = response.content.strip()
            
            # Fallback: if LLM returns empty or too long, use heuristic
            if not refined or len(refined) > 200:
                return self._heuristic_refine(query, iteration)
            
            return refined
            
        except Exception as e:
            print(f"   [WARNING]  Query refinement failed: {e}")
            # Fallback to heuristic refinement
            return self._heuristic_refine(query, iteration)
    
    def _heuristic_refine(self, query: str, iteration: int) -> str:
        """
        Fallback heuristic refinement if LLM fails.
        
        Args:
            query: Original query
            iteration: Current iteration
            
        Returns:
            Refined query using simple heuristics
        """
        
        if iteration == 1:
            # Add legal keywords
            keywords = ["clause", "provision", "section", "law"]
            # Add first keyword that's not already in query
            for kw in keywords:
                if kw.lower() not in query.lower():
                    return f"{query} {kw}"
            return query
        
        elif iteration == 2:
            # Simplify: extract key nouns
            words = query.split()
            # Keep only substantial words (>3 chars, not common words)
            stop_words = {"the", "what", "does", "about", "can", "my", "is", "are", "this", "that"}
            key_words = [w for w in words if len(w) > 3 and w.lower() not in stop_words]
            return " ".join(key_words[:5])  # Max 5 key words
        
        else:
            # Iteration 3+: Just return original
            # At this point, further refinement unlikely to help
            return query


# For testing
if __name__ == "__main__":
    refiner = QueryRefiner()
    
    test_query = "What does California law say about maximum security deposits?"
    
    print("Original query:", test_query)
    print()
    
    for i in range(1, 4):
        refined = refiner.refine(
            query=test_query,
            iteration=i,
            failure_reason="Previous search did not find specific legal limits"
        )
        print(f"Iteration {i}: {refined}")
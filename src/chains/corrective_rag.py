from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.utils.prompts import RETRIEVAL_GRADER_PROMPT, QUERY_REFINEMENT_PROMPT
from typing import Dict, List
import json
import yaml

# Load config
with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

class RetrievalGrader:
    """Grades quality of retrieved documents"""
    
    def __init__(self):
        """Initialize grader with fast model"""
        self.llm = ChatOpenAI(
            model=config["models"]["fast_model"],
            temperature=0
        )
    
    def grade(self, query: str, retrieved_docs: List[Dict]) -> Dict:
        """
        Grade retrieval quality on 0-10 scale.
        
        Args:
            query: Original user query
            retrieved_docs: Documents returned from retrieval
            
        Returns:
            {
                "grade": int (0-10),
                "reasoning": str,
                "needs_requery": bool
            }
        """
        # Format documents for grading
        docs_str = self._format_docs_for_grading(retrieved_docs)
        
        # Create prompt
        prompt = ChatPromptTemplate.from_template(RETRIEVAL_GRADER_PROMPT)
        chain = prompt | self.llm
        
        # Get grading
        response = chain.invoke({
            "query": query,
            "documents": docs_str
        })
        
        # Parse JSON response
        try:
            result = json.loads(response.content)
            
            # Validate structure
            assert "grade" in result, "Missing 'grade' in response"
            assert "reasoning" in result, "Missing 'reasoning' in response"
            assert "needs_requery" in result, "Missing 'needs_requery' in response"
            
            # Ensure grade is in valid range
            result["grade"] = max(0, min(10, int(result["grade"])))
            
            return result
            
        except (json.JSONDecodeError, AssertionError, ValueError) as e:
            # Fallback if LLM doesn't return valid JSON
            print(f"Warning: Grader returned invalid JSON: {e}")
            return {
                "grade": 5,
                "reasoning": "Unable to parse grader response - assuming medium quality",
                "needs_requery": False
            }
    
    def _format_docs_for_grading(self, docs: List[Dict], max_chars: int = 2000) -> str:
        """
        Format documents for grading prompt.
        
        Includes metadata and truncates if too long.
        """
        formatted = []
        
        for i, doc in enumerate(docs[:10], 1):  # Max 10 docs
            metadata = doc.get('metadata', {})
            text = doc['text']
            
            # Truncate long texts
            if len(text) > 400:
                text = text[:400] + "..."
            
            doc_str = f"""Document {i}:
Source: {metadata.get('section', 'unknown')}
Relevance score: {doc.get('score', 'N/A')}
Content: {text}
"""
            formatted.append(doc_str)
        
        result = "\n\n".join(formatted)
        
        # Truncate if still too long
        if len(result) > max_chars:
            result = result[:max_chars] + "\n\n[Additional documents truncated...]"
        
        return result

class QueryRefiner:
    """Refines queries for better retrieval"""
    
    def __init__(self):
        """Initialize refiner"""
        self.llm = ChatOpenAI(
            model=config["models"]["fast_model"],
            temperature=0.3  # Slight creativity for reformulation
        )
    
    def refine(self, original_query: str, issue: str, iteration: int) -> str:
        """
        Refine query based on retrieval issue.
        
        Args:
            original_query: Original search query
            issue: Description of why retrieval was poor
            iteration: Which refinement iteration (1, 2, 3...)
            
        Returns:
            Refined query string
        """
        # For simple cases, use heuristic refinement
        if iteration == 1:
            return self._heuristic_refinement_1(original_query)
        elif iteration == 2:
            return self._heuristic_refinement_2(original_query)
        else:
            # Use LLM for more sophisticated refinement
            return self._llm_refinement(original_query, issue, iteration)
    
    def _heuristic_refinement_1(self, query: str) -> str:
        """First refinement: Add legal keywords"""
        # Simple keyword expansion
        expansions = {
            "late fee": "late fee late payment penalty charges",
            "entry": "entry access landlord entry notice",
            "deposit": "security deposit refund return",
            "rent": "rent rental payment monthly",
            "break lease": "early termination breach lease",
            "eviction": "eviction termination notice unlawful detainer",
        }
        
        query_lower = query.lower()
        for key, expansion in expansions.items():
            if key in query_lower:
                return expansion
        
        # Default: just add "terms conditions clause"
        return f"{query} terms conditions clause"
    
    def _heuristic_refinement_2(self, query: str) -> str:
        """Second refinement: Simplify to core concept"""
        # Extract key nouns
        key_terms = {
            "late fee": "late fee",
            "entry": "entry",
            "deposit": "deposit",
            "rent": "rent",
            "pets": "pets",
            "utilities": "utilities",
            "maintenance": "maintenance repair",
        }
        
        query_lower = query.lower()
        for key, simplified in key_terms.items():
            if key in query_lower:
                return simplified
        
        # Default: return original
        return query
    
    def _llm_refinement(self, original_query: str, issue: str, iteration: int) -> str:
        """Use LLM to refine query"""
        prompt = ChatPromptTemplate.from_template(QUERY_REFINEMENT_PROMPT)
        chain = prompt | self.llm

        response = chain.invoke({
            "original_query": original_query,
            "failure_reason": issue,
            "iteration": iteration
        })

        return response.content.strip()

class CorrectiveRAG:
    """RAG with iterative refinement based on quality grading"""
    
    def __init__(self, base_rag, max_iterations: int = None):
        """
        Initialize corrective RAG.
        
        Args:
            base_rag: The underlying RAG chain (LeaseRAG or LawRAG)
            max_iterations: Max requery attempts (from config if not specified)
        """
        self.base_rag = base_rag
        self.grader = RetrievalGrader()
        self.refiner = QueryRefiner()
        
        if max_iterations is None:
            max_iterations = config["rag"]["max_requery_iterations"]
        self.max_iterations = max_iterations
        
        self.quality_threshold = config["rag"]["confidence_threshold"]
    
    def run(self, query: str, verbose: bool = True) -> Dict:
        """
        Run RAG with corrective loop.
        
        Process:
        1. Retrieve documents
        2. Grade retrieval quality
        3. If quality < threshold and iterations left:
           - Refine query
           - Retrieve again
           - Repeat
        4. Return best result
        
        Args:
            query: User's question
            verbose: Print iteration info
            
        Returns:
            {
                "retrieved_docs": List[Dict],
                "analysis": str,
                "retrieval_score": float,
                "quality_grade": int,
                "iterations": int,
                "grading_reasoning": str
            }
        """
        iteration = 0
        current_query = query
        best_result = None
        best_grade = 0
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"Corrective RAG: {query}")
            print(f"{'='*60}")
        
        while iteration < self.max_iterations:
            if verbose:
                print(f"\n--- Iteration {iteration + 1} ---")
                print(f"Query: {current_query}")
            
            # Retrieve and analyze
            result = self.base_rag.run(current_query)
            
            # Grade retrieval
            grade_result = self.grader.grade(
                query,  # Grade against original query, not refined
                result['retrieved_docs']
            )
            
            if verbose:
                print(f"Grade: {grade_result['grade']}/10")
                print(f"Reasoning: {grade_result['reasoning']}")
            
            # Track best result
            if grade_result['grade'] > best_grade:
                best_grade = grade_result['grade']
                best_result = result
                best_result['quality_grade'] = grade_result['grade']
                best_result['grading_reasoning'] = grade_result['reasoning']
                best_result['iterations'] = iteration + 1
            
            # Check if quality is sufficient
            if grade_result['grade'] >= self.quality_threshold:
                if verbose:
                    print(f"[✓] Quality threshold met!")
                return best_result
            
            # If not, refine and retry (if iterations left)
            if grade_result['needs_requery'] and iteration < self.max_iterations - 1:
                current_query = self.refiner.refine(
                    query,
                    grade_result['reasoning'],
                    iteration + 1
                )
                iteration += 1
            else:
                break
        
        if verbose:
            print(f"\n[✓] Completed {iteration + 1} iterations")
            print(f"[✓] Best grade achieved: {best_grade}/10")
        
        # Return best attempt even if below threshold
        return best_result

# Testing
if __name__ == "__main__":
    from src.chains.rag_chain import LeaseRAG, LawRAG
    
    print("=" * 60)
    print("Testing Corrective RAG")
    print("=" * 60)
    
    # Test with law RAG (should have consistent results)
    print("\n1. Testing with LawRAG:")
    law_rag = LawRAG("california")
    corrective_law = CorrectiveRAG(law_rag)
    
    result = corrective_law.run(
        "late fee",  # Intentionally vague query
        verbose=True
    )
    
    print(f"\nFinal Result:")
    print(f"  Grade: {result['quality_grade']}/10")
    print(f"  Iterations: {result['iterations']}")
    print(f"  Reasoning: {result['grading_reasoning']}")
    
    # Test with lease RAG (you need test lease vector store)
    print("\n" + "=" * 60)
    print("2. Testing with LeaseRAG:")
    try:
        lease_rag = LeaseRAG("test_lease_phase1")
        corrective_lease = CorrectiveRAG(lease_rag)
        
        result = corrective_lease.run(
            "fees",  # Vague query
            verbose=True
        )
        
        print(f"\nFinal Result:")
        print(f"  Grade: {result['quality_grade']}/10")
        print(f"  Iterations: {result['iterations']}")
        
    except Exception as e:
        print(f"Skipping lease test: {e}")
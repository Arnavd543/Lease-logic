from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.utils.state import LeaseAnalysisState
from src.utils.prompts import CLASSIFIER_PROMPT
import json
import yaml

# Load config
with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

def classifier_node(state: LeaseAnalysisState) -> dict:
    """
    Classify query intent to route to appropriate agents.

    Determines if query should:
    - Search only lease ("lease_only")
    - Search only law ("law_only")
    - Search both for comparison ("both")

    This prevents unnecessary searches and low-quality scores from irrelevant sources.

    Args:
        state: Current analysis state with user_query

    Returns:
        Dictionary with:
        - query_scope: "lease_only" | "law_only" | "both"
        - classification_reasoning: Brief explanation
    """

    print("[Classifier] Classifier: Determining query scope...")

    # Use fast model for classification
    llm = ChatOpenAI(
        model=config["models"]["fast_model"],
        temperature=0
    )

    prompt = ChatPromptTemplate.from_template(CLASSIFIER_PROMPT)
    chain = prompt | llm

    # Classify query
    response = chain.invoke({"query": state["user_query"]})

    # Parse JSON response
    try:
        result = json.loads(response.content)

        # Validate structure
        assert "category" in result, "Missing 'category' in response"
        assert "reasoning" in result, "Missing 'reasoning' in response"
        assert result["category"] in ["lease_only", "law_only", "both"], f"Invalid category: {result['category']}"

        print(f"   Scope: {result['category']}")
        print(f"   Reasoning: {result['reasoning']}")

        return {
            "query_scope": result["category"],
            "classification_reasoning": result["reasoning"],
            "agent_logs": [f"Classifier: Scope={result['category']}"]
        }

    except (json.JSONDecodeError, AssertionError, KeyError) as e:
        # Fallback to "both" if classification fails
        print(f"[WARNING]  Classification failed: {e}")
        print(f"   Defaulting to 'both' (search everything)")

        return {
            "query_scope": "both",
            "classification_reasoning": "Classification failed, searching all sources for safety",
            "agent_logs": ["Classifier: Fallback to 'both'"]
        }


# Testing
if __name__ == "__main__":
    print("=" * 60)
    print("Testing Classifier Agent")
    print("=" * 60)

    test_queries = [
        # Lease-only examples
        "What is my monthly rent?",
        "Can I have a pet in my apartment?",
        "When is my rent due each month?",
        "What utilities are included?",

        # Law-only examples
        "What does California law say about security deposits?",
        "Are late fees legal in California?",
        "What is the maximum security deposit allowed by law?",
        "Does California require landlords to provide air conditioning?",

        # Both (comparison) examples
        "Is my $300 late fee legal?",
        "Can my landlord charge me for carpet cleaning?",
        "Is the 2-month security deposit in my lease allowed?",
        "Can my landlord enter without 24 hours notice like my lease says?"
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")

        # Mock state
        test_state = {
            "user_query": query
        }

        result = classifier_node(test_state)

        print(f"\nResult:")
        print(f"  Category: {result['query_scope']}")
        print(f"  Reasoning: {result['classification_reasoning']}")

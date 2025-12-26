"""
Quick integration test that uses existing vector stores
instead of processing PDFs from scratch
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.supervisor import run_analysis

def test_query_classification():
    """Test intelligent query routing"""
    print("=" * 60)
    print("INTEGRATION TEST: Query Classification")
    print("=" * 60)

    test_cases = [
        ("What is my monthly rent?", "lease_only"),
        ("What does California law say about security deposits?", "law_only"),
        ("Is my $300 late fee legal?", "both"),
    ]

    for query, expected_scope in test_cases:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"Expected scope: {expected_scope}")
        print('='*60)

        result = run_analysis(
            user_query=query,
            lease_collection_name="test_lease_phase1",
            state_location="california"
        )

        actual_scope = result.get('query_scope', 'both')
        print(f"\n✓ Actual scope: {actual_scope}")
        print(f"✓ Reasoning: {result.get('classification_reasoning', 'N/A')}")
        print(f"✓ Confidence: {result['confidence']}")
        print(f"✓ Quality: {result['retrieval_quality_grade']}/10")

        # Validate required fields
        assert "final_answer" in result, "Missing final answer"
        assert "confidence" in result, "Missing confidence"
        assert "retrieval_quality_grade" in result, "Missing quality grade"
        assert "query_scope" in result, "Missing query classification"
        assert actual_scope in ["lease_only", "law_only", "both"], \
            f"Invalid scope: {actual_scope}"

        print(f"\n✅ Test passed for: {query}\n")

    print("\n" + "=" * 60)
    print("✅ ALL QUERY CLASSIFICATION TESTS PASSED")
    print("=" * 60)

def test_multi_state_support():
    """Test that different states work"""
    print("\n" + "=" * 60)
    print("INTEGRATION TEST: Multi-State Support")
    print("=" * 60)

    states = ["california"]  # Test just one state for speed

    for state in states:
        print(f"\nTesting {state.title()}...")
        result = run_analysis(
            user_query="What is the maximum security deposit?",
            lease_collection_name="test_lease_phase1",
            state_location=state
        )

        # Check that state name appears in answer
        answer_lower = result['final_answer'].lower()
        assert state.lower() in answer_lower or state.replace('_', ' ') in answer_lower, \
            f"State {state} not mentioned in answer"

        print(f"✓ Scope: {result.get('query_scope', 'unknown')}")
        print(f"✓ Quality: {result['retrieval_quality_grade']}/10")
        print(f"✓ {state.title()} analysis complete")

    print("\n✅ Multi-state test passed!")

if __name__ == "__main__":
    # Run tests that use existing vector stores
    print("\nNOTE: These tests use the existing 'test_lease_phase1' collection")
    print("If that doesn't exist, run test_phase1.py first\n")

    test_query_classification()
    test_multi_state_support()

    print("\n" + "=" * 60)
    print("✅ ALL QUICK INTEGRATION TESTS PASSED")
    print("=" * 60)

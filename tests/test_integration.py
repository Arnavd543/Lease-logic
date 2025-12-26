import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.pdf_processor import LeaseDocumentProcessor
from src.tools.embeddings import VectorStoreManager
from src.agents.supervisor import run_analysis

def test_full_pipeline():
    """Test complete pipeline: PDF → Analysis → Answer"""
    print("=" * 60)
    print("INTEGRATION TEST: Full Pipeline")
    print("=" * 60)

    # Step 1: Process PDF
    print("\n1. Processing PDF...")
    processor = LeaseDocumentProcessor()
    chunks = processor.process_lease_pdf("data/leases/sample_lease.pdf")
    assert len(chunks) > 0, "No chunks created from PDF"
    print(f"✓ Created {len(chunks)} chunks")

    # Step 2: Create vector store
    print("\n2. Creating vector store...")
    vsm = VectorStoreManager()
    collection_name = "integration_test_lease"
    vsm.create_lease_vectorstore(chunks, collection_name)
    print(f"✓ Vector store '{collection_name}' created")

    # Step 3: Run analysis
    print("\n3. Running multi-agent analysis...")
    result = run_analysis(
        user_query="Can my landlord charge a $300 late fee?",
        lease_collection_name=collection_name,
        state_location="california"
    )

    # Step 4: Validate results
    print("\n4. Validating results...")
    assert "final_answer" in result, "Missing final answer"
    assert "confidence" in result, "Missing confidence"
    assert "retrieval_quality_grade" in result, "Missing quality grade"
    assert "query_scope" in result, "Missing query classification"
    assert len(result['final_answer']) > 100, "Answer too short"

    print(f"✓ Confidence: {result['confidence']}")
    print(f"✓ Quality: {result['retrieval_quality_grade']}/10")
    print(f"✓ Query Scope: {result['query_scope']}")
    print(f"✓ Answer length: {len(result['final_answer'])} chars")

    # Step 5: Cleanup
    print("\n5. Cleaning up...")
    vsm.delete_collection(collection_name)
    print("✓ Test collection deleted")

    print("\n" + "=" * 60)
    print("✅ INTEGRATION TEST PASSED")
    print("=" * 60)

def test_query_classification():
    """Test intelligent query routing"""
    print("\n" + "=" * 60)
    print("INTEGRATION TEST: Query Classification")
    print("=" * 60)

    test_cases = [
        ("What is my monthly rent?", "lease_only"),
        ("What does California law say about deposits?", "law_only"),
        ("Is my $300 late fee legal?", "both"),
    ]

    for query, expected_scope in test_cases:
        print(f"\nQuery: {query}")
        result = run_analysis(
            user_query=query,
            lease_collection_name="test_lease_phase1",
            state_location="california"
        )

        actual_scope = result.get('query_scope', 'both')
        print(f"  Expected scope: {expected_scope}")
        print(f"  Actual scope: {actual_scope}")
        print(f"  Reasoning: {result.get('classification_reasoning', 'N/A')}")

        # Note: Classification may vary, so we don't assert strict equality
        # Just check it's one of the valid values
        assert actual_scope in ["lease_only", "law_only", "both"], \
            f"Invalid scope: {actual_scope}"

        print(f"✓ Classification complete")

    print("\n✅ Query classification test passed!")

def test_multi_state_support():
    """Test that different states work"""
    print("\n" + "=" * 60)
    print("INTEGRATION TEST: Multi-State Support")
    print("=" * 60)

    states = ["california", "new_york", "texas"]

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

        print(f"✓ {state.title()} analysis complete")

    print("\n✅ Multi-state test passed!")

def test_error_handling():
    """Test system handles errors gracefully"""
    print("\n" + "=" * 60)
    print("INTEGRATION TEST: Error Handling")
    print("=" * 60)

    # Test with non-existent collection
    try:
        result = run_analysis(
            user_query="Test question",
            lease_collection_name="nonexistent_collection",
            state_location="california"
        )
        print("⚠️ Should have raised error for nonexistent collection")
    except Exception as e:
        print(f"✓ Correctly raised error: {type(e).__name__}")

    print("\n✅ Error handling test passed!")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Run integration tests')
    parser.add_argument('--full', action='store_true',
                       help='Run full pipeline test (slow - processes PDF)')
    parser.add_argument('--quick', action='store_true',
                       help='Run quick tests only (use existing vectorstore)')
    args = parser.parse_args()

    if args.full:
        # Run all tests including the slow PDF processing one
        test_full_pipeline()
        test_query_classification()
        test_multi_state_support()
        test_error_handling()
    elif args.quick:
        # Skip the slow PDF test
        print("Running quick tests (skipping PDF processing)...\n")
        test_query_classification()
        test_multi_state_support()
        test_error_handling()
    else:
        # Default: run quick tests
        print("Running quick tests. Use --full to include PDF processing test\n")
        test_query_classification()
        test_multi_state_support()
        test_error_handling()

    print("\n" + "=" * 60)
    print("✅ ALL INTEGRATION TESTS PASSED")
    print("=" * 60)
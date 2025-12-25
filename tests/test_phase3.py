import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.chains.rag_chain import LeaseRAG, LawRAG

def test_lease_rag():
    """Test lease RAG chain"""
    print("=" * 60)
    print("TEST 1: Lease RAG Chain")
    print("=" * 60)
    
    try:
        lease_rag = LeaseRAG("test_lease_phase1")
        
        test_queries = [
            "What is the monthly rent?",
            "What are the late fees?",
            "Can I have pets?"
        ]
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            result = lease_rag.run(query)
            
            print(f"  Retrieved: {len(result['retrieved_docs'])} docs")
            print(f"  Score: {result['retrieval_score']:.3f}")
            print(f"  Analysis preview: {result['analysis'][:150]}...")
        
        print("\n✅ Lease RAG test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Lease RAG test failed: {e}")
        return False

def test_law_rag():
    """Test law RAG chain"""
    print("\n" + "=" * 60)
    print("TEST 2: Law RAG Chain")
    print("=" * 60)
    
    try:
        law_rag = LawRAG("california")
        
        test_queries = [
            "Can landlord charge a $300 late fee?",
            "How much notice for landlord entry?",
            "What is maximum security deposit?"
        ]
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            result = law_rag.run(query)
            
            print(f"  Retrieved: {len(result['retrieved_docs'])} sections")
            print(f"  Score: {result['retrieval_score']:.3f}")
            
            # Check that law sections are relevant
            sections = [d['metadata']['section'] for d in result['retrieved_docs']]
            print(f"  Sections: {sections}")
        
        print("\n✅ Law RAG test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Law RAG test failed: {e}")
        return False

def test_combined_analysis():
    """Test combining lease + law analysis"""
    print("\n" + "=" * 60)
    print("TEST 3: Combined Analysis")
    print("=" * 60)
    
    try:
        lease_rag = LeaseRAG("test_lease_phase1")
        law_rag = LawRAG("california")
        
        query = "Can my landlord charge a $300 late fee?"
        
        print(f"Query: {query}\n")
        
        # Get lease finding
        lease_result = lease_rag.run(query)
        print("LEASE SAYS:")
        print(lease_result['analysis'])
        
        # Get law finding
        law_result = law_rag.run(query)
        print("\n" + "-" * 60)
        print("LAW SAYS:")
        print(law_result['analysis'])
        
        print("\n✅ Combined analysis test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Combined analysis test failed: {e}")
        return False

if __name__ == "__main__":
    print("LeaseLogic - Phase 3 Testing")
    print("=" * 60)
    
    results = []
    results.append(test_lease_rag())
    results.append(test_law_rag())
    results.append(test_combined_analysis())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ PHASE 3 COMPLETE!")
    else:
        print("⚠️  Some tests failed")
    print("=" * 60)
    print("\nNext: Phase 4 - Implement corrective RAG")
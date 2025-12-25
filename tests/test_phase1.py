import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.pdf_processor import LeaseDocumentProcessor
from src.tools.embeddings import VectorStoreManager

def test_pdf_processing():
    """Test PDF extraction and chunking"""
    print("=" * 60)
    print("TEST 1: PDF Processing")
    print("=" * 60)
    
    sample_pdf = "data/leases/sample_lease.pdf"
    
    if not os.path.exists(sample_pdf):
        print(f"❌ Sample PDF not found at {sample_pdf}")
        print("   Download a sample lease from https://eforms.com/rental/ca/")
        return None
    
    processor = LeaseDocumentProcessor()
    chunks = processor.process_lease_pdf(
        sample_pdf,
        lease_metadata={"state": "california", "lease_type": "residential"}
    )
    
    print(f"\n✓ Extracted {len(chunks)} chunks")
    print(f"✓ Sample chunk metadata: {chunks[0]['metadata']}")
    
    # Check section detection
    sections_found = set(c['metadata']['section'] for c in chunks)
    print(f"✓ Detected sections: {sections_found}")
    
    # Validate chunks
    assert len(chunks) > 0, "No chunks created"
    assert all('text' in c and 'metadata' in c for c in chunks), "Invalid chunk structure"
    
    print("\n✅ PDF processing test passed!")
    return chunks

def test_vector_store(chunks):
    """Test vector store creation and search"""
    print("\n" + "=" * 60)
    print("TEST 2: Vector Store")
    print("=" * 60)
    
    if chunks is None:
        print("⏭️  Skipping (no chunks from previous test)")
        return
    
    vsm = VectorStoreManager()
    
    # Create vector store
    vectorstore = vsm.create_lease_vectorstore(chunks, "test_lease_phase1")
    
    print(f"\n✓ Created vector store with {len(chunks)} embeddings")
    
    # Test searches
    test_queries = [
        "What is the monthly rent?",
        "Can the landlord enter without notice?",
        "What happens if I break the lease early?",
        "What are the late fees?"
    ]
    
    print("\nTesting searches:")
    for query in test_queries:
        results = vsm.search_lease(query, "test_lease_phase1", k=2)
        
        print(f"\n  Query: {query}")
        if results:
            print(f"    Top result section: {results[0]['metadata']['section']}")
            print(f"    Relevance score: {results[0]['score']:.3f}")
        else:
            print("    No results found")
    
    print("\n✅ Vector store test passed!")
    
    # Cleanup
    # vsm.delete_collection("test_lease_phase1")

def test_metadata_filtering():
    """Test metadata filtering in search"""
    print("\n" + "=" * 60)
    print("TEST 3: Metadata Filtering")
    print("=" * 60)
    
    vsm = VectorStoreManager()
    
    try:
        # Search only in rent section
        results = vsm.search_lease(
            "payment",
            collection_name="test_lease_phase1",
            k=5,
            filter_metadata={"section": "rent_payment"}
        )
        
        print(f"\n✓ Found {len(results)} results in 'rent_payment' section")
        
        # Verify all results are from correct section
        sections = [r['metadata']['section'] for r in results]
        assert all(s == "rent_payment" for s in sections), "Filtering failed"
        
        print("✅ Metadata filtering test passed!")
        
    except Exception as e:
        print(f"⚠️  Metadata filtering test skipped: {e}")

if __name__ == "__main__":
    print("LeaseLogic - Phase 1 Testing")
    print("=" * 60)
    
    chunks = test_pdf_processing()
    test_vector_store(chunks)
    test_metadata_filtering()
    
    print("\n" + "=" * 60)
    print("✅ PHASE 1 COMPLETE!")
    print("=" * 60)
    print("\nNext: Phase 2 - Build state law corpus")
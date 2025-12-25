from dotenv import load_dotenv
load_dotenv()

from src.tools.state_law_database import StateLawDatabase
from src.tools.embeddings import VectorStoreManager
from typing import List, Dict
import sys

def create_law_chunks(laws: List[Dict]) -> List[Dict]:
    """
    Convert law sections into chunks for embedding.
    
    Enhanced formatting includes jurisdiction (state vs federal)
    for better context in retrieval.
    
    Args:
        laws: List of law dicts from database
        
    Returns:
        List of chunks ready for embedding
    """
    chunks = []
    
    for law in laws:
        # Determine jurisdiction display
        jurisdiction = law.get('jurisdiction', 'state').upper()
        state_display = law['state'].replace("_", " ").title()
        
        # Enhanced formatting with jurisdiction indicator
        combined_text = f"""{jurisdiction} LAW - {law['title']}

{state_display} Section {law['section']}

{law['text']}

Category: {law['category']}
Jurisdiction: {law.get('jurisdiction', 'state')}
Applies to: {state_display}
"""
        
        chunks.append({
            "text": combined_text.strip(),
            "metadata": {
                "section": law['section'],
                "title": law['title'],
                "category": law['category'],
                "state": law['state'],
                "jurisdiction": law.get('jurisdiction', 'state'),
                "source": f"{law['state']}_tenant_law"
            }
        })
    
    return chunks

def build_law_vectorstore(state: str = "california") -> None:
    """
    Build vector store for a specific state + federal laws.
    
    Args:
        state: State to build (e.g., "california", "new_york", "texas")
    """
    print(f"\n{'='*60}")
    print(f"Building {state.upper()} Law Vector Store")
    print(f"{'='*60}")
    
    # Load laws (includes federal automatically)
    db = StateLawDatabase()
    laws = db.get_laws_for_state(state)
    
    # Count state vs federal
    state_count = len([l for l in laws if l.get('jurisdiction') == 'state'])
    federal_count = len([l for l in laws if l.get('jurisdiction') == 'federal'])
    
    print(f"Loaded {len(laws)} total laws:")
    print(f"  - {state_count} {state} state laws")
    print(f"  - {federal_count} federal laws")
    
    # Create chunks
    chunks = create_law_chunks(laws)
    print(f"Created {len(chunks)} law chunks")
    
    # Create vector store
    vsm = VectorStoreManager()
    vectorstore = vsm.create_lease_vectorstore(
        chunks, 
        collection_name=f"{state}_laws"
    )
    
    print(f"\n✅ Law vector store complete!")
    print(f"   Collection name: {state}_laws")
    print(f"   Total sections embedded: {len(chunks)}")
    
    return vectorstore

def build_all_states() -> None:
    """Build vector stores for ALL supported states"""
    
    db = StateLawDatabase()
    
    print("\n" + "="*60)
    print("BUILDING VECTOR STORES FOR ALL STATES")
    print("="*60)
    print(f"\nStates to build: {len(db.SUPPORTED_STATES)}")
    print(f"States: {', '.join(s.title() for s in db.SUPPORTED_STATES)}\n")
    
    success_count = 0
    failed_states = []
    
    for state in db.SUPPORTED_STATES:
        try:
            build_law_vectorstore(state)
            success_count += 1
        except Exception as e:
            print(f"\n❌ Error building {state}: {e}")
            failed_states.append(state)
    
    # Summary
    print("\n" + "="*60)
    print("BUILD SUMMARY")
    print("="*60)
    print(f"Successful: {success_count}/{len(db.SUPPORTED_STATES)}")
    
    if failed_states:
        print(f"Failed: {', '.join(failed_states)}")
    else:
        print("All states built successfully! ✅")
    
    print("\n" + "="*60)
    print("USAGE INSTRUCTIONS")
    print("="*60)
    print("\nTo use in your app:")
    print("  from src.chains.rag_chain import LawRAG")
    print("  law_rag = LawRAG('california')  # or 'new_york', 'texas', etc.")
    print("  result = law_rag.run('Can landlord charge $300 late fee?')")

def test_law_search(state: str = "california"):
    """
    Test law vector store with sample queries.
    
    Args:
        state: State to test
    """
    print(f"\n{'='*60}")
    print(f"Testing {state.upper()} Law Search")
    print(f"{'='*60}")
    
    vsm = VectorStoreManager()
    
    # Test queries designed to match different categories
    test_queries = [
        ("Can landlord charge a $300 late fee?", "fees"),
        ("Does landlord need to give notice before entry?", "entry_notice"),
        ("What is the maximum security deposit?", "security_deposit"),
        ("How much notice to end month-to-month lease?", "termination"),
        ("Can landlord shut off utilities?", "unlawful_actions"),
        ("Housing discrimination based on race", "discrimination"),  # Should match federal
    ]
    
    for query, expected_category in test_queries:
        print(f"\n{'─'*60}")
        print(f"Query: {query}")
        
        try:
            results = vsm.search_lease(
                query,
                collection_name=f"{state}_laws",
                k=2
            )
            
            if results:
                top_result = results[0]
                jurisdiction = top_result['metadata'].get('jurisdiction', 'state').upper()
                
                print(f"  Top match: {jurisdiction} - Section {top_result['metadata']['section']}")
                print(f"  Title: {top_result['metadata']['title']}")
                print(f"  Category: {top_result['metadata']['category']}")
                print(f"  Relevance: {top_result['score']:.3f}")
                
                # Check if category matches
                if top_result['metadata']['category'] == expected_category:
                    print(f"  ✓ Correct category!")
                else:
                    print(f"  ⚠️  Expected '{expected_category}', got '{top_result['metadata']['category']}'")
            else:
                print("  ❌ No results found")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")

def compare_states(query: str, states: List[str] = None):
    """
    Compare how different states handle the same issue.
    
    Args:
        query: Question to ask across states
        states: List of states to compare (default: all supported)
    """
    db = StateLawDatabase()
    vsm = VectorStoreManager()
    
    if states is None:
        states = db.SUPPORTED_STATES
    
    print(f"\n{'='*60}")
    print(f"COMPARING STATES: {query}")
    print(f"{'='*60}")
    
    for state in states:
        print(f"\n{state.upper()}:")
        print(f"{'─'*60}")
        
        try:
            results = vsm.search_lease(
                query,
                collection_name=f"{state}_laws",
                k=1
            )
            
            if results:
                top = results[0]
                print(f"Section: {top['metadata']['section']}")
                print(f"Title: {top['metadata']['title']}")
                print(f"Summary: {top['text'][:200]}...")
            else:
                print("No relevant law found")
                
        except Exception as e:
            print(f"Error: {e}")

# Main execution
if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "all":
            # Build all states
            build_all_states()
            
        elif command == "test":
            # Test specific state or all
            if len(sys.argv) > 2:
                test_law_search(sys.argv[2])
            else:
                test_law_search("california")
                
        elif command == "compare":
            # Compare states on an issue
            if len(sys.argv) > 2:
                query = " ".join(sys.argv[2:])
                compare_states(query)
            else:
                compare_states("security deposit maximum")
                
        elif command in StateLawDatabase.SUPPORTED_STATES:
            # Build specific state
            build_law_vectorstore(command)
            
        else:
            print(f"Unknown command: {command}")
            print("\nUsage:")
            print("  python src/tools/law_vectorstore.py all              # Build all states")
            print("  python src/tools/law_vectorstore.py california       # Build one state")
            print("  python src/tools/law_vectorstore.py test             # Test California")
            print("  python src/tools/law_vectorstore.py test new_york    # Test specific state")
            print("  python src/tools/law_vectorstore.py compare <query>  # Compare states")
    else:
        # Default: build California only
        print("Building California law database (default)")
        print("Tip: Use 'python src/tools/law_vectorstore.py all' to build all states\n")
        build_law_vectorstore("california")
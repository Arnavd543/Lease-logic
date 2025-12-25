import sys
import os

def test_imports():
    """Test that all required packages can be imported"""
    print("Testing imports...")
    
    try:
        import langchain
        print("✓ LangChain")
        
        import langgraph
        print("✓ LangGraph")
        
        import chromadb
        print("✓ ChromaDB")
        
        import streamlit
        print("✓ Streamlit")
        
        import openai
        print("✓ OpenAI")
        
        from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        print("✓ LangChain-OpenAI")
        
        print("\n✅ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import failed: {e}")
        return False

def test_environment():
    """Test that environment variables are set"""
    print("\nTesting environment variables...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ["OPENAI_API_KEY"]
    optional_vars = ["LANGCHAIN_API_KEY", "LANGCHAIN_TRACING_V2"]
    
    all_set = True
    
    for var in required_vars:
        if os.getenv(var):
            print(f"✓ {var} is set")
        else:
            print(f"❌ {var} is NOT set")
            all_set = False
    
    for var in optional_vars:
        if os.getenv(var):
            print(f"✓ {var} is set (optional)")
        else:
            print(f"⚠️  {var} is not set (optional)")
    
    return all_set

def test_openai_connection():
    """Test OpenAI API connection"""
    print("\nTesting OpenAI connection...")
    
    try:
        from langchain_openai import ChatOpenAI
        from dotenv import load_dotenv
        load_dotenv()
        
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        response = llm.invoke("Say 'Hello from LeaseLogic setup!'")
        
        print(f"✓ OpenAI API connected")
        print(f"  Response: {response.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("LeaseLogic Environment Setup Verification")
    print("=" * 60)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Environment", test_environment()))
    results.append(("OpenAI", test_openai_connection()))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name}: {status}")
    
    if all(r[1] for r in results):
        print("\n🎉 Environment setup complete!")
    else:
        print("\n⚠️  Some tests failed. Fix issues before proceeding.")
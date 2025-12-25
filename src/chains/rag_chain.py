from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.tools.embeddings import VectorStoreManager
from src.utils.prompts import LEASE_ANALYZER_PROMPT, LAW_ANALYZER_PROMPT
from typing import Dict, List
import yaml

# Load config
with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

class LeaseRAG:
    """RAG chain for analyzing lease documents"""
    
    def __init__(self, collection_name: str):
        """
        Initialize lease RAG chain.
        
        Args:
            collection_name: ChromaDB collection name for user's lease
        """
        self.vsm = VectorStoreManager()
        self.collection_name = collection_name
        self.llm = ChatOpenAI(
            model=config["models"]["fast_model"],  # gpt-4o-mini
            temperature=0  # Deterministic for analysis
        )
        self.retrieval_k = config["rag"]["retrieval_k"]
    
    def retrieve(self, query: str, k: int = None) -> List[Dict]:
        """
        Retrieve relevant lease chunks.
        
        Args:
            query: Search query
            k: Number of chunks to retrieve (default from config)
            
        Returns:
            List of retrieved documents with metadata
        """
        if k is None:
            k = self.retrieval_k
        
        results = self.vsm.search_lease(
            query, 
            collection_name=self.collection_name,
            k=k
        )
        
        return results
    
    def analyze(self, query: str, retrieved_docs: List[Dict]) -> str:
        """
        Analyze retrieved lease documents to answer query.
        
        Args:
            query: User's question
            retrieved_docs: Documents from retrieval
            
        Returns:
            Analysis text
        """
        # Format context from retrieved docs
        context_str = "\n\n".join([
            f"[Section: {doc['metadata'].get('section', 'unknown')}]\n{doc['text']}"
            for doc in retrieved_docs
        ])
        
        # Create prompt
        prompt = ChatPromptTemplate.from_template(LEASE_ANALYZER_PROMPT)
        
        # Generate analysis
        chain = prompt | self.llm
        response = chain.invoke({
            "lease_context": context_str,
            "query": query
        })
        
        return response.content
    
    def run(self, query: str) -> Dict:
        """
        Full RAG pipeline: retrieve + analyze.
        
        Args:
            query: User's question
            
        Returns:
            Dict with retrieved_docs, analysis, retrieval_score
        """
        # Retrieve
        docs = self.retrieve(query)
        
        # Analyze
        analysis = self.analyze(query, docs)
        
        # Calculate average score
        avg_score = sum(d['score'] for d in docs) / len(docs) if docs else 0
        
        return {
            "retrieved_docs": docs,
            "analysis": analysis,
            "retrieval_score": avg_score
        }

class LawRAG:
    """RAG chain for analyzing state law"""
    
    def __init__(self, state: str = "california"):
        """
        Initialize law RAG chain.
        
        Args:
            state: State whose laws to search
        """
        self.vsm = VectorStoreManager()
        self.state = state
        self.collection_name = f"{state}_laws"
        self.llm = ChatOpenAI(
            model=config["models"]["fast_model"],
            temperature=0
        )
        # Use fewer results for laws since each section is comprehensive
        self.retrieval_k = 3
    
    def retrieve(self, query: str, k: int = None) -> List[Dict]:
        """Retrieve relevant law sections"""
        if k is None:
            k = self.retrieval_k
        
        results = self.vsm.search_lease(
            query,
            collection_name=self.collection_name,
            k=k
        )
        
        return results
    
    def analyze(self, query: str, retrieved_laws: List[Dict]) -> str:
        """Analyze retrieved laws"""
        # Format context
        context_str = "\n\n".join([
            f"[Civil Code §{doc['metadata']['section']}: {doc['metadata']['title']}]\n{doc['text']}"
            for doc in retrieved_laws
        ])
        
        prompt = ChatPromptTemplate.from_template(LAW_ANALYZER_PROMPT)
        chain = prompt | self.llm
        
        response = chain.invoke({
            "law_context": context_str,
            "query": query
        })
        
        return response.content
    
    def run(self, query: str) -> Dict:
        """Full law RAG pipeline"""
        docs = self.retrieve(query)
        analysis = self.analyze(query, docs)
        
        avg_score = sum(d['score'] for d in docs) / len(docs) if docs else 0
        
        return {
            "retrieved_docs": docs,
            "analysis": analysis,
            "retrieval_score": avg_score
        }

# Testing
if __name__ == "__main__":
    print("=" * 60)
    print("Testing RAG Chains")
    print("=" * 60)
    
    # Test lease RAG (you'll need to have created a test lease vector store)
    print("\n1. Testing Lease RAG:")
    print("-" * 60)
    try:
        lease_rag = LeaseRAG("test_lease_phase1")
        result = lease_rag.run("What is the monthly rent amount?")
        
        print(f"Retrieved {len(result['retrieved_docs'])} documents")
        print(f"Avg score: {result['retrieval_score']:.3f}")
        print(f"\nAnalysis:\n{result['analysis']}")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you've created a test lease vector store first")
    
    # Test law RAG
    print("\n" + "=" * 60)
    print("2. Testing Law RAG:")
    print("-" * 60)
    try:
        law_rag = LawRAG("california")
        result = law_rag.run("Can landlord charge a $300 late fee?")
        
        print(f"Retrieved {len(result['retrieved_docs'])} law sections")
        print(f"Avg score: {result['retrieval_score']:.3f}")
        print(f"\nAnalysis:\n{result['analysis']}")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you've built the law vector store first")
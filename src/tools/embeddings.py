from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
load_dotenv()

class VectorStoreManager:
    """Manages vector stores for leases and laws"""
    
    def __init__(self, persist_directory: str = "./data/vector_stores"):
        """
        Initialize vector store manager.
        
        Args:
            persist_directory: Where to save ChromaDB collections
        """
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"  # $0.02 per 1M tokens
        )
        
        # Initialize ChromaDB client
        self.chroma_client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
    
    def create_lease_vectorstore(
        self, 
        chunks: List[Dict],
        collection_name: str = "lease_documents"
    ) -> Chroma:
        """
        Create vector store from processed lease chunks.
        
        Args:
            chunks: List of dicts with 'text' and 'metadata' keys
            collection_name: Name for the Chroma collection
            
        Returns:
            Chroma vector store instance
        """
        # Extract texts and metadatas
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        
        print(f"Creating embeddings for {len(texts)} chunks...")
        
        # Create vector store
        vectorstore = Chroma.from_texts(
            texts=texts,
            embedding=self.embeddings,
            metadatas=metadatas,
            collection_name=collection_name,
            persist_directory=self.persist_directory
        )
                
        print(f"✓ Vector store '{collection_name}' created with {len(texts)} embeddings")
        
        return vectorstore
    
    def load_vectorstore(self, collection_name: str) -> Chroma:
        """
        Load existing vector store from disk.
        
        Args:
            collection_name: Name of collection to load
            
        Returns:
            Chroma vector store instance
        """
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )
        return vectorstore
    
    def search_lease(
        self,
        query: str,
        collection_name: str = "lease_documents",
        k: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search lease documents with optional metadata filtering.
        
        Args:
            query: Search query
            collection_name: Collection to search
            k: Number of results
            filter_metadata: e.g., {"section": "rent_payment"}
            
        Returns:
            List of dicts with 'text', 'metadata', 'score'
        """
        vectorstore = self.load_vectorstore(collection_name)
        
        # Perform search
        if filter_metadata:
            results = vectorstore.similarity_search_with_score(
                query, k=k, filter=filter_metadata
            )
        else:
            results = vectorstore.similarity_search_with_score(query, k=k)
        
        # Format results
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "text": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score)  # Convert to Python float
            })
        
        return formatted_results
    
    def delete_collection(self, collection_name: str):
        """Delete a collection from ChromaDB"""
        try:
            self.chroma_client.delete_collection(collection_name)
            print(f"✓ Deleted collection '{collection_name}'")
        except Exception as e:
            print(f"Error deleting collection: {e}")

# Example usage
if __name__ == "__main__":
    from pdf_processor import LeaseDocumentProcessor
    import os
    
    # Process PDF
    processor = LeaseDocumentProcessor()
    
    sample_pdf = "data/leases/sample_lease.pdf"
    
    if os.path.exists(sample_pdf):
        chunks = processor.process_lease_pdf(sample_pdf)
        
        # Create vector store
        vsm = VectorStoreManager()
        vectorstore = vsm.create_lease_vectorstore(chunks, "test_lease")
        
        # Test search
        print("\n" + "=" * 60)
        print("Testing vector search...")
        print("=" * 60)
        
        test_queries = [
            "What is the monthly rent amount?",
            "Can the landlord enter without notice?",
            "What are the late fees?"
        ]
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            results = vsm.search_lease(
                query,
                collection_name="test_lease",
                k=3
            )
            
            print(f"Found {len(results)} results:")
            for i, r in enumerate(results, 1):
                print(f"  {i}. Section: {r['metadata'].get('section')}")
                print(f"     Score: {r['score']:.3f}")
                print(f"     Text: {r['text'][:100]}...")
    else:
        print(f"Please add a sample PDF to {sample_pdf} for testing")
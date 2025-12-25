from PyPDF2 import PdfReader
from typing import List, Dict
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter

class LeaseDocumentProcessor:
    """Processes lease PDF documents into structured chunks"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize processor.
        
        Args:
            chunk_size: Target size for each chunk (in characters)
            chunk_overlap: Overlap between chunks to preserve context
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # LangChain's recursive splitter tries to keep semantic units together
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]  # Try splits in this order
        )
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract raw text from PDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text as string
        """
        reader = PdfReader(pdf_path)
        text = ""
        
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            # Add page markers for debugging
            text += f"\n--- PAGE {page_num + 1} ---\n"
            text += page_text + "\n"
        
        return text
    
    def detect_sections(self, text: str) -> Dict[str, str]:
        """
        Detect common lease sections using regex patterns.
        
        This is a heuristic approach - not perfect but works for most leases.
        
        Returns:
            Dict mapping section names to their text content
        """
        sections = {}
        
        # Common lease section headers (case-insensitive)
        # Pattern: section header followed by content until next header or end
        section_patterns = {
            "rent_payment": r"(?i)(RENT|MONTHLY PAYMENT|PAYMENT OF RENT)[\s:]+.*?(?=\n[A-Z\s]{3,}:|$)",
            "security_deposit": r"(?i)(SECURITY DEPOSIT|DEPOSIT)[\s:]+.*?(?=\n[A-Z\s]{3,}:|$)",
            "maintenance": r"(?i)(MAINTENANCE|REPAIRS|UPKEEP)[\s:]+.*?(?=\n[A-Z\s]{3,}:|$)",
            "termination": r"(?i)(TERMINATION|ENDING|BREAKING|EARLY TERMINATION)[\s:]+.*?(?=\n[A-Z\s]{3,}:|$)",
            "utilities": r"(?i)(UTILITIES|ELECTRIC|WATER|GAS)[\s:]+.*?(?=\n[A-Z\s]{3,}:|$)",
            "pets": r"(?i)(PETS|ANIMALS)[\s:]+.*?(?=\n[A-Z\s]{3,}:|$)",
            "entry_notice": r"(?i)(ENTRY|ACCESS|LANDLORD ENTRY|NOTICE OF ENTRY)[\s:]+.*?(?=\n[A-Z\s]{3,}:|$)",
            "late_fees": r"(?i)(LATE FEE|LATE PAYMENT|LATE CHARGE)[\s:]+.*?(?=\n[A-Z\s]{3,}:|$)",
            "renewal": r"(?i)(RENEWAL|EXTENSION)[\s:]+.*?(?=\n[A-Z\s]{3,}:|$)",
        }
        
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, text, re.DOTALL)
            if match:
                sections[section_name] = match.group(0)
        
        # If no sections detected, treat entire document as one section
        if not sections:
            sections["full_document"] = text
            
        return sections
    
    def chunk_document(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split document into chunks with metadata.
        
        Strategy: First detect sections, then chunk each section separately.
        This keeps related content together.
        
        Args:
            text: Full document text
            metadata: Base metadata to attach to all chunks
            
        Returns:
            List of dicts with 'text' and 'metadata' keys
        """
        chunks = []
        
        # First detect sections
        sections = self.detect_sections(text)
        
        # Chunk each section separately
        for section_name, section_text in sections.items():
            section_chunks = self.text_splitter.split_text(section_text)
            
            for i, chunk_text in enumerate(section_chunks):
                # Build metadata for this chunk
                chunk_metadata = metadata.copy() if metadata else {}
                chunk_metadata.update({
                    "section": section_name,
                    "chunk_index": i,
                    "section_total_chunks": len(section_chunks)
                })
                
                chunks.append({
                    "text": chunk_text,
                    "metadata": chunk_metadata
                })
        
        return chunks
    
    def process_lease_pdf(self, pdf_path: str, lease_metadata: Dict = None) -> List[Dict]:
        """
        Complete processing pipeline for a lease PDF.
        
        This is the main entry point you'll use.
        
        Args:
            pdf_path: Path to lease PDF
            lease_metadata: Optional metadata (state, lease_type, etc.)
            
        Returns:
            List of chunks ready for embedding
        """
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        
        # Add file metadata
        base_metadata = lease_metadata or {}
        base_metadata["source_file"] = pdf_path
        base_metadata["total_pages"] = text.count("--- PAGE")
        
        # Chunk with section detection
        chunks = self.chunk_document(text, base_metadata)
        
        print(f"Processed {pdf_path}:")
        print(f"  - Extracted {len(text)} characters")
        print(f"  - Detected {len(set(c['metadata']['section'] for c in chunks))} sections")
        print(f"  - Created {len(chunks)} chunks")
        
        return chunks

# Example usage and testing
if __name__ == "__main__":
    processor = LeaseDocumentProcessor()
    
    # Test with a sample lease (you'll need to add a sample PDF)
    # For testing, you can download a sample lease from:
    # https://eforms.com/rental/ca/
    
    sample_pdf = "data/leases/sample_lease.pdf"
    
    if os.path.exists(sample_pdf):
        chunks = processor.process_lease_pdf(
            sample_pdf,
            lease_metadata={"state": "california", "lease_type": "residential"}
        )
        
        print(f"\nFirst chunk preview:")
        print(f"Section: {chunks[0]['metadata']['section']}")
        print(f"Text: {chunks[0]['text'][:200]}...")
    else:
        print(f"Please add a sample PDF to {sample_pdf} for testing")
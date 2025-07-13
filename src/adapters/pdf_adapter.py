"""PDF document adapter for resume parsing."""

import PyPDF2
from typing import Optional, Dict, Any
from pathlib import Path


class PDFAdapter:
    """Adapter for parsing PDF resume documents."""
    
    def __init__(self):
        self.supported_extensions = ['.pdf']
    
    def can_handle(self, file_path: str) -> bool:
        """Check if this adapter can handle the given file."""
        return Path(file_path).suffix.lower() in self.supported_extensions
    
    def extract_text(self, file_path: str) -> str:
        """Extract text content from PDF file."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {e}")
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from PDF file."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata = {
                    'num_pages': len(pdf_reader.pages),
                    'file_size': Path(file_path).stat().st_size,
                    'filename': Path(file_path).name
                }
                return metadata
        except Exception as e:
            raise ValueError(f"Failed to extract metadata from PDF: {e}") 
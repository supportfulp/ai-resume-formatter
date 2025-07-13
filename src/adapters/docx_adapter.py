"""DOCX document adapter for resume parsing."""

from docx import Document
from typing import Dict, Any
from pathlib import Path


class DOCXAdapter:
    """Adapter for parsing DOCX resume documents."""
    
    def __init__(self):
        self.supported_extensions = ['.docx', '.doc']
    
    def can_handle(self, file_path: str) -> bool:
        """Check if this adapter can handle the given file."""
        return Path(file_path).suffix.lower() in self.supported_extensions
    
    def extract_text(self, file_path: str) -> str:
        """Extract text content from DOCX file."""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise ValueError(f"Failed to extract text from DOCX: {e}")
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from DOCX file."""
        try:
            doc = Document(file_path)
            metadata = {
                'num_paragraphs': len(doc.paragraphs),
                'file_size': Path(file_path).stat().st_size,
                'filename': Path(file_path).name
            }
            return metadata
        except Exception as e:
            raise ValueError(f"Failed to extract metadata from DOCX: {e}") 
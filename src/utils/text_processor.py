"""Text processing utilities for resume content."""

import re
from typing import List, Dict, Any
from pathlib import Path


class TextProcessor:
    """Utility class for text processing operations."""
    
    def __init__(self):
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        self.url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might interfere with parsing
        text = re.sub(r'[^\w\s@.-]', ' ', text)
        return text.strip()
    
    def extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text."""
        return re.findall(self.email_pattern, text)
    
    def extract_phones(self, text: str) -> List[str]:
        """Extract phone numbers from text."""
        return re.findall(self.phone_pattern, text)
    
    def extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text."""
        return re.findall(self.url_pattern, text)
    
    def extract_skills(self, text: str, skill_keywords: List[str]) -> List[str]:
        """Extract skills from text based on keywords."""
        found_skills = []
        text_lower = text.lower()
        
        for skill in skill_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def split_into_sections(self, text: str) -> Dict[str, str]:
        """Split resume text into sections."""
        sections = {}
        
        # Common section headers
        section_patterns = {
            'experience': r'(?i)(experience|work\s+history|employment)',
            'education': r'(?i)(education|academic)',
            'skills': r'(?i)(skills|technical\s+skills|competencies)',
            'summary': r'(?i)(summary|objective|profile)',
            'certifications': r'(?i)(certifications|certificates)',
            'languages': r'(?i)(languages|language\s+skills)'
        }
        
        lines = text.split('\n')
        current_section = 'header'
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line is a section header
            section_found = False
            for section_name, pattern in section_patterns.items():
                if re.search(pattern, line):
                    if current_content:
                        sections[current_section] = '\n'.join(current_content)
                    current_section = section_name
                    current_content = []
                    section_found = True
                    break
            
            if not section_found:
                current_content.append(line)
        
        # Add the last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def validate_file_path(self, file_path: str) -> bool:
        """Validate if file exists and is readable."""
        path = Path(file_path)
        return path.exists() and path.is_file() and path.stat().st_size > 0
    
    def get_file_extension(self, file_path: str) -> str:
        """Get file extension."""
        return Path(file_path).suffix.lower()
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file operations."""
        # Remove or replace unsafe characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        return sanitized.strip() 
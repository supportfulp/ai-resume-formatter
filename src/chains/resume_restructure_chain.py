"""Resume restructuring chain for predefined template formatting."""

import json
import re
from typing import Dict, Any, Optional
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI

from ..models.resume_models import ResumeData, ResumeProcessingRequest, ResumeProcessingResponse
from ..prompts.resume_restructure_prompts import RESUME_RESTRUCTURE_PROMPT
from ..adapters.pdf_adapter import PDFAdapter
from ..adapters.docx_adapter import DOCXAdapter
from ..utils.text_processor import TextProcessor
from langchain.prompts import PromptTemplate


class ResumeRestructureChain:
    """Chain for restructuring resumes according to predefined template."""
    
    def __init__(self, api_key: Optional[str] = None, custom_prompt: Optional[str] = None):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.1,
            google_api_key=api_key
        )
        
        # Use custom prompt if provided, otherwise use default
        if custom_prompt:
            self.prompt_template = PromptTemplate(
                input_variables=["resume_data", "reference_number"],
                template=custom_prompt
            )
        else:
            self.prompt_template = RESUME_RESTRUCTURE_PROMPT
        
        # Initialize the restructuring chain
        self.restructure_chain = self.prompt_template | self.llm
        
        # Initialize adapters
        self.pdf_adapter = PDFAdapter()
        self.docx_adapter = DOCXAdapter()
        
        # Initialize utilities
        self.text_processor = TextProcessor()
    
    def _get_adapter(self, file_path: str):
        """Get appropriate adapter for file type."""
        if self.pdf_adapter.can_handle(file_path):
            return self.pdf_adapter
        elif self.docx_adapter.can_handle(file_path):
            return self.docx_adapter
        else:
            raise ValueError(f"Unsupported file type: {file_path}")
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from document."""
        adapter = self._get_adapter(file_path)
        return adapter.extract_text(file_path)
    
    def _extract_structured_data(self, text: str) -> ResumeData:
        """Extract structured data from resume text using a simpler approach."""
        # Use the text processor for better extraction
        emails = self.text_processor.extract_emails(text)
        phones = self.text_processor.extract_phones(text)
        urls = self.text_processor.extract_urls(text)
        
        # Split text into sections
        sections = self.text_processor.split_into_sections(text)
        
        # Extract basic info
        name = ""
        email = emails[0] if emails else "unknown@example.com"
        phone = phones[0] if phones else None
        location = ""
        skills = []
        experience = []
        education = []
        languages = []
        
        # Try to extract name from header section
        if 'header' in sections:
            header_lines = sections['header'].split('\n')
            for line in header_lines:
                line = line.strip()
                if line and not any(char in line for char in ['@', '+', 'http', 'www', '.com']):
                    # Likely a name if it doesn't contain contact info
                    name = line
                    break
        
        # Extract skills from skills section
        if 'skills' in sections:
            skills_text = sections['skills']
            # Split by common delimiters
            skill_parts = re.split(r'[,;•\n]', skills_text)
            skills = [skill.strip() for skill in skill_parts if skill.strip() and len(skill.strip()) > 1]
        
        # Extract languages from languages section
        if 'languages' in sections:
            languages_text = sections['languages']
            language_parts = re.split(r'[,;•\n]', languages_text)
            languages = [lang.strip() for lang in language_parts if lang.strip() and len(lang.strip()) > 1]
        
        # Create basic ResumeData object
        return ResumeData(
            name=name or "Unknown",
            email=email,
            phone=phone,
            location=location,
            skills=skills,
            experience=[],
            education=[],
            languages=languages,
            certifications=[],
            summary=None
        )
    
    def _generate_reference_number(self, name: str) -> str:
        """Generate a reference number based on name in format XXX-ABC."""
        # Split name into parts
        name_parts = name.split()
        
        if len(name_parts) < 2:
            # Fallback if only one name part
            first_name = name_parts[0] if name_parts else "X"
            last_name = name_parts[0] if name_parts else "X"
        else:
            first_name = name_parts[0]
            last_name = name_parts[-1]  # Last part is surname
        
        # Generate reference number: XXX-ABC
        # A: first letter in the first name
        # B: first letter in the last name
        # C: last letter in the last name
        a = first_name[0].upper() if first_name else "X"
        b = last_name[0].upper() if last_name else "X"
        c = last_name[-1].upper() if last_name else "X"
        
        # Generate XXX part (could be initials or random)
        initials = ''.join([word[0].upper() for word in name_parts[:3]])  # First 3 initials
        xxx = initials.ljust(3, 'X')[:3]  # Pad to 3 chars, max 3 chars
        
        return f"{xxx}-{a}{b}{c}"
    
    def _calculate_years_experience(self, experience: list) -> int:
        """Calculate total years of experience."""
        if not experience:
            return 0
        
        # Simple calculation - in production you'd want more sophisticated date parsing
        return len(experience) * 2  # Rough estimate
    
    def restructure(self, request: ResumeProcessingRequest, reference_number: Optional[str] = None) -> str:
        """Main restructuring pipeline."""
        # Extract text from document
        original_text = self._extract_text(request.file_path)
        
        # print(f"Original text: {original_text}")
        
        # Extract structured data
        extracted_data = self._extract_structured_data(original_text)
        
        # print(f"Extracted data: {extracted_data}")
        
        # Generate reference number if not provided
        if not reference_number:
            reference_number = self._generate_reference_number(extracted_data.name)
        
        # Prepare data for restructuring
        resume_data = {
            "name": extracted_data.name,
            "email": extracted_data.email,
            "phone": extracted_data.phone,
            "location": extracted_data.location,
            "summary": extracted_data.summary,
            "experience": [exp.dict() for exp in extracted_data.experience],
            "education": [edu.dict() for edu in extracted_data.education],
            "skills": extracted_data.skills,
            "certifications": extracted_data.certifications,
            "languages": extracted_data.languages,
            "original_text": original_text
        }
        print(f"Resume data: {resume_data}")
        
        try:
            # Restructure using the LLM chain
            result = self.restructure_chain.invoke({
                "resume_data": json.dumps(resume_data, indent=2),
                "reference_number": reference_number
            })
            
            # Extract the formatted content
            formatted_resume = result.content if hasattr(result, 'content') else str(result)
            
            return formatted_resume.strip()
            
        except Exception as e:
            print(f"Error during restructuring: {e}")
            raise ValueError(f"Failed to restructure resume: {e}")
    
    def restructure_from_data(self, resume_data: ResumeData, reference_number: Optional[str] = None) -> str:
        """Restructure from already extracted ResumeData."""
        if not reference_number:
            reference_number = self._generate_reference_number(resume_data.name)
        
        # Prepare data for restructuring
        data_dict = {
            "name": resume_data.name,
            "email": resume_data.email,
            "phone": resume_data.phone,
            "location": resume_data.location,
            "summary": resume_data.summary,
            "experience": [exp.dict() for exp in resume_data.experience],
            "education": [edu.dict() for edu in resume_data.education],
            "skills": resume_data.skills,
            "certifications": [cert.dict() for cert in resume_data.certifications],
            "languages": resume_data.languages
        }
        
        try:
            # Restructure using the LLM chain
            result = self.restructure_chain.invoke({
                "resume_data": json.dumps(data_dict, indent=2),
                "reference_number": reference_number
            })
            
            # Store usage metadata for later access
            self.last_usage_metadata = getattr(result, 'usage_metadata', {})
            print(f"Restructure usage metadata: {self.last_usage_metadata}")
            
            # Extract the formatted content
            formatted_resume = result.content if hasattr(result, 'content') else str(result)
            
            return formatted_resume.strip()
            
        except Exception as e:
            print(f"Error during restructuring: {e}")
            raise ValueError(f"Failed to restructure resume: {e}") 
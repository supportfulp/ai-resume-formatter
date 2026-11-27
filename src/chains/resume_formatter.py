"""Main resume formatting chain using LangChain."""

import json
import re
from typing import Dict, Any, Optional
from langchain_core.output_parsers import PydanticOutputParser

from ..llm import make_llm, response_text
from ..models.resume_models import ResumeData, ResumeProcessingRequest, ResumeProcessingResponse
from ..prompts.resume_prompts import (
    EXTRACT_INFO_PROMPT,
    ENHANCE_CONTENT_PROMPT,
    FORMAT_RESUME_PROMPT,
    ATS_OPTIMIZE_PROMPT
)
from ..adapters.pdf_adapter import PDFAdapter
from ..adapters.docx_adapter import DOCXAdapter
from ..utils.text_processor import TextProcessor


class ResumeFormatter:
    """Main resume formatting chain."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.llm = make_llm(api_key)
        
        # Initialize chains using new RunnableSequence API
        self.extract_chain = EXTRACT_INFO_PROMPT | self.llm
        self.enhance_chain = ENHANCE_CONTENT_PROMPT | self.llm
        self.format_chain = FORMAT_RESUME_PROMPT | self.llm
        self.ats_chain = ATS_OPTIMIZE_PROMPT | self.llm
        
        # Initialize adapters
        self.pdf_adapter = PDFAdapter()
        self.docx_adapter = DOCXAdapter()
        
        # Initialize utilities
        self.text_processor = TextProcessor()
        
        # Output parser
        self.output_parser = PydanticOutputParser(pydantic_object=ResumeData)
    
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
        """Extract structured data from resume text."""
        # try:
        result = self.extract_chain.invoke({"resume_text": text})
        print(f"Raw Gemini output: {result}")
        
        # Store usage metadata for later access
        self.last_usage_metadata = getattr(result, 'usage_metadata', {})
        print(f"Extract usage metadata: {self.last_usage_metadata}")
        
        # Clean the response - remove markdown formatting if present
        content = response_text(result)
        content = content.strip()
        
        # Try to extract JSON from the response
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            data = json.loads(json_str)
        else:
            # If no JSON found, try parsing the entire response
            data = json.loads(content)
        
        # Gemini 3.x sometimes writes missing values as the string "null"
        data = self._normalize_null_strings(data)

        # Clean up null values and provide defaults
        if data.get('email') is None:
            data['email'] = None  # This will be handled by Optional[EmailStr]
        
        if data.get('name') is None:
            data['name'] = "Unknown"
        
        # Ensure lists are not None
        if data.get('experience') is None:
            data['experience'] = []
        if data.get('education') is None:
            data['education'] = []
        if data.get('skills') is None:
            data['skills'] = []
        if data.get('certifications') is None:
            data['certifications'] = []
        if data.get('languages') is None:
            data['languages'] = []
        
        # Handle null company names in experience
        for exp in data.get('experience', []):
            if exp.get('company') is None:
                exp['company'] = 'Self-employed'
        
        # Convert date fields from integers to strings
        self._convert_date_fields(data)
        
        return ResumeData(**data)
        # except Exception as e:
        #     print(f"Error parsing Gemini response: {e}")
        #     print(f"Response content: {content if 'content' in locals() else 'No content'}")
        #     raise ValueError(f"Failed to extract structured data: {e}")
    
    @classmethod
    def _normalize_null_strings(cls, value):
        """Turn "null"/"none"/"n/a"/"" strings into real None, recursively."""
        if isinstance(value, dict):
            return {k: cls._normalize_null_strings(v) for k, v in value.items()}
        if isinstance(value, list):
            cleaned = (cls._normalize_null_strings(v) for v in value)
            return [v for v in cleaned if v is not None]
        if isinstance(value, str) and value.strip().lower() in ("null", "none", "n/a", ""):
            return None
        return value

    def _enhance_content(self, text: str, target_role: Optional[str] = None) -> str:
        """Enhance resume content."""
        if not target_role:
            return text
        
        try:
            result = self.enhance_chain.invoke({
                "resume_text": text,
                "target_role": target_role
            })
            
            # Store usage metadata
            self.last_enhance_usage = getattr(result, 'usage_metadata', {})
            print(f"Enhance usage metadata: {self.last_enhance_usage}")
            
            return response_text(result)
        except Exception as e:
            print(f"Warning: Content enhancement failed: {e}")
            return text
    
    def _format_resume(self, data: ResumeData, template_style: str) -> str:
        """Format resume according to template style."""
        try:
            result = self.format_chain.invoke({
                "resume_data": data.model_dump_json(),
                "template_style": template_style
            })
            
            # Store usage metadata
            self.last_format_usage = getattr(result, 'usage_metadata', {})
            print(f"Format usage metadata: {self.last_format_usage}")
            
            return response_text(result)
        except Exception as e:
            raise ValueError(f"Failed to format resume: {e}")
    
    def _optimize_for_ats(self, text: str, job_description: str) -> str:
        """Optimize resume for ATS."""
        try:
            result = self.ats_chain.invoke({
                "resume_text": text,
                "target_role": text,
                "job_description": job_description
            })
            
            # Store usage metadata
            self.last_ats_usage = getattr(result, 'usage_metadata', {})
            print(f"ATS usage metadata: {self.last_ats_usage}")
            
            return response_text(result)
        except Exception as e:
            print(f"Warning: ATS optimization failed: {e}")
            return text
    
    def format(self, request: ResumeProcessingRequest) -> ResumeProcessingResponse:
        """Main formatting pipeline."""
        # Initialize usage tracking
        total_usage = {
            'input_tokens': 0,
            'output_tokens': 0,
            'total_tokens': 0
        }
        
        # Extract text from document
        if request.content:
            original_text = request.content
        else:
            original_text = self._extract_text(request.file_path)
        
        # Extract structured data
        extracted_data = self._extract_structured_data(original_text)
        
        # Add usage from extraction
        if hasattr(self, 'last_usage_metadata') and self.last_usage_metadata:
            total_usage['input_tokens'] += self.last_usage_metadata.get('input_tokens', 0)
            total_usage['output_tokens'] += self.last_usage_metadata.get('output_tokens', 0)
            total_usage['total_tokens'] += self.last_usage_metadata.get('total_tokens', 0)
            print(f"Added extraction usage: {self.last_usage_metadata}")
        
        # Enhance content if requested
        enhanced_text = None
        if request.enhance_content:
            enhanced_text = self._enhance_content(
                original_text, 
                request.target_role
            )
            # Add usage from enhancement
            if hasattr(self, 'last_enhance_usage') and self.last_enhance_usage:
                total_usage['input_tokens'] += self.last_enhance_usage.get('input_tokens', 0)
                total_usage['output_tokens'] += self.last_enhance_usage.get('output_tokens', 0)
                total_usage['total_tokens'] += self.last_enhance_usage.get('total_tokens', 0)
                print(f"Added enhancement usage: {self.last_enhance_usage}")
        
        # Format resume
        formatted_resume = self._format_resume(
            extracted_data, 
            request.template_style
        )
        
        # Add usage from formatting
        if hasattr(self, 'last_format_usage') and self.last_format_usage:
            total_usage['input_tokens'] += self.last_format_usage.get('input_tokens', 0)
            total_usage['output_tokens'] += self.last_format_usage.get('output_tokens', 0)
            total_usage['total_tokens'] += self.last_format_usage.get('total_tokens', 0)
            print(f"Added format usage: {self.last_format_usage}")
        
        # ATS optimization if requested
        if request.ats_optimize and request.job_description:
            formatted_resume = self._optimize_for_ats(
                formatted_resume,
                request.job_description
            )
            # Add usage from ATS optimization
            if hasattr(self, 'last_ats_usage') and self.last_ats_usage:
                total_usage['input_tokens'] += self.last_ats_usage.get('input_tokens', 0)
                total_usage['output_tokens'] += self.last_ats_usage.get('output_tokens', 0)
                total_usage['total_tokens'] += self.last_ats_usage.get('total_tokens', 0)
                print(f"Added ATS usage: {self.last_ats_usage}")
        
        print(f"Total usage accumulated: {total_usage}")
        
        # Prepare metadata
        processing_metadata = {
            "file_path": request.file_path,
            "target_role": request.target_role,
            "template_style": request.template_style,
            "enhance_content": request.enhance_content,
            "ats_optimize": request.ats_optimize,
            "usage_metadata": total_usage
        }
        
        return ResumeProcessingResponse(
            original_text=original_text,
            extracted_data=extracted_data,
            enhanced_text=enhanced_text,
            formatted_resume=formatted_resume,
            processing_metadata=processing_metadata
        )
    
    def _convert_date_fields(self, data: dict):
        """Convert date fields from integers to strings."""
        print("🔄 Converting date fields from integers to strings...")
        
        # Convert experience dates
        if 'experience' in data and isinstance(data['experience'], list):
            for exp in data['experience']:
                if isinstance(exp, dict):
                    if 'start_date' in exp and isinstance(exp['start_date'], int):
                        exp['start_date'] = str(exp['start_date'])
                        print(f"✅ Converted experience start_date: {exp['start_date']}")
                    if 'end_date' in exp and isinstance(exp['end_date'], int):
                        exp['end_date'] = str(exp['end_date'])
                        print(f"✅ Converted experience end_date: {exp['end_date']}")
        
        # Convert education dates
        if 'education' in data and isinstance(data['education'], list):
            for edu in data['education']:
                if isinstance(edu, dict):
                    if 'start_date' in edu and isinstance(edu['start_date'], int):
                        edu['start_date'] = str(edu['start_date'])
                        print(f"✅ Converted education start_date: {edu['start_date']}")
                    if 'end_date' in edu and isinstance(edu['end_date'], int):
                        edu['end_date'] = str(edu['end_date'])
                        print(f"✅ Converted education end_date: {edu['end_date']}")
        
        if 'certifications' in data and isinstance(data['certifications'], list):
            print(f"✅ Converting certifications year: {data['certifications']}")
            for cert in data['certifications']:
                if isinstance(cert, dict):
                    if 'year' in cert and isinstance(cert['year'], int):
                        cert['year'] = str(cert['year'])
                    # if year is None, set it to 'N/A'
                    if cert['year'] is None:
                        cert['year'] = 'N/A'
                    if cert['issuer'] is None:
                        cert['issuer'] = 'N/A'
            print(f"✅ Converted certifications year: {data['certifications']}")
        
        print("✅ Date field conversion completed")
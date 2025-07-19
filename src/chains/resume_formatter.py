"""Main resume formatting chain using LangChain."""

import json
import re
from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser

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
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.1,
            google_api_key=api_key
        )
        
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
        try:
            result = self.extract_chain.invoke({"resume_text": text})
            print(f"Raw Gemini output: {result}")
            
            # Clean the response - remove markdown formatting if present
            content = result.content if hasattr(result, 'content') else str(result)
            content = content.strip()
            
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
            else:
                # If no JSON found, try parsing the entire response
                data = json.loads(content)
            
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
            
            return ResumeData(**data)
        except Exception as e:
            print(f"Error parsing Gemini response: {e}")
            print(f"Response content: {content if 'content' in locals() else 'No content'}")
            raise ValueError(f"Failed to extract structured data: {e}")
    
    def _enhance_content(self, text: str, target_role: Optional[str] = None) -> str:
        """Enhance resume content."""
        if not target_role:
            return text
        
        try:
            result = self.enhance_chain.invoke({
                "resume_text": text,
                "target_role": target_role
            })
            return result.content if hasattr(result, 'content') else str(result)
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
            return result.content if hasattr(result, 'content') else str(result)
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
            return result.content if hasattr(result, 'content') else str(result)
        except Exception as e:
            print(f"Warning: ATS optimization failed: {e}")
            return text
    
    def format(self, request: ResumeProcessingRequest) -> ResumeProcessingResponse:
        """Main formatting pipeline."""
        # Extract text from document
        if request.content:
            original_text = request.content
        else:
            original_text = self._extract_text(request.file_path)
        
        # Extract structured data
        extracted_data = self._extract_structured_data(original_text)
        
        # Enhance content if requested
        enhanced_text = None
        if request.enhance_content:
            enhanced_text = self._enhance_content(
                original_text, 
                request.target_role
            )
        
        # Format resume
        formatted_resume = self._format_resume(
            extracted_data, 
            request.template_style
        )
        
        # ATS optimization if requested
        if request.ats_optimize and request.job_description:
            formatted_resume = self._optimize_for_ats(
                formatted_resume,
                request.job_description
            )
        
        # Prepare metadata
        processing_metadata = {
            "file_path": request.file_path,
            "target_role": request.target_role,
            "template_style": request.template_style,
            "enhance_content": request.enhance_content,
            "ats_optimize": request.ats_optimize
        }
        
        return ResumeProcessingResponse(
            original_text=original_text,
            extracted_data=extracted_data,
            enhanced_text=enhanced_text,
            formatted_resume=formatted_resume,
            processing_metadata=processing_metadata
        ) 
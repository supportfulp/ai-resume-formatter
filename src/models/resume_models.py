"""Pydantic models for resume data structures."""

from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import date


class Experience(BaseModel):
    """Work experience model."""
    company: str
    title: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    achievements: Optional[List[str]] = None


class Education(BaseModel):
    """Education model."""
    degree: str
    institution: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[float] = None
    relevant_coursework: Optional[List[str]] = None


class ResumeData(BaseModel):
    """Complete resume data model."""
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    website: Optional[str] = None
    summary: Optional[str] = None
    reference_number: Optional[str] = None
    experience: List[Experience] = []
    education: List[Education] = []
    skills: List[str] = []
    certifications: List[str] = []
    languages: List[str] = []
    projects: Optional[List[Dict[str, Any]]] = None


class ResumeProcessingRequest(BaseModel):
    """Request model for resume processing."""
    file_path: str
    content: Optional[str] = None
    target_role: Optional[str] = None
    template_style: Optional[str] = "professional"
    enhance_content: bool = True
    ats_optimize: bool = False
    job_description: Optional[str] = None


class ResumeProcessingResponse(BaseModel):
    """Response model for resume processing."""
    original_text: str
    extracted_data: ResumeData
    enhanced_text: Optional[str] = None
    formatted_resume: str
    processing_metadata: Dict[str, Any] 
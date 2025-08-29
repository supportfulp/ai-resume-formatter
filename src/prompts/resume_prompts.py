"""Prompt templates for resume processing tasks."""

from langchain.prompts import PromptTemplate


# Extract structured information from resume text
EXTRACT_INFO_PROMPT = PromptTemplate(
    input_variables=["resume_text"],
    template="""
    You are a resume parser. Extract the following information from this resume and return ONLY a valid JSON object with no additional text, markdown formatting, or explanations.

    Required JSON structure:
    {{
        "name": "Full name (always make the first letter of the first name and last name capitalized)",
        "email": "email@example.com", 
        "phone": "phone number or null",
        "location": "City, State/Country or null",
        "summary": "Professional summary or null",
        "communcation_skills": "Communication skills or null",
        "reference_number": "Reference number or null",
        "experience": [
            {{
                "company": "Company name, Country",
                "title": "Job title", 
                "start_date": "Start date (year)",
                "end_date": "End date (year) or null",
                "achievements": ["achievement1", "achievement2"] or null (if the current job talk in the achievements section in the past tense, then the previous jobs should be in the past tense and the current job should be in the present continuous tense.)
            }}
        ],
        "education": [
            {{
                "degree": "Degree name",
                "institution": "Institution name",
                "start_date": "Start date (year)",
                "end_date": "End date (year) or null",
                "gpa": GPA or null,
                "relevant_coursework": ["course1", "course2"] or null 
            }}
        ],
        "certifications": [
            {{
                "name": "Certification name",
                "year": "Year of certification",
                "issuer": "Issuing organization"
            }}
        ],
        "skills": ["skill1", "skill2", "skill3"],
        "languages": ["language1", "language2"] or [] (always include "English" by default then add other languages if mentioned)
    }}

    Resume text:
    {resume_text}

    IMPORTANT: Return ONLY the JSON object, no other text, no markdown formatting, no explanations.
    IMPORTANT: The Skills should be ordered by the most relevant to the least relevant to the person's experience.
    IMPORTANT: In the experience section, if the current job talk in the achievements section in the past tense, then the previous jobs should be in the past tense and the current job should be in the present tense.
    """
)

# Enhance resume content
ENHANCE_CONTENT_PROMPT = PromptTemplate(
    input_variables=["resume_text", "target_role"],
    template="""
    Enhance this resume content to better match the target role. 
    Focus on:
    - Improving action verbs and achievements
    - Quantifying results where possible
    - Aligning skills with job requirements
    - Making descriptions more impactful
    
    Target role: {target_role}
    
    Original resume:
    {resume_text}
    
    Return the enhanced resume content.
    """
)

# Format resume for specific template
FORMAT_RESUME_PROMPT = PromptTemplate(
    input_variables=["resume_data", "template_style"],
    template="""
    Format this resume data according to the specified template style.
    
    Template style: {template_style}
    
    Resume data:
    {resume_data}
    
    Return the formatted resume in the requested style.
    """
)

# Generate ATS-friendly resume
ATS_OPTIMIZE_PROMPT = PromptTemplate(
    input_variables=["resume_text", "job_description"],
    template="""
    Optimize this resume for ATS (Applicant Tracking System) compatibility.
    
    Job description:
    {job_description}
    
    Resume:
    {resume_text}
    
    Make the following improvements:
    1. Include relevant keywords from the job description
    2. Use standard section headings
    3. Ensure proper formatting
    4. Remove any graphics or unusual formatting
    5. Use bullet points for achievements
    
    Return the ATS-optimized resume.
    """
) 
"""Prompt templates for resume restructuring according to predefined template."""

from langchain.prompts import PromptTemplate


# Main resume restructuring prompt
RESUME_RESTRUCTURE_PROMPT = PromptTemplate(
    input_variables=["resume_data", "reference_number"],
    template="""
You are a professional resume restructuring expert. Transform the provided resume data into a clean, professionally structured document following the exact template format.

System Instructions:
- Create a document that is clean, easy to scan, and highlights the candidate's most relevant qualifications
- Adhere strictly to the formatting, section ordering, and content style
- Rewrite raw text to be more direct and impactful
- Maintain professional and formal tone throughout

Template Structure:
1. Header: Full name + Reference number
2. Summary: Job title with years of experience and their primary areas of expertise identified from the resume data + communication skills + languages
3. Key Skills: Technical skills in multi-column format
4. Experience: Reverse chronological order with achievements (consolidate multiple positions at same company into single entries)
5. Education: Degrees in reverse chronological order

Reference Number: {reference_number}

Resume Data:
{resume_data}

Generate the restructured resume following the exact template format below:

[Full Name]
[Ref#: {reference_number}]

[Job Title] with [Number] years of experience.
Good communication skills.
Fluent in [Language 1, Language 2, ...].

Key Skills

[Skill 1] \t\t [Skill 2, Skill 3] \t\t [Skill 4]
[Skill 5] \t\t [Skill 6] \t\t\t [Skill 7]
[Skill 8] \t\t [Skill 9, Skill 10] \t\t [Skill 11]
...

Experience

[Year-Year]
[Job Title] [Company Name], [Location]

[Key achievement or responsibility statement.]

[Key achievement or responsibility statement.]

[Key achievement or responsibility statement.]

[Year-Year]
[Job Title] [Company Name], [Location]

[Key achievement or responsibility statement.]

[Key achievement or responsibility statement.]

Education

[Year] [Degree], [University Name], [Location]
[Year] [Degree], [University Name], [Location]

IMPORTANT: 
- Do not include contact information (email, phone, social media)
- Do not include personal photos
- Use bullet points only for experience achievements
- Group related skills on the same line where appropriate
- Calculate years of experience from the most recent position
- If no formal degree but has certifications, use "Education & Certifications" section
- **CONSOLIDATE MULTIPLE POSITIONS in the same company**: If the candidate has multiple positions at the same company, combine them into one entry with the total date range and most senior title. For example:
  * Multiple positions like "Senior Technical Consultant (2022), Technical Consultant (2021), Software Developer (2018-2020)" at ITG should become:
  * "2018-2022 Senior Technical Consultant & Software Engineer • ITG, Lebanon"
  * Include the most significant achievements from all positions in the bullet points
- **USE ONLY PROVIDED INFORMATION**: Do not make up, invent, or add any information that is not present in the resume data. Only use the facts, dates, companies, titles, and achievements that are explicitly provided in the input data
- Return only the formatted resume, no explanations or additional text
- Do Not Skip any experience or education entries
"""
)


# Alternative prompt for specific template variations
RESUME_TEMPLATE_VARIANT_PROMPT = PromptTemplate(
    input_variables=["resume_data", "reference_number", "template_style"],
    template="""
Restructure this resume according to the specified template style.

Template Style: {template_style}
Reference Number: {reference_number}

Resume Data:
{resume_data}

Follow the exact template format and return only the formatted resume.
"""
) 
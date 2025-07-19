import streamlit as st
import json
import tempfile
import os
from pathlib import Path
import sys
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.chains.resume_restructure_chain import ResumeRestructureChain
from src.chains.resume_formatter import ResumeFormatter
from src.models.resume_models import ResumeProcessingRequest


def process_resume_3_steps(pdf_file, api_key: str) -> Dict[str, Any]:
    """Process resume through 3 steps and return results."""
    
    # Initialize chains
    restructure_chain = ResumeRestructureChain(api_key=api_key)
    formatter = ResumeFormatter(api_key=api_key)
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(pdf_file.getvalue())
        temp_path = tmp_file.name
    
    try:
        # Step 1: Extract structured data
        request = ResumeProcessingRequest(
            file_path=temp_path,
            target_role="Software Engineer",
            template_style="professional",
            enhance_content=False,
            ats_optimize=False
        )
        
        step1_result = formatter.format(request)
        extracted_data = step1_result.extracted_data
        
        # Step 2: First restructuring
        restructured_from_data = restructure_chain.restructure_from_data(
            extracted_data, 
            reference_number="SDA02-AMH"
        )
        
        # Step 3: Second restructuring - process Step 2 output through formatter again
        step3_request = ResumeProcessingRequest(
            file_path="",
            content=restructured_from_data,
            target_role="Software Engineer",
            template_style="professional",
            enhance_content=False,
            ats_optimize=False
        )
        
        step3_result = formatter.format(step3_request)
        
        # Prepare results
        results = {
            "step1_extracted_data": step1_result.extracted_data.model_dump(),
            "step2_restructured_text": restructured_from_data,
            "step3_final_data": step3_result.extracted_data.model_dump(),
            "step3_final_formatted": step3_result.formatted_resume,
            "processing_metadata": {
                "original_filename": pdf_file.name,
                "target_role": "Software Engineer",
                "template_style": "professional"
            }
        }
        
        return results
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def render_editing_interface():
    """Render the editing interface with proper session state management."""
    
    # Get current data from session state
    final_data = st.session_state.edited_data
    original_results = st.session_state.original_results
    
    # Personal Information Section
    st.subheader("👤 Personal Information")
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Full Name", value=final_data.get("name", ""), key="name_input")
        email = st.text_input("Email", value=final_data.get("email", ""), key="email_input")
        phone = st.text_input("Phone", value=final_data.get("phone", ""), key="phone_input")
    
    with col2:
        location = st.text_input("Location", value=final_data.get("location", ""), key="location_input")
        linkedin = st.text_input("LinkedIn", value=final_data.get("linkedin", ""), key="linkedin_input")
        website = st.text_input("Website", value=final_data.get("website", ""), key="website_input")
    
    # Summary
    summary = st.text_area("Professional Summary", value=final_data.get("summary", ""), height=100, key="summary_input")
    
    # Experience Section
    st.subheader("💼 Work Experience")
    experiences = final_data.get("experience", [])
    
    for i, exp in enumerate(experiences):
        with st.expander(f"Experience {i+1}: {exp.get('title', 'Unknown')} at {exp.get('company', 'Unknown')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                exp['company'] = st.text_input(f"Company {i+1}", value=exp.get("company", ""), key=f"company_{i}")
                exp['title'] = st.text_input(f"Title {i+1}", value=exp.get("title", ""), key=f"title_{i}")
                exp['start_date'] = st.text_input(f"Start Date {i+1}", value=exp.get("start_date", ""), key=f"start_{i}")
            
            with col2:
                exp['end_date'] = st.text_input(f"End Date {i+1}", value=exp.get("end_date", ""), key=f"end_{i}")
            
            exp['description'] = st.text_area(f"Description {i+1}", value=exp.get("description", ""), height=100, key=f"desc_{i}")
    
    # Education Section
    st.subheader("🎓 Education")
    educations = final_data.get("education", [])
    
    for i, edu in enumerate(educations):
        with st.expander(f"Education {i+1}: {edu.get('degree', 'Unknown')} at {edu.get('institution', 'Unknown')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                edu['degree'] = st.text_input(f"Degree {i+1}", value=edu.get("degree", ""), key=f"degree_{i}")
                edu['institution'] = st.text_input(f"Institution {i+1}", value=edu.get("institution", ""), key=f"institution_{i}")
                edu['start_date'] = st.text_input(f"Start Date {i+1}", value=edu.get("start_date", ""), key=f"edu_start_{i}")
            
            with col2:
                edu['end_date'] = st.text_input(f"End Date {i+1}", value=edu.get("end_date", ""), key=f"edu_end_{i}")
                edu['gpa'] = st.number_input(f"GPA {i+1}", value=float(edu.get("gpa", 0.0)) if edu.get("gpa") else 0.0, step=0.01, key=f"gpa_{i}")
    
    # Skills Section
    st.subheader("🛠️ Skills")
    skills_text = ", ".join(final_data.get("skills", []))
    skills_input = st.text_area("Skills (comma-separated)", value=skills_text, height=80, key="skills_input")
    skills = [skill.strip() for skill in skills_input.split(",") if skill.strip()]
    
    # Languages Section
    st.subheader("🌍 Languages")
    languages_text = ", ".join(final_data.get("languages", []))
    languages_input = st.text_area("Languages (comma-separated)", value=languages_text, height=60, key="languages_input")
    languages = [lang.strip() for lang in languages_input.split(",") if lang.strip()]
    
    # Certifications Section
    st.subheader("🏆 Certifications")
    certifications_text = ", ".join(final_data.get("certifications", []))
    certifications_input = st.text_area("Certifications (comma-separated)", value=certifications_text, height=60, key="certifications_input")
    certifications = [cert.strip() for cert in certifications_input.split(",") if cert.strip()]
    
    # Save and Export buttons in the same row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save Changes", type="primary", key="save_button"):
            # Update the session state with edited values
            st.session_state.edited_data = {
                "name": name,
                "email": email,
                "phone": phone,
                "location": location,
                "linkedin": linkedin,
                "website": website,
                "summary": summary,
                "experience": experiences,
                "education": educations,
                "skills": skills,
                "languages": languages,
                "certifications": certifications,
                "projects": final_data.get("projects")
            }
            
            # Also update the results for export
            st.session_state.original_results["step3_final_data"] = st.session_state.edited_data
            st.success("✅ Changes saved successfully!")
            st.rerun()
    
    with col2:
        # Export edited JSON data
        export_data = st.session_state.edited_data
        final_filename = f"resume_data_{st.session_state.current_filename.replace('.pdf', '')}.json"
        st.download_button(
            label="📥 Download JSON",
            data=json.dumps(export_data, indent=2),
            file_name=final_filename,
            mime="application/json",
            key="download_final"
        )
    
    with col3:
        # Export formatted text
        formatted_filename = f"formatted_resume_{st.session_state.current_filename.replace('.pdf', '')}.txt"
        st.download_button(
            label="📥 Download TXT",
            data=st.session_state.original_results["step3_final_formatted"],
            file_name=formatted_filename,
            mime="text/plain",
            key="download_formatted"
        )
    
    # Display formatted resume
    st.subheader("📄 Formatted Resume Preview")
    st.text_area(
        "Formatted resume",
        value=st.session_state.original_results["step3_final_formatted"],
        height=400,
        disabled=True
    )


def main():
    st.set_page_config(
        page_title="Resume Processing Tool",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("📄 Resume Processing Tool")
    st.markdown("Upload a PDF resume and process it through our 3-step AI pipeline.")
    
    # Get API key from environment
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        st.error("❌ GOOGLE_API_KEY not found in environment variables. Please set it in your .env file or environment.")
        st.stop()
    
    # Show API key status in sidebar
    st.sidebar.header("Configuration")
    st.sidebar.success("✅ API Key loaded from environment")
    st.sidebar.info(f"Key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else '***'}")
    
    # Initialize session state
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False
    if 'current_filename' not in st.session_state:
        st.session_state.current_filename = ""
    
    # File upload
    st.header("📁 Upload Resume")
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload a PDF resume to process",
        key="file_uploader"
    )
    
    # Check if a new file was uploaded
    if uploaded_file is not None:
        # If this is a new file, reset the session state
        if st.session_state.current_filename != uploaded_file.name:
            st.session_state.current_filename = uploaded_file.name
            st.session_state.processing_complete = False
            st.session_state.edited_data = None
            st.session_state.original_results = None
        
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Show processing button if not already processed
        if not st.session_state.processing_complete:
            if st.button("🚀 Process Resume (3 Steps)", type="primary", key="process_button"):
                with st.spinner("Processing resume through 3-step pipeline..."):
                    try:
                        results = process_resume_3_steps(uploaded_file, api_key)
                        
                        # Store results in session state
                        st.session_state.edited_data = results["step3_final_data"].copy()
                        st.session_state.original_results = results.copy()
                        st.session_state.processing_complete = True
                        
                        st.success("✅ Processing complete! You can now edit the data below.")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error processing resume: {str(e)}")
                        st.exception(e)
        
        # Show editing interface if processing is complete
        if st.session_state.processing_complete and st.session_state.edited_data is not None:
            st.header("📝 Edit Resume Data")
            st.markdown("Review and edit the extracted resume information below.")
            render_editing_interface()


if __name__ == "__main__":
    main() 
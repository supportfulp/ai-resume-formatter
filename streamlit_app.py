import streamlit as st
import json
import tempfile
import os
from pathlib import Path
import sys
from typing import Dict, Any
from dotenv import load_dotenv
import hashlib
import time

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.chains.resume_restructure_chain import ResumeRestructureChain
from src.chains.resume_formatter import ResumeFormatter
from src.models.resume_models import ResumeProcessingRequest


def hash_password(password: str) -> str:
    """Hash password for secure storage."""
    return hashlib.sha256(password.encode()).hexdigest()


def hash_api_key(api_key: str) -> str:
    """Hash API key for secure storage in session state."""
    return hashlib.sha256(api_key.encode()).hexdigest()


def validate_api_key(api_key: str) -> bool:
    """Basic validation for Google API key format."""
    if not api_key:
        return False
    # Google API keys are typically 39 characters long and start with 'AI'
    return len(api_key) >= 30 and (api_key.startswith('AI') or 'google' in api_key.lower())


def create_user_account(username: str, password: str) -> bool:
    """Create a new user account (simple in-memory storage for demo)."""
    if 'users' not in st.session_state:
        st.session_state.users = {}
    
    if username in st.session_state.users:
        return False
    
    st.session_state.users[username] = {
        'password_hash': hash_password(password),
        'created_at': time.time()
    }
    return True


def verify_user_credentials(username: str, password: str) -> bool:
    """Verify user login credentials."""
    if 'users' not in st.session_state:
        return False
    
    if username not in st.session_state.users:
        return False
    
    stored_hash = st.session_state.users[username]['password_hash']
    return stored_hash == hash_password(password)


def login_page():
    """Render the login page for user authentication."""
    st.set_page_config(
        page_title="Resume Processor - Login",
        page_icon="🔐",
        layout="centered"
    )
    
    st.title("🔐 Resume Processor Login")
    st.markdown("---")
    
    # Main login interface
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        st.markdown("### Welcome Back!")
        with st.form("login_form"):
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                login_button = st.form_submit_button("🔐 Login", type="primary")
            with col2:
                if st.form_submit_button("❓ Forgot Password?"):
                    st.info("💡 For demo purposes, you can register a new account or use: username: 'demo', password: 'demo123'")
            
            if login_button:
                if not username or not password:
                    st.error("❌ Please enter both username and password!")
                elif verify_user_credentials(username, password):
                    st.session_state.user_logged_in = True
                    st.session_state.username = username
                    st.success("✅ Login successful! Redirecting to API key setup...")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password!")
    
    with tab2:
        st.markdown("### Create New Account")
        with st.form("register_form"):
            new_username = st.text_input("👤 New Username", placeholder="Choose a username")
            new_password = st.text_input("🔒 New Password", type="password", placeholder="Choose a password")
            confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password")
            
            register_button = st.form_submit_button("📝 Register", type="primary")
            
            if register_button:
                if not new_username or not new_password:
                    st.error("❌ Please fill in all fields!")
                elif new_password != confirm_password:
                    st.error("❌ Passwords don't match!")
                elif len(new_password) < 6:
                    st.error("❌ Password must be at least 6 characters!")
                elif create_user_account(new_username, new_password):
                    st.success("✅ Account created successfully! You can now login.")
                else:
                    st.error("❌ Username already exists!")
    
    # Demo account info
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
        <p>💡 <strong>Demo Account:</strong> username: 'demo', password: 'demo123'</p>
        <p>🔒 Your data is stored securely in your browser session only</p>
    </div>
    """, unsafe_allow_html=True)


def api_key_setup_page():
    """Render the API key setup page."""
    st.set_page_config(
        page_title="Resume Processor - API Key Setup",
        page_icon="🔑",
        layout="centered"
    )
    
    st.header("🔑 Google API Key Setup")
    st.markdown("---")
    
    st.markdown("""
    ### Welcome to the Resume Processor! 🤖
    
    This app uses **Google's Gemini AI** to analyze and restructure your resumes.
    
    **To get started, you'll need:**
    1. A Google API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
    2. Your resume in PDF or DOCX format
    
    **Don't have an API key?** [Get one here](https://makersuite.google.com/app/apikey) (Free tier available)
    """)
    
    # Show help info in expander
    with st.expander("ℹ️ How to get Google API Key", expanded=False):
        st.markdown("""
        **Step-by-step guide:**
        
        1. **Visit Google AI Studio**: Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
        2. **Sign in**: Use your Google account
        3. **Create API Key**: Click "Create API Key" button
        4. **Copy Key**: Copy the generated key (starts with "AIzaSy...")
        5. **Set Limits**: Go to dashboard and set usage limits
        
        **Free Tier Limits:**
        - 15 requests/minute
        - 1,500 requests/day
        - $0 cost for most users
        
        **Cost**: ~$0.001-0.003 per resume processed
        """)
    
    # API Key Input Form
    st.subheader("🔑 Enter Your API Key")
    
    # Use a simple form without complex logic
    api_key = st.text_input(
        "Google API Key",
        type="password",
        placeholder="AIzaSyC...",
        help="Your API key is stored securely in your browser session only",
        key="api_key_input"
    )
    
    # Show current API key status
    if st.session_state.get("api_key_set"):
        st.success("✅ API key is already configured!")
        if st.button("🔄 Change API Key"):
            st.session_state.api_key_set = False
            st.session_state.api_key = None
            st.rerun()
    
    # Set API Key Button
    if st.button("🔑 Set API Key", type="primary", key="set_api_key_btn"):
        if not api_key:
            st.error("❌ Please enter your Google API key!")
        elif not validate_api_key(api_key):
            st.warning("⚠️ API key format looks invalid. Please check your key.")
            st.info("💡 Google API keys typically start with 'AIzaSy' and are about 39 characters long.")
        else:
            # Store API key securely in session state
            st.session_state.api_key = api_key
            st.session_state.api_key_hash = hash_api_key(api_key)
            st.session_state.api_key_set = True
            st.session_state.api_key_setup_time = time.time()
            
            st.success("✅ API key set successfully!")
            st.balloons()
            st.rerun()
    
    # Back to login button
    if st.button("← Back to Login", key="back_to_login_btn"):
        st.session_state.user_logged_in = False
        st.session_state.username = None
        st.rerun()
    

    
    # Footer with helpful links
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
        <p>🔒 Your API key is stored securely in your browser session only</p>
        <p>💰 Free tier: 15 requests/minute, 1500 requests/day</p>
        <p>📖 <a href='https://ai.google.dev/docs' target='_blank'>Google AI Documentation</a></p>
    </div>
    """, unsafe_allow_html=True)


def logout_button():
    """Render logout button in sidebar."""
    if st.sidebar.button("🚪 Logout", type="secondary"):
        st.session_state.authenticated = False
        st.session_state.user_logged_in = False
        st.session_state.username = None
        st.session_state.api_key = None
        st.session_state.api_key_hash = None
        st.session_state.api_key_set = False
        st.session_state.api_key_setup_time = None
        st.session_state.show_api_key_setup = False
        st.rerun()


def show_user_info():
    """Show user information in sidebar."""
    if st.session_state.get("user_logged_in"):
        username = st.session_state.get("username", "User")
        st.sidebar.success(f"✅ Logged in as: {username}")
        
        # Show API key status
        if st.session_state.get("api_key_set"):
            st.sidebar.success("🔑 API Key: Configured")
            
            # Show masked API key
            api_key = st.session_state.get("api_key", "")
            if api_key:
                masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
                st.sidebar.text(f"Key: {masked_key}")
            
            # Show session time
            setup_time = st.session_state.get("api_key_setup_time")
            if setup_time:
                elapsed = time.time() - setup_time
                hours = int(elapsed // 3600)
                minutes = int((elapsed % 3600) // 60)
                st.sidebar.text(f"⏱️ Setup: {hours}h {minutes}m ago")
        else:
            st.sidebar.warning("⚠️ API Key: Not set")
        
        st.sidebar.markdown("---")


def process_resume_3_steps(pdf_file, api_key: str, custom_prompt: str = None) -> Dict[str, Any]:
    """Process resume through 3 steps and return results."""
    
    # Initialize chains
    restructure_chain = ResumeRestructureChain(api_key=api_key, custom_prompt=custom_prompt)
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
        reference_number = st.text_input("Reference Number", value=final_data.get("reference_number", ""), key="reference_number_input")
    
    with col2:
        location = st.text_input("Location", value=final_data.get("location", ""), key="location_input")
        linkedin = st.text_input("LinkedIn", value=final_data.get("linkedin", ""), key="linkedin_input")
        website = st.text_input("Website", value=final_data.get("website", ""), key="website_input")    
    # Summary
    summary = st.text_area("Professional Summary", value=final_data.get("summary", ""), height=100, key="summary_input")
    
    # Experience Section
    st.subheader("💼 Work Experience")
    experiences = final_data.get("experience", [])
    
    # Add new experience button
    if st.button("➕ Add New Experience", key="add_experience"):
        new_exp = {
            "company": "",
            "title": "",
            "start_date": "",
            "end_date": "",
            "description": ""
        }
        experiences.append(new_exp)
        st.session_state.edited_data["experience"] = experiences
        st.success("✅ New experience added!")
        st.rerun()
    
    for i, exp in enumerate(experiences):
        with st.expander(f"Experience {i+1}: {exp.get('title', 'Unknown')} at {exp.get('company', 'Unknown')}"):
            # Delete button for this experience
            if st.button(f"🗑️ Delete Experience {i+1}", key=f"delete_exp_{i}", type="secondary"):
                experiences.pop(i)
                st.session_state.edited_data["experience"] = experiences
                st.success(f"✅ Experience {i+1} deleted!")
                st.rerun()
            
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
    
    # Add new education button
    if st.button("➕ Add New Education", key="add_education"):
        new_edu = {
            "degree": "",
            "institution": "",
            "start_date": "",
            "end_date": "",
            "gpa": None,
            "relevant_coursework": []
        }
        educations.append(new_edu)
        st.session_state.edited_data["education"] = educations
        st.success("✅ New education added!")
        st.rerun()
    
    for i, edu in enumerate(educations):
        with st.expander(f"Education {i+1}: {edu.get('degree', 'Unknown')} at {edu.get('institution', 'Unknown')}"):
            # Delete button for this education
            if st.button(f"🗑️ Delete Education {i+1}", key=f"delete_edu_{i}", type="secondary"):
                educations.pop(i)
                st.session_state.edited_data["education"] = educations
                st.success(f"✅ Education {i+1} deleted!")
                st.rerun()
            
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
                "projects": final_data.get("projects"),
                "reference_number": reference_number
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
    
    # Initialize demo user if not exists
    if 'users' not in st.session_state:
        st.session_state.users = {}
        # Create demo account
        demo_password_hash = hash_password("demo123")
        st.session_state.users['demo'] = {
            'password_hash': demo_password_hash,
            'created_at': time.time()
        }
    
    # Authentication flow
    if not st.session_state.get("user_logged_in", False):
        # User not logged in - show login page
        login_page()
        st.stop()
    elif not st.session_state.get("api_key_set", False):
        # User logged in but no API key - show API key setup
        api_key_setup_page()
        st.stop()
    else:
        # User logged in and API key set - show main app
        st.title("📄 Resume Processing Tool")
        st.markdown("Upload a PDF resume and process it through our 3-step AI pipeline.")
        
        # Show user info in sidebar
        show_user_info()
        logout_button()

    # Prompt editing section in sidebar
    st.sidebar.header("🔧 AI Prompt Settings")
    
    # Load default prompt
    from src.prompts.resume_restructure_prompts import RESUME_RESTRUCTURE_PROMPT
    default_prompt = RESUME_RESTRUCTURE_PROMPT.template
    
    # Show prompt status and quick actions
    current_prompt = st.session_state.get('custom_prompt', default_prompt)
    is_custom = 'custom_prompt' in st.session_state
    
    if is_custom:
        st.sidebar.success("✅ Using custom prompt")
    else:
        st.sidebar.info("ℹ️ Using default prompt")
    
    # Show a preview of the current prompt
    with st.sidebar.expander("👀 Preview Current Prompt", expanded=False):
        # Handle None case
        if current_prompt is None:
            preview_text = "No prompt available"
        else:
            preview_text = current_prompt[:500] + "..." if len(current_prompt) > 500 else current_prompt
        
        st.text_area(
            "Current Prompt",
            value=preview_text,
            height=150,
            disabled=True,
            key="prompt_preview"
        )
        if current_prompt and len(current_prompt) > 500:
            st.caption("(Showing first 500 characters)")
        
        # Debug info
        st.caption(f"Prompt length: {len(current_prompt) if current_prompt else 0} characters")
        st.caption(f"Is custom: {is_custom}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.sidebar.button("📝 Edit Prompt", key="edit_prompt_btn"):
            st.session_state['show_prompt_editor'] = True
    
    with col2:
        if st.sidebar.button("🔄 Reset", key="reset_prompt_btn"):
            if 'custom_prompt' in st.session_state:
                del st.session_state['custom_prompt']
            if 'show_prompt_editor' in st.session_state:
                del st.session_state['show_prompt_editor']
            st.sidebar.success("✅ Reset to default!")
            st.rerun()
    
    # Initialize session state
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False
    if 'current_filename' not in st.session_state:
        st.session_state.current_filename = ""
    
    # Show prompt editor if requested
    if st.session_state.get('show_prompt_editor', False):
        st.header("🔧 Customize AI Prompt")
        st.markdown("**Edit the AI prompt that guides resume restructuring. This prompt controls how your resume will be formatted and structured.**")
        
        # Load default prompt
        from src.prompts.resume_restructure_prompts import RESUME_RESTRUCTURE_PROMPT
        default_prompt = RESUME_RESTRUCTURE_PROMPT.template
        
        # Use custom prompt if available, otherwise use default
        current_prompt = st.session_state.get('custom_prompt', default_prompt)
        
        # Show current prompt status
        if 'custom_prompt' in st.session_state:
            st.info("📝 **Currently editing a custom prompt**")
        else:
            st.info("📝 **Currently editing the default prompt**")
        
        # Prompt editing interface
        edited_prompt = st.text_area(
            "AI Prompt Template",
            value=current_prompt,
            height=400,
            help="Edit the prompt that guides the AI in restructuring resumes. Use {resume_data} and {reference_number} as placeholders.",
            placeholder="Enter your custom prompt here..."
        )
        
        # Placeholder information
        with st.expander("💡 Available Placeholders", expanded=False):
            st.markdown("""
            **Use these placeholders in your prompt:**
            
            - `{resume_data}` - The structured resume data to process
            - `{reference_number}` - The reference number for the resume
            
            **Example usage:**
            ```
            You are a professional resume restructuring expert. 
            Transform the provided resume data: {resume_data}
            Use reference number: {reference_number}
            ```
            """)
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Save Prompt", type="primary", key="save_prompt_main"):
                st.session_state['custom_prompt'] = edited_prompt
                st.success("✅ Custom prompt saved successfully!")
                st.rerun()
        
        with col2:
            if st.button("🔄 Reset to Default", key="reset_prompt_main"):
                if 'custom_prompt' in st.session_state:
                    del st.session_state['custom_prompt']
                st.success("✅ Reset to default prompt!")
                st.rerun()
        
        with col3:
            if st.button("❌ Close Editor", key="close_prompt_editor"):
                del st.session_state['show_prompt_editor']
                st.rerun()
        
        st.divider()
    
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
                        # Get custom prompt if available
                        custom_prompt = st.session_state.get('custom_prompt', None)
                        
                        results = process_resume_3_steps(uploaded_file, st.session_state.api_key, custom_prompt)
                        
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
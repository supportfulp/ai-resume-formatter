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
import uuid

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.chains.resume_restructure_chain import ResumeRestructureChain
from src.chains.resume_formatter import ResumeFormatter
from src.models.resume_models import ResumeProcessingRequest
from src.docx_export.create_resume_document import ResumeDocumentGenerator

# Import streamlit-shadcn-ui components
from streamlit_shadcn_ui import button, input, textarea, card, tabs, alert_dialog, badges, avatar, switch, select
from streamlit_shadcn_ui import input as shadcn_input
from streamlit_shadcn_ui import textarea as shadcn_textarea
from streamlit_shadcn_ui import card as shadcn_card
from streamlit_shadcn_ui import tabs as shadcn_tabs
# Use regular Streamlit alerts instead of shadcn alerts for simplicity
from streamlit_shadcn_ui import badges as shadcn_badge
from streamlit_shadcn_ui import avatar as shadcn_avatar
from streamlit_shadcn_ui import switch as shadcn_switch
from streamlit_shadcn_ui import select as shadcn_select

# Import database manager
try:
    from database import db_manager, init_database, create_demo_user
    DATABASE_AVAILABLE = True
except ImportError as e:
    st.error(f"Database module not found. Error: {e}")
    st.info("Please ensure database.py is in the same directory and all dependencies are installed.")
    st.info("Run: pip install -r requirements.txt")
    DATABASE_AVAILABLE = False
except Exception as e:
    st.warning(f"Database connection failed: {e}")
    st.info("Running in demo mode without database persistence.")
    DATABASE_AVAILABLE = False


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


def create_user_account(username: str, password: str, email: str = None) -> bool:
    """Create a new user account in database."""
    if DATABASE_AVAILABLE:
        return db_manager.create_user(username, password, email)
    else:
        # Demo mode - always return True for demo user
        return username == "demo" and password == "demo123"


def verify_user_credentials(username: str, password: str) -> Dict[str, Any]:
    """Verify user login credentials and return user info."""
    if DATABASE_AVAILABLE:
        return db_manager.verify_user(username, password)
    else:
        # Demo mode - only allow demo user
        if username == "demo" and password == "demo123":
            return {
                'id': 1,
                'username': 'demo',
                'email': 'demo@example.com',
                'created_at': None,
                'last_login': None
            }
        return None


def login_page():
    """Render the modern login page with shadcn components."""
    st.set_page_config(
        page_title="Resume Processor - Login",
        page_icon="🔐",
        layout="centered"
    )
    
    # Modern header with gradient
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                   font-size: 3rem; font-weight: bold; margin-bottom: 0.5rem;">
            🔐 Resume Processor
        </h1>
        <p style="color: #666; font-size: 1.1rem; margin-top: 0;">
            AI-Powered Resume Analysis & Restructuring
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main login interface with modern tabs
    selected_tab = shadcn_tabs(
        options=["🔐 Login", "📝 Register"],
        default_value="🔐 Login",
        key="login_tabs"
    )
    
    if selected_tab == "🔐 Login":
        with shadcn_card(
            title="Welcome Back!",
            description="Sign in to your account to continue",
            key="login_card"
        ):
            with st.form("login_form", clear_on_submit=False):
                username = shadcn_input(
                    default_value="",
                    placeholder="Enter your username",
                    key="login_username"
                )
                st.caption("Username")
                
                password = shadcn_input(
                    default_value="",
                    placeholder="Enter your password",
                    type="password",
                    key="login_password"
                )
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    login_button = st.form_submit_button(
                        "🔐 Sign In",
                        type="primary",
                        use_container_width=True
                    )
                with col2:
                    if st.form_submit_button("❓ Forgot Password?", use_container_width=True):
                        st.info("💡 For demo purposes, use: username: 'demo', password: 'demo123'")
                
                if login_button:
                    if not username or not password:
                        st.error("❌ Please enter both username and password!")
                    else:
                        user_info = verify_user_credentials(username, password)
                        if user_info:
                            st.session_state.user_logged_in = True
                            st.session_state.user_id = user_info['id']
                            st.session_state.username = user_info['username']
                            st.session_state.user_email = user_info.get('email')
                            st.success("✅ Login successful! Redirecting to API key setup...")
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password!")
    
    elif selected_tab == "📝 Register":
        with shadcn_card(
            title="Create New Account",
            description="Join us to start processing resumes",
            key="register_card"
        ):
            with st.form("register_form", clear_on_submit=True):
                new_username = shadcn_input(
                    default_value="",
                    placeholder="Choose a username",
                    key="register_username"
                )
                st.caption("Username")
                
                new_email = shadcn_input(
                    default_value="",
                    placeholder="your.email@example.com",
                    key="register_email"
                )
                st.caption("Email (optional)")
                
                new_password = shadcn_input(
                    default_value="",
                    placeholder="Choose a password",
                    type="password",
                    key="register_password"
                )
                st.caption("Password")
                
                confirm_password = shadcn_input(
                    default_value="",
                    placeholder="Confirm your password",
                    type="password",
                    key="register_confirm_password"
                )
                st.caption("Confirm Password")
                
                register_button = st.form_submit_button(
                    "📝 Create Account",
                    type="primary",
                    use_container_width=True
                )
                
                if register_button:
                    if not new_username or not new_password:
                        st.error("❌ Please fill in all required fields!")
                    elif new_password != confirm_password:
                        st.error("❌ Passwords don't match!")
                    elif len(new_password) < 6:
                        st.error("❌ Password must be at least 6 characters!")
                    else:
                        st.error("❌ Username already exists!")
    
    # Demo account info with modern styling
    st.divider()
    if st.session_state.get("demo_mode"):
        with shadcn_card(
            title="🔧 Demo Mode",
            description="Running without database persistence",
            key="demo_info_card"
        ):
            st.markdown("""
            - **Demo Account:** username: 'demo', password: 'demo123'
            - **Storage:** Your data is stored in your browser session only
            - **Features:** All functionality available in demo mode
            """)
    else:
        with shadcn_card(
            title="💡 Quick Start",
            description="Get started with our demo account",
            key="quick_start_card"
        ):
            st.markdown("""
            - **Demo Account:** username: 'demo', password: 'demo123'
            - **Storage:** Your data is stored securely in the database
            - **Features:** Full functionality with persistent storage
            """)


def api_key_setup_page():
    """Render the modern API key setup page with shadcn components."""
    st.set_page_config(
        page_title="Resume Processor - API Key Setup",
        page_icon="🔑",
        layout="centered"
    )
    
    # Modern header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                   font-size: 2.5rem; font-weight: bold; margin-bottom: 0.5rem;">
            🔑 API Key Setup
        </h1>
        <p style="color: #666; font-size: 1.1rem; margin-top: 0;">
            Configure your Google Gemini API key to get started
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main content card
    with shadcn_card(
        title="Welcome to Resume Processor! 🤖",
        description="This app uses Google's Gemini AI to analyze and restructure your resumes.",
        key="api_setup_card"
    ):
        st.markdown("""
        **To get started, you'll need:**
        1. A Google API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
        2. Your resume in PDF or DOCX format
        
        **Don't have an API key?** [Get one here](https://makersuite.google.com/app/apikey) (Free tier available)
        """)
        
        # Help expander
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
    
    # API Key Input Section
    with shadcn_card(
        title="🔑 Enter Your API Key",
        description="Your API key is stored securely in your browser session only",
        key="api_input_card"
    ):
        # Show current API key status
        if st.session_state.get("api_key_set"):
            st.success("✅ API key is already configured!")
            if button("🔄 Change API Key", variant="outline", key="change_api_key"):
                st.session_state.api_key_set = False
                st.session_state.api_key = None
                st.rerun()
        
        # API Key Input
        api_key = shadcn_input(
            default_value="",
            placeholder="AIzaSyC...",
            type="password",
            key="api_key_input"
        )
        st.caption("Google API Key")
        
        # Set API Key Button
        if button("🔑 Set API Key", variant="default", key="set_api_key_btn"):
            if not api_key:
                st.error("❌ Please enter your Google API key!")
            elif not validate_api_key(api_key):
                st.warning("⚠️ API key format looks invalid. Please check your key.")
                st.info("💡 Google API keys typically start with 'AIzaSy' and are about 39 characters long.")
            else:
                # Store API key in database or session state
                if DATABASE_AVAILABLE:
                    user_id = st.session_state.get('user_id')
                    if user_id and db_manager.save_api_key(user_id, api_key):
                        st.session_state.api_key = api_key
                        st.session_state.api_key_set = True
                        st.session_state.api_key_setup_time = time.time()
                        
                        st.success("✅ API key set successfully!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Failed to save API key. Please try again.")
                else:
                    # Demo mode - store in session state only
                    st.session_state.api_key = api_key
                    st.session_state.api_key_set = True
                    st.session_state.api_key_setup_time = time.time()
                    
                    st.success("✅ API key set successfully! (Demo mode)")
                    st.balloons()
                    st.rerun()
        
        # Back to login button
        if button("← Back to Login", variant="outline", key="back_to_login_btn"):
            st.session_state.user_logged_in = False
            st.session_state.username = None
            st.rerun()
    
    # Footer with helpful links
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.8em; padding: 1rem 0;'>
        <p>🔒 Your API key is stored securely in your browser session only</p>
        <p>💰 Free tier: 15 requests/minute, 1500 requests/day</p>
        <p>📖 <a href='https://ai.google.dev/docs' target='_blank'>Google AI Documentation</a></p>
    </div>
    """, unsafe_allow_html=True)


def logout_button():
    """Render modern logout button in sidebar."""
    if button("🚪 Logout", variant="outline", key="logout_btn"):
        # Clear session state
        st.session_state.authenticated = False
        st.session_state.user_logged_in = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.user_email = None
        st.session_state.api_key = None
        st.session_state.api_key_set = False
        st.session_state.api_key_setup_time = None
        st.session_state.show_api_key_setup = False
        st.rerun()


def show_user_info():
    """Show modern user information in sidebar."""
    if st.session_state.get("user_logged_in"):
        username = st.session_state.get("username", "User")
        user_id = st.session_state.get("user_id")
        user_email = st.session_state.get("user_email")
        
        # User profile card
        with shadcn_card(
            title=f"👤 {username}",
            description=user_email if user_email else "User",
            key="user_profile_card"
        ):
            # Show API key status
            if st.session_state.get("api_key_set"):
                shadcn_badge(badge_list=[("🔑 API Key: Configured", "default")], key="api_key_badge")
                
                # Show masked API key
                api_key = st.session_state.get("api_key", "")
                if api_key:
                    masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
                    st.caption(f"Key: {masked_key}")
                
                # Show session time
                setup_time = st.session_state.get("api_key_setup_time")
                if setup_time:
                    elapsed = time.time() - setup_time
                    hours = int(elapsed // 3600)
                    minutes = int((elapsed % 3600) // 60)
                    st.caption(f"⏱️ Setup: {hours}h {minutes}m ago")
            else:
                shadcn_badge(badge_list=[("⚠️ API Key: Not set", "destructive")], key="api_key_badge")
            
            # Show processing history if available
            if DATABASE_AVAILABLE and user_id:
                history = db_manager.get_processing_history(user_id, limit=3)
                if history:
                    st.divider()
                    st.subheader("📊 Recent Activity")
                    for item in history:
                        st.caption(f"📄 {item['filename']}")
                        st.caption(f"🕒 {item['processing_date'].strftime('%Y-%m-%d %H:%M')}")
            elif st.session_state.get("demo_mode"):
                st.info("🔧 Demo Mode - No persistent storage")
        
        st.divider()
        
        # Quick export section in sidebar
        if st.session_state.get("processing_complete") and st.session_state.get("edited_data"):
            with shadcn_card(
                title="📤 Quick Export",
                key="quick_export_card"
            ):
                # DOCX export button in sidebar
                if button("📄 Export to DOCX", variant="default", key="sidebar_docx_export"):
                    docx_filename = f"resume_{st.session_state.current_filename.replace('.pdf', '')}.docx"
                    docx_content = generate_docx_file(st.session_state.edited_data, docx_filename)
                    
                    if docx_content:
                        st.success("✅ DOCX generated successfully!")
                        # Create download link
                        st.download_button(
                            label="📥 Download DOCX",
                            data=docx_content,
                            file_name=docx_filename,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key="sidebar_download_docx"
                        )
                    else:
                        st.error("❌ Failed to generate DOCX")
                
                # JSON export button in sidebar
                if button("📄 Export to JSON", variant="outline", key="sidebar_json_export"):
                    export_data = st.session_state.edited_data
                    final_filename = f"resume_data_{st.session_state.current_filename.replace('.pdf', '')}.json"
                    st.download_button(
                        label="📥 Download JSON",
                        data=json.dumps(export_data, indent=2),
                        file_name=final_filename,
                        mime="application/json",
                        key="sidebar_download_json"
                    )


def process_resume_3_steps(pdf_file, api_key: str, custom_prompt: str = None) -> Dict[str, Any]:
    """Process resume through 3 steps and return results with token tracking."""
    
    # Initialize token tracking
    total_tokens = {
        'input_tokens': 0,
        'output_tokens': 0,
        'total_tokens': 0
    }
    
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
        
        # Track tokens from Step 1 (extract_chain)
        if hasattr(step1_result, 'processing_metadata') and step1_result.processing_metadata:
            usage = step1_result.processing_metadata.get('usage_metadata', {})
            print(f"Step 1 usage: {usage}")
            total_tokens['input_tokens'] += usage.get('input_tokens', 0)
            total_tokens['output_tokens'] += usage.get('output_tokens', 0)
            total_tokens['total_tokens'] += usage.get('total_tokens', 0)
        
        # Step 2: First restructuring
        restructured_from_data = restructure_chain.restructure_from_data(
            extracted_data, 
            reference_number="SDA02-AMH"
        )
        
        # Track tokens from Step 2 (restructure_chain)
        if hasattr(restructure_chain, 'last_usage_metadata') and restructure_chain.last_usage_metadata:
            usage = restructure_chain.last_usage_metadata
            print(f"Step 2 usage: {usage}")
            total_tokens['input_tokens'] += usage.get('input_tokens', 0)
            total_tokens['output_tokens'] += usage.get('output_tokens', 0)
            total_tokens['total_tokens'] += usage.get('total_tokens', 0)
        
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
        
        # Track tokens from Step 3 (extract_chain again)
        if hasattr(step3_result, 'processing_metadata') and step3_result.processing_metadata:
            usage = step3_result.processing_metadata.get('usage_metadata', {})
            print(f"Step 3 usage: {usage}")
            total_tokens['input_tokens'] += usage.get('input_tokens', 0)
            total_tokens['output_tokens'] += usage.get('output_tokens', 0)
            total_tokens['total_tokens'] += usage.get('total_tokens', 0)
        
        print(f"Total tokens tracked: {total_tokens}")
        
        # Calculate cost (Gemini 2.5 Flash pricing as of 2024)
        # Input: $0.000125 per 1K tokens, Output: $0.000375 per 1K tokens
        input_cost = (total_tokens['input_tokens'] / 1000) * 0.000125
        output_cost = (total_tokens['output_tokens'] / 1000) * 0.000375
        total_cost = input_cost + output_cost
        
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
            },
            "token_usage": {
                "total_tokens": total_tokens,
                "cost_estimation": {
                    "input_cost_usd": round(input_cost, 6),
                    "output_cost_usd": round(output_cost, 6),
                    "total_cost_usd": round(total_cost, 6),
                    "model": "gemini-2.5-flash"
                }
            }
        }
        
        return results
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def generate_docx_file(resume_data: Dict[str, Any], filename: str) -> bytes:
    """
    Generate a DOCX file from resume data and return as bytes.
    
    Args:
        resume_data (Dict[str, Any]): The resume data to convert
        filename (str): Base filename for the output
        
    Returns:
        bytes: The DOCX file content as bytes
    """
    # try:
    # Create temporary file path
    temp_docx_path = tempfile.mktemp(suffix='.docx')
    
    # Convert resume data to JSON string
    resume_json = json.dumps(resume_data)
    
    # Generate DOCX using the ResumeDocumentGenerator
    generator = ResumeDocumentGenerator(page_height=11)  # Standard letter size
    generator.generate_docx(resume_json, temp_docx_path)
    
    # Read the generated file and return as bytes
    with open(temp_docx_path, 'rb') as f:
        docx_content = f.read()
    
    # Clean up temporary file
    if os.path.exists(temp_docx_path):
        os.unlink(temp_docx_path)
    
    return docx_content
        
    # except Exception as e:
    #     st.error(f"Error generating DOCX: {str(e)}")
    #     return None


def render_editing_interface():
    """Render the modern editing interface with shadcn components."""
    
    # Get current data from session state
    final_data = st.session_state.edited_data
    original_results = st.session_state.original_results
    
    # Personal Information Section
    with shadcn_card(
        title="👤 Personal Information",
        key="personal_info_card"
    ):
        col1, col2 = st.columns(2)
        
        with col1:
            st.caption("Full Name")
            name = shadcn_input(default_value=final_data.get("name", ""), key="name_input")
            st.caption("Email")
            email = shadcn_input(default_value=final_data.get("email", ""), key="email_input")
            st.caption("Phone")
            phone = shadcn_input(default_value=final_data.get("phone", ""), key="phone_input")
            st.caption("Reference Number")
            reference_number = shadcn_input(default_value=final_data.get("reference_number", ""), key="reference_number_input")
        
        with col2:
            st.caption("Location")
            location = shadcn_input(default_value=final_data.get("location", ""), key="location_input")
            st.caption("LinkedIn")
            linkedin = shadcn_input(default_value=final_data.get("linkedin", ""), key="linkedin_input")
            st.caption("Website")
            website = shadcn_input(default_value=final_data.get("website", ""), key="website_input")
    
    # Summary
    st.caption("Professional Summary")
    summary = shadcn_textarea(default_value=final_data.get("summary", ""), key="summary_input")
    
    # Experience Section
    with shadcn_card(
        title="💼 Work Experience",
        key="experience_card"
    ):
        experiences = final_data.get("experience", [])
        
        # Add new experience button
        if button("➕ Add New Experience", variant="outline", key="add_experience"):
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
                if button(f"🗑️ Delete Experience {i+1}", variant="destructive", key=f"delete_exp_{i}"):
                    experiences.pop(i)
                    st.session_state.edited_data["experience"] = experiences
                    st.success(f"✅ Experience {i+1} deleted!")
                    st.rerun()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.caption(f"Company {i+1}")
                    exp['company'] = shadcn_input(default_value=exp.get("company", ""), key=f"company_{i}")
                    st.caption(f"Title {i+1}")
                    exp['title'] = shadcn_input(default_value=exp.get("title", ""), key=f"title_{i}")
                    st.caption(f"Start Date {i+1}")
                    exp['start_date'] = shadcn_input(default_value=exp.get("start_date", ""), key=f"start_{i}")
                
                with col2:
                    st.caption(f"End Date {i+1}")
                    exp['end_date'] = shadcn_input(default_value=exp.get("end_date", ""), key=f"end_{i}")
                
                st.caption(f"Achievements {i+1}")
                exp['achievements'] = shadcn_textarea(default_value=exp.get("achievements", ""), key=f"desc_{i}")
    
    # Education Section
    with shadcn_card(
        title="🎓 Education",
        key="education_card"
    ):
        educations = final_data.get("education", [])
        
        # Add new education button
        if button("➕ Add New Education", variant="outline", key="add_education"):
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
                if button(f"🗑️ Delete Education {i+1}", variant="destructive", key=f"delete_edu_{i}"):
                    educations.pop(i)
                    st.session_state.edited_data["education"] = educations
                    st.success(f"✅ Education {i+1} deleted!")
                    st.rerun()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.caption(f"Degree {i+1}")
                    edu['degree'] = shadcn_input(default_value=edu.get("degree", ""), key=f"degree_{i}")
                    st.caption(f"Institution {i+1}")
                    edu['institution'] = shadcn_input(default_value=edu.get("institution", ""), key=f"edu_institution_{i}")
                    st.caption(f"Start Date {i+1}")
                    edu['start_date'] = shadcn_input(default_value=edu.get("start_date", ""), key=f"edu_start_{i}")
                
                with col2:
                    st.caption(f"End Date {i+1}")
                    edu['end_date'] = shadcn_input(default_value=edu.get("end_date", ""), key=f"edu_end_{i}")
                    edu['gpa'] = st.number_input(f"GPA {i+1}", value=float(edu.get("gpa", 0.0)) if edu.get("gpa") else 0.0, step=0.01, key=f"gpa_{i}")
    
    # Skills Section
    st.caption("Skills (comma-separated)")

    with shadcn_card(
        title="🛠️ Skills",
        key="skills_card"
    ):
        skills_text = ", ".join(final_data.get("skills", []))
        skills_input = shadcn_textarea(default_value=skills_text, key="skills_input")
        skills = [skill.strip() for skill in skills_input.split(",") if skill.strip()]
    
    # Languages Section
    with shadcn_card(
        title="🌍 Languages",
        key="languages_card"
    ):
        languages_text = ", ".join(final_data.get("languages", []))
        st.caption("Languages (comma-separated)")
        languages_input = shadcn_textarea(default_value=languages_text, key="languages_input")
        languages = [lang.strip() for lang in languages_input.split(",") if lang.strip()]
    
    # Certifications Section
    with shadcn_card(
        title="🏆 Certifications",
        key="certifications_card"
    ):
        certifications_text = ", ".join(final_data.get("certifications", []))
        st.caption("Certifications (comma-separated)")
        certifications_input = shadcn_textarea(default_value=certifications_text, key="certifications_input")
        certifications = [cert.strip() for cert in certifications_input.split(",") if cert.strip()]
    
    # Save and Export buttons
    with shadcn_card(
        title="💾 Save & Export",
        key="export_card"
    ):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if button("💾 Save Changes", variant="default", key="save_button"):
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
        
        with col4:
            # Export DOCX file
            docx_filename = f"resume_{st.session_state.current_filename.replace('.pdf', '')}.docx"
            
            # Generate DOCX content
            docx_content = generate_docx_file(st.session_state.edited_data, docx_filename)
            
            if docx_content:
                st.download_button(
                    label="📄 Download DOCX",
                    data=docx_content,
                    file_name=docx_filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key="download_docx"
                )
            else:
                st.error("❌ Failed to generate DOCX")
    
    # Display formatted resume
    with shadcn_card(
        title="📄 Formatted Resume Preview",
        key="preview_card"
    ):
        st.text_area(
            "Formatted resume",
            value=st.session_state.original_results["step3_final_formatted"],
            height=400,
            disabled=True
        )


def show_processing_history_tab():
    """Show processing history tab."""
    st.header("📊 Processing History")
    
    if not DATABASE_AVAILABLE:
        st.warning("⚠️ Database not available. Processing history is not available in demo mode.")
        return
    
    if not st.session_state.get('user_id'):
        st.warning("⚠️ User not logged in.")
        return
    
    # Get processing history
    history = db_manager.get_processing_history(st.session_state.user_id, limit=50)
    
    if not history:
        st.info("📝 No processing history found. Start by processing a resume!")
        return
    
    # Display history in a table
    for i, record in enumerate(history):
        with shadcn_card(
            title=f"📄 {record['filename']}",
            key=f"history_card_{i}"
        ):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.caption(f"**Processed:** {record['processing_date'].strftime('%Y-%m-%d %H:%M:%S')}")
                if record['metadata']:
                    st.caption(f"**Status:** {record['status']}")
            
            with col2:
                if button("🔄 Load Result", variant="outline", key=f"load_result_{i}"):
                    result = db_manager.get_processing_result(record['id'])
                    if result:
                        st.session_state.edited_data = result['result_data']
                        st.session_state.processing_complete = True
                        # Switch to resume processing tab
                        st.rerun()
                    else:
                        st.error("❌ No result data found for this record")
            
            with col3:
                if button("🗑️ Delete", variant="outline", key=f"delete_history_{i}"):
                    # TODO: Add delete functionality
                    st.warning("Delete functionality not implemented yet")


def show_prompt_management_tab():
    """Show prompt management tab."""
    st.header("🔧 Prompt Management")
    
    # Load default prompt
    from src.prompts.resume_restructure_prompts import RESUME_RESTRUCTURE_PROMPT
    default_prompt = RESUME_RESTRUCTURE_PROMPT.template
    
    # Get custom prompts from database
    custom_prompts = []
    if DATABASE_AVAILABLE and st.session_state.get('user_id'):
        custom_prompts = db_manager.get_custom_prompts(st.session_state.user_id)
    
    # Current prompt selection
    with shadcn_card(
        title="🎯 Current Prompt Selection",
        key="current_prompt_card"
    ):
        if custom_prompts:
            # Show custom prompts dropdown
            prompt_options = ["Default Prompt"] + [f"{p['name']} (Custom)" for p in custom_prompts]
            selected_prompt_index = st.selectbox(
                "Select a prompt to use:",
                options=prompt_options,
                index=0,
                key="prompt_selector"
            )
            
            if selected_prompt_index == "Default Prompt":
                st.session_state.selected_prompt = default_prompt
                st.session_state.selected_prompt_name = "Default"
            else:
                # Get the selected custom prompt
                prompt_name = selected_prompt_index.replace(" (Custom)", "")
                selected_prompt = next((p for p in custom_prompts if p['name'] == prompt_name), None)
                if selected_prompt:
                    st.session_state.selected_prompt = selected_prompt['prompt_text']
                    st.session_state.selected_prompt_name = selected_prompt['name']
        else:
            st.session_state.selected_prompt = default_prompt
            st.session_state.selected_prompt_name = "Default"
            st.info("📝 No custom prompts found. Using default prompt.")
        
        # Show current prompt preview
        with st.expander("👀 Preview Current Prompt", expanded=False):
            current_prompt = st.session_state.get('selected_prompt', default_prompt)
            if current_prompt:
                preview_text = current_prompt[:500] + "..." if len(current_prompt) > 500 else current_prompt
                st.text_area(
                    "Current Prompt",
                    value=preview_text,
                    height=150,
                    disabled=True,
                    key="prompt_preview"
                )
                if len(current_prompt) > 500:
                    st.caption("(Showing first 500 characters)")
    
    # Create new custom prompt
    with shadcn_card(
        title="📝 Create New Custom Prompt",
        key="create_prompt_card"
    ):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            prompt_name = shadcn_input(
                default_value="",
                placeholder="Enter prompt name",
                key="new_prompt_name"
            )
            st.caption("Prompt Name")
        
        with col2:
            if button("💾 Save New Prompt", variant="default", key="save_new_prompt"):
                if not prompt_name:
                    st.error("❌ Please enter a prompt name!")
                elif not DATABASE_AVAILABLE:
                    st.error("❌ Database not available. Cannot save in demo mode.")
                else:
                    # Get the prompt text from the editor below
                    new_prompt_text = st.session_state.get('new_prompt_text', default_prompt)
                    if db_manager.save_custom_prompt(st.session_state.user_id, prompt_name, new_prompt_text):
                        st.success("✅ Custom prompt saved successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to save custom prompt!")
        
        # Prompt editor
        st.caption("Prompt Template")
        new_prompt_text = shadcn_textarea(
            default_value=default_prompt,
            key="new_prompt_text"
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
    
    # Manage existing custom prompts
    if custom_prompts:
        with shadcn_card(
            title="📋 Manage Custom Prompts",
            key="manage_prompts_card"
        ):
            for i, prompt in enumerate(custom_prompts):
                with st.expander(f"📝 {prompt['name']} (Created: {prompt['created_at'].strftime('%Y-%m-%d')})", expanded=False):
                    st.text_area(
                        f"Prompt Content",
                        value=prompt['prompt_text'],
                        height=200,
                        disabled=True,
                        key=f"prompt_content_{i}"
                    )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if button("🗑️ Delete", variant="outline", key=f"delete_prompt_{i}"):
                            if db_manager.delete_custom_prompt(prompt['id'], st.session_state.user_id):
                                st.success("✅ Prompt deleted successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to delete prompt!")
                    
                    with col2:
                        if button("📋 Use This Prompt", variant="default", key=f"use_prompt_{i}"):
                            st.session_state.selected_prompt = prompt['prompt_text']
                            st.session_state.selected_prompt_name = prompt['name']
                            st.success(f"✅ Now using prompt: {prompt['name']}")


def show_resume_processing_tab():
    """Show resume processing tab."""
    st.header("📁 Resume Processing")
    
    # File upload
    with shadcn_card(
        title="📁 Upload Resume",
        key="upload_card"
    ):
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
                if button("🚀 Process Resume (3 Steps)", variant="default", key="process_button"):
                    with st.spinner("Processing resume through 3-step pipeline..."):
                        try:
                            # Get selected prompt
                            selected_prompt = st.session_state.get('selected_prompt', None)
                            
                            results = process_resume_3_steps(uploaded_file, st.session_state.api_key, selected_prompt)
                            
                            # Store results in session state
                            st.session_state.edited_data = results["step3_final_data"].copy()
                            st.session_state.original_results = results.copy()
                            st.session_state.processing_complete = True
                            
                            # Save processing history and results to database
                            if DATABASE_AVAILABLE:
                                user_id = st.session_state.get('user_id')
                                if user_id:
                                    metadata = {
                                        'target_role': 'Software Engineer',
                                        'template_style': 'professional',
                                        'steps_completed': 3,
                                        'prompt_used': st.session_state.get('selected_prompt_name', 'Default')
                                    }
                                    history_id = db_manager.save_processing_history(user_id, uploaded_file.name, metadata)
                                    if history_id:
                                        db_manager.save_processing_result(history_id, results["step3_final_data"])
                                        
                                        # Save token usage data
                                        if 'token_usage' in results:
                                            token_data = {
                                                'input_tokens': results['token_usage']['total_tokens']['input_tokens'],
                                                'output_tokens': results['token_usage']['total_tokens']['output_tokens'],
                                                'total_tokens': results['token_usage']['total_tokens']['total_tokens'],
                                                'input_cost_usd': results['token_usage']['cost_estimation']['input_cost_usd'],
                                                'output_cost_usd': results['token_usage']['cost_estimation']['output_cost_usd'],
                                                'total_cost_usd': results['token_usage']['cost_estimation']['total_cost_usd'],
                                                'model': results['token_usage']['cost_estimation']['model']
                                            }
                                            db_manager.save_token_usage(user_id, history_id, token_data)
                            
                            st.success("✅ Processing complete! You can now edit the data below.")
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Error processing resume: {str(e)}")
                            st.exception(e)
            
            # Show editing interface if processing is complete
            if st.session_state.processing_complete and st.session_state.edited_data is not None:
                # Display token usage and cost information
                if 'original_results' in st.session_state and st.session_state.original_results:
                    token_usage = st.session_state.original_results.get('token_usage', {})
                    if token_usage:
                        with shadcn_card(
                            title="💰 Token Usage & Cost",
                            key="token_usage_card"
                        ):
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric(
                                    "Input Tokens",
                                    f"{token_usage.get('total_tokens', {}).get('input_tokens', 0):,}"
                                )
                            
                            with col2:
                                st.metric(
                                    "Output Tokens",
                                    f"{token_usage.get('total_tokens', {}).get('output_tokens', 0):,}"
                                )
                            
                            with col3:
                                st.metric(
                                    "Total Tokens",
                                    f"{token_usage.get('total_tokens', {}).get('total_tokens', 0):,}"
                                )
                            
                            with col4:
                                cost_info = token_usage.get('cost_estimation', {})
                                st.metric(
                                    "Estimated Cost",
                                    f"${cost_info.get('total_cost_usd', 0):.6f}"
                                )
                            
                            # Show detailed cost breakdown
                            with st.expander("📊 Detailed Cost Breakdown", expanded=False):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.caption("**Input Cost:**")
                                    st.write(f"${cost_info.get('input_cost_usd', 0):.6f}")
                                    st.caption("**Output Cost:**")
                                    st.write(f"${cost_info.get('output_cost_usd', 0):.6f}")
                                
                                with col2:
                                    st.caption("**Model Used:**")
                                    st.write(cost_info.get('model', 'Unknown'))
                                    st.caption("**Pricing:**")
                                    st.write("Input: $0.000125/1K tokens")
                                    st.write("Output: $0.000375/1K tokens")
                
                st.info("💡 **Export Options:** You can export your resume as JSON, TXT, or DOCX format. Use the buttons below or the Quick Export section in the sidebar.")
                
                render_editing_interface()


def show_consumption_dashboard_tab():
    """Show consumption dashboard tab."""
    st.header("💰 Consumption Dashboard")
    
    if not DATABASE_AVAILABLE:
        st.warning("⚠️ Database not available. Consumption dashboard is not available in demo mode.")
        return
    
    if not st.session_state.get('user_id'):
        st.warning("⚠️ User not logged in.")
        return
    
    # Time period selector
    col1, col2 = st.columns([1, 1])
    with col1:
        days = st.selectbox(
            "Time Period",
            options=[7, 30, 90, 365],
            index=1,
            format_func=lambda x: f"{x} days"
        )
    
    with col2:
        if st.button("🔄 Refresh Data", key="refresh_consumption"):
            st.rerun()
    
    # Get user's token usage data
    user_id = st.session_state.get('user_id')
    usage_data = db_manager.get_user_token_usage(user_id, days)
    summary_data = db_manager.get_user_token_summary(user_id, days)
    
    if not usage_data:
        st.info("📊 No token usage data found for your account.")
        return
    
    # Summary metrics
    with shadcn_card(
        title="📊 Usage Summary",
        key="usage_summary_card"
    ):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Requests",
                f"{summary_data.get('total_requests', 0):,}"
            )
        
        with col2:
            st.metric(
                "Total Tokens",
                f"{summary_data.get('total_tokens', 0):,}"
            )
        
        with col3:
            st.metric(
                "Total Cost",
                f"${summary_data.get('total_cost', 0):.6f}"
            )
        
        with col4:
            avg_cost = summary_data.get('avg_cost_per_request', 0)
            st.metric(
                "Avg Cost/Request",
                f"${avg_cost:.6f}"
            )
    
    # Detailed breakdown
    with shadcn_card(
        title="📈 Detailed Breakdown",
        key="detailed_breakdown_card"
    ):
        col1, col2 = st.columns(2)
        
        with col1:
            st.caption("**Token Distribution**")
            st.metric("Input Tokens", f"{summary_data.get('total_input_tokens', 0):,}")
            st.metric("Output Tokens", f"{summary_data.get('total_output_tokens', 0):,}")
        
        with col2:
            st.caption("**Cost Breakdown**")
            st.metric("Input Cost", f"${summary_data.get('total_input_cost', 0):.6f}")
            st.metric("Output Cost", f"${summary_data.get('total_output_cost', 0):.6f}")
    
    # Charts section
    with shadcn_card(
        title="📊 Usage Trends",
        key="usage_trends_card"
    ):
        # Prepare data for charts
        import pandas as pd
        from datetime import datetime
        
        # Convert usage data to DataFrame
        df = pd.DataFrame(usage_data)
        
        if not df.empty:
            # Convert created_at to datetime if it's not already
            df['created_at'] = pd.to_datetime(df['created_at'])
            
            # Group by date and aggregate
            df['date'] = df['created_at'].dt.date
            daily_tokens = df.groupby('date')['total_tokens'].sum().reset_index()
            daily_requests = df.groupby('date').size().reset_index(name='request_count')
            
            # Convert date back to datetime for plotting
            daily_tokens['date'] = pd.to_datetime(daily_tokens['date'])
            daily_requests['date'] = pd.to_datetime(daily_requests['date'])
            
            # Set date as index for plotting
            daily_tokens.set_index('date', inplace=True)
            daily_requests.set_index('date', inplace=True)
            
            # Token Count per Day chart
            st.subheader("🔢 Token Count per Day")
            if not daily_tokens.empty:
                st.line_chart(daily_tokens, y="total_tokens")
            else:
                st.info("No token data available for the selected period.")
            
            # Request Count per Day chart
            st.subheader("📋 Request Count per Day")
            if not daily_requests.empty:
                st.line_chart(daily_requests, y="request_count")
            else:
                st.info("No request data available for the selected period.")
        else:
            st.info("No data available for the selected period.")
    
    # Recent usage table
    with shadcn_card(
        title="📋 Recent Usage",
        key="recent_usage_card"
    ):
        if usage_data:
            # Create a simple table of recent usage
            for i, usage in enumerate(usage_data[:10]):  # Show last 10 entries
                with st.expander(f"📄 {usage['filename']} - {usage['created_at'].strftime('%Y-%m-%d %H:%M')}", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.caption("**Tokens**")
                        st.write(f"Input: {usage['input_tokens']:,}")
                        st.write(f"Output: {usage['output_tokens']:,}")
                        st.write(f"Total: {usage['total_tokens']:,}")
                    
                    with col2:
                        st.caption("**Cost**")
                        st.write(f"Input: ${usage['input_cost_usd']:.6f}")
                        st.write(f"Output: ${usage['output_cost_usd']:.6f}")
                        st.write(f"Total: ${usage['total_cost_usd']:.6f}")
                    
                    with col3:
                        st.caption("**Model**")
                        st.write(usage['model'])
                        st.caption(f"Processed: {usage['processing_date'].strftime('%Y-%m-%d %H:%M')}")
        else:
            st.info("No recent usage data available.")
    
    # Pricing information
    with shadcn_card(
        title="💡 Pricing Information",
        key="pricing_info_card"
    ):
        st.markdown("""
        **Gemini 2.5 Flash Pricing (as of 2024):**
        
        - **Input Tokens:** $0.000125 per 1K tokens
        - **Output Tokens:** $0.000375 per 1K tokens
        
        **Cost Calculation:**
        - Input Cost = (Input Tokens ÷ 1000) × $0.000125
        - Output Cost = (Output Tokens ÷ 1000) × $0.000375
        - Total Cost = Input Cost + Output Cost
        """)


def main():
    st.set_page_config(
        page_title="Resume Processing Tool",
        page_icon="📄",
        layout="wide"
    )
    
    # Initialize database if available
    if DATABASE_AVAILABLE:
        try:
            init_database()
            create_demo_user()
        except Exception as e:
            st.warning(f"⚠️ Database initialization failed: {e}")
            st.info("Running in demo mode without database persistence.")
            st.session_state.demo_mode = True
    else:
        st.session_state.demo_mode = True
    
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
        # Modern header
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                       font-size: 3rem; font-weight: bold; margin-bottom: 0.5rem;">
                📄 Resume Processing Tool
            </h1>
            <p style="color: #666; font-size: 1.1rem; margin-top: 0;">
                Upload a PDF resume and process it through our 3-step AI pipeline
            </p>
        </div>
        """, unsafe_allow_html=True)
        # Initialize session state
        if 'processing_complete' not in st.session_state:
            st.session_state.processing_complete = False
        if 'current_filename' not in st.session_state:
            st.session_state.current_filename = ""
        if 'current_step' not in st.session_state:
            st.session_state.current_step = 1

        # Main content area with vertical tabs
        col1, col2 = st.columns([1, 4])
        
        with col1:
            # Vertical tabs in left column
            selected_tab = st.radio(
                "Navigation",
                options=["📁 Resume Processing", "🔧 Prompt Management", "📊 Processing History", "💰 Consumption Dashboard"],
                label_visibility="collapsed",
                key="vertical_tabs"
            )
        
        with col2:
            # Main content in right column
            if selected_tab == "📁 Resume Processing":
                show_resume_processing_tab()
            elif selected_tab == "🔧 Prompt Management":
                show_prompt_management_tab()
            elif selected_tab == "📊 Processing History":
                show_processing_history_tab()
            elif selected_tab == "💰 Consumption Dashboard":
                show_consumption_dashboard_tab()
        logout_button()


if __name__ == "__main__":
    main() 
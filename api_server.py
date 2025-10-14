#!/usr/bin/env python3
"""
FastAPI backend server for the Resume Processor React app.
Provides REST API endpoints to match the React frontend requirements.
"""

import os
import sys
import json
import tempfile
import hashlib
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import asyncio
import uuid
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

try:
    from src.chains.resume_restructure_chain import ResumeRestructureChain
    from src.chains.resume_formatter import ResumeFormatter
    from src.models.resume_models import ResumeProcessingRequest
    from src.docx_export.create_resume_document import ResumeDocumentGenerator
    from database import db_manager, init_database, create_demo_user
    DATABASE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some imports failed: {e}")
    DATABASE_AVAILABLE = False

# Initialize database using lifespan events
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if DATABASE_AVAILABLE:
        try:
            init_database()
            create_demo_user()
            print("✅ Database initialized successfully")
        except Exception as e:
            print(f"⚠️ Database initialization failed: {e}")
    yield
    # Shutdown (if needed)
    pass

# Initialize FastAPI app
app = FastAPI(
    title="Resume Processor API",
    description="REST API for AI-powered resume processing",
    version="1.0.0",
    lifespan=lifespan
)

# In-memory job store for incremental processing
JOBS: Dict[str, Dict[str, Any]] = {}

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://34.31.70.193:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class ApiKeyRequest(BaseModel):
    api_key: str

class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None

class User(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    created_at: Optional[str] = None
    last_login: Optional[str] = None

class SavePromptRequest(BaseModel):
    user_id: int
    name: str
    prompt_text: str

class ExportDocxRequest(BaseModel):
    data: Dict[str, Any]
    filename: str

# Utility functions
def hash_password(password: str) -> str:
    """Hash password for secure storage."""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_api_key(api_key: str) -> bool:
    """Basic validation for Google API key format."""
    if not api_key:
        return False
    return len(api_key) >= 30 and (api_key.startswith('AI') or 'google' in api_key.lower())

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Authentication endpoints
@app.post("/auth/login", response_model=ApiResponse)
async def login(request: LoginRequest):
    """User login endpoint."""
    try:
        # Demo user check
        if request.username == "demo" and request.password == "demo123":
            demo_user = User(
                id=1,
                username="demo",
                email="demo@example.com"
            )
            return ApiResponse(success=True, data=demo_user.dict())
        
        # Database authentication
        if DATABASE_AVAILABLE:
            user_data = db_manager.verify_user(request.username, request.password)
            if user_data:
                # Convert datetime objects to strings for Pydantic model
                if 'created_at' in user_data and user_data['created_at']:
                    user_data['created_at'] = user_data['created_at'].isoformat()
                if 'last_login' in user_data and user_data['last_login']:
                    user_data['last_login'] = user_data['last_login'].isoformat()
                user = User(**user_data)
                return ApiResponse(success=True, data=user.dict())
        
        return ApiResponse(success=False, error="Invalid credentials")
    
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

@app.post("/auth/register", response_model=ApiResponse)
async def register(request: RegisterRequest):
    """User registration endpoint."""
    try:
        if DATABASE_AVAILABLE:
            success = db_manager.create_user(request.username, request.password, request.email)
            if success:
                # Return the created user
                user_data = db_manager.verify_user(request.username, request.password)
                if user_data:
                    # Convert datetime objects to strings for Pydantic model
                    if 'created_at' in user_data and user_data['created_at']:
                        user_data['created_at'] = user_data['created_at'].isoformat()
                    if 'last_login' in user_data and user_data['last_login']:
                        user_data['last_login'] = user_data['last_login'].isoformat()
                    user = User(**user_data)
                    return ApiResponse(success=True, data=user.dict())
            return ApiResponse(success=False, error="Failed to create user")
        else:
            return ApiResponse(success=False, error="Database not available")
    
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

@app.post("/auth/verify-api-key", response_model=ApiResponse)
async def verify_api_key(request: ApiKeyRequest):
    """Verify API key format."""
    try:
        is_valid = validate_api_key(request.api_key)
        return ApiResponse(success=True, data=is_valid)
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

class SaveApiKeyRequest(BaseModel):
    user_id: int
    api_key: str

@app.post("/auth/save-api-key", response_model=ApiResponse)
async def save_api_key(request: SaveApiKeyRequest):
    """Save user's API key securely."""
    try:
        if not validate_api_key(request.api_key):
            return ApiResponse(success=False, error="Invalid API key format")
        
        if DATABASE_AVAILABLE:
            success = db_manager.save_api_key(request.user_id, request.api_key)
            if success:
                return ApiResponse(success=True, message="API key saved successfully")
            else:
                return ApiResponse(success=False, error="Failed to save API key")
        else:
            return ApiResponse(success=False, error="Database not available")
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

@app.get("/auth/get-api-key/{user_id}", response_model=ApiResponse)
async def get_api_key(user_id: int):
    """Get user's API key hash (for verification purposes only)."""
    try:
        if DATABASE_AVAILABLE:
            api_key_hash = db_manager.get_api_key(user_id)
            if api_key_hash:
                # Return masked version for security
                masked_key = "***Key is configured***"
                return ApiResponse(success=True, data={"has_api_key": True, "masked_key": masked_key})
            else:
                return ApiResponse(success=True, data={"has_api_key": False, "masked_key": None})
        else:
            return ApiResponse(success=False, error="Database not available")
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

import secrets

class CreateSessionRequest(BaseModel):
    user_id: int
    expires_in_hours: Optional[int] = 24

class ValidateSessionRequest(BaseModel):
    session_token: str

@app.post("/auth/create-session", response_model=ApiResponse)
async def create_session(request: CreateSessionRequest):
    """Create a new user session."""
    try:
        if DATABASE_AVAILABLE:
            # Generate secure session token
            session_token = secrets.token_urlsafe(32)
            success = db_manager.create_session(request.user_id, session_token, request.expires_in_hours)
            if success:
                return ApiResponse(success=True, data={"session_token": session_token})
            else:
                return ApiResponse(success=False, error="Failed to create session")
        else:
            return ApiResponse(success=False, error="Database not available")
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

@app.post("/auth/validate-session", response_model=ApiResponse)
async def validate_session(request: ValidateSessionRequest):
    """Validate session token and return user ID."""
    try:
        if DATABASE_AVAILABLE:
            user_id = db_manager.validate_session(request.session_token)
            if user_id:
                return ApiResponse(success=True, data={"user_id": user_id, "valid": True})
            else:
                return ApiResponse(success=True, data={"user_id": None, "valid": False})
        else:
            return ApiResponse(success=False, error="Database not available")
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

@app.post("/auth/logout", response_model=ApiResponse)
async def logout(request: ValidateSessionRequest):
    """Logout user by invalidating session."""
    try:
        if DATABASE_AVAILABLE:
            success = db_manager.delete_session(request.session_token)
            if success:
                return ApiResponse(success=True, message="Logged out successfully")
            else:
                return ApiResponse(success=False, error="Failed to logout")
        else:
            return ApiResponse(success=False, error="Database not available")
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

# Resume processing endpoints
@app.post("/process/resume", response_model=ApiResponse)
async def process_resume(
    file: UploadFile = File(...),
    api_key: Optional[str] = Form(None),
    custom_prompt: Optional[str] = Form(None),
    user_id: Optional[int] = Form(None),
    custom_prompt_name: Optional[str] = Form(None)
):
    """Process resume through 3-step AI pipeline."""
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            return ApiResponse(success=False, error="Only PDF files are supported")
        
        # Obtain API key: use provided, otherwise fallback to stored key for the user
        effective_api_key = api_key
        if not effective_api_key and user_id and DATABASE_AVAILABLE:
            effective_api_key = db_manager.get_api_key_plaintext(user_id)

        # Validate API key
        if not effective_api_key or not validate_api_key(effective_api_key):
            return ApiResponse(success=False, error="Invalid or missing API key")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            temp_path = tmp_file.name
        
        try:
            # Initialize token tracking
            total_tokens = {
                'input_tokens': 0,
                'output_tokens': 0,
                'total_tokens': 0
            }
            
            # Initialize chains
            restructure_chain = ResumeRestructureChain(api_key=effective_api_key, custom_prompt=custom_prompt)
            formatter = ResumeFormatter(api_key=effective_api_key)
            
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
            
            # Track tokens from Step 1
            if hasattr(step1_result, 'processing_metadata') and step1_result.processing_metadata:
                usage = step1_result.processing_metadata.get('usage_metadata', {})
                total_tokens['input_tokens'] += usage.get('input_tokens', 0)
                total_tokens['output_tokens'] += usage.get('output_tokens', 0)
                total_tokens['total_tokens'] += usage.get('total_tokens', 0)
            
            # Step 2: First restructuring
            restructured_from_data = restructure_chain.restructure_from_data(
                extracted_data, 
                reference_number="SDA02-AMH"
            )
            
            # Track tokens from Step 2
            if hasattr(restructure_chain, 'last_usage_metadata') and restructure_chain.last_usage_metadata:
                usage = restructure_chain.last_usage_metadata
                total_tokens['input_tokens'] += usage.get('input_tokens', 0)
                total_tokens['output_tokens'] += usage.get('output_tokens', 0)
                total_tokens['total_tokens'] += usage.get('total_tokens', 0)
            
            # Step 3: Second restructuring
            step3_request = ResumeProcessingRequest(
                file_path="",
                content=restructured_from_data,
                target_role="Software Engineer",
                template_style="professional",
                enhance_content=False,
                ats_optimize=False
            )
            
            step3_result = formatter.format(step3_request)
            
            # Track tokens from Step 3
            if hasattr(step3_result, 'processing_metadata') and step3_result.processing_metadata:
                usage = step3_result.processing_metadata.get('usage_metadata', {})
                total_tokens['input_tokens'] += usage.get('input_tokens', 0)
                total_tokens['output_tokens'] += usage.get('output_tokens', 0)
                total_tokens['total_tokens'] += usage.get('total_tokens', 0)
            
            # Calculate cost (Gemini 2.5 Flash pricing)
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
                    "original_filename": file.filename,
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
            
            # Save to database if user is logged in and database is available
            if DATABASE_AVAILABLE and user_id:
                try:
                    # Save processing history
                    metadata = {
                        'target_role': 'Software Engineer',
                        'template_style': 'professional',
                        'steps_completed': 3,
                        'prompt_used': custom_prompt_name or 'Default'
                    }
                    history_id = db_manager.save_processing_history(user_id, file.filename, metadata)
                    
                    if history_id:
                        # Save processing result
                        db_manager.save_processing_result(history_id, results["step3_final_data"])
                        
                        # Save token usage data
                        token_data = {
                            'input_tokens': total_tokens['input_tokens'],
                            'output_tokens': total_tokens['output_tokens'],
                            'total_tokens': total_tokens['total_tokens'],
                            'input_cost_usd': input_cost,
                            'output_cost_usd': output_cost,
                            'total_cost_usd': total_cost,
                            'model': 'gemini-2.5-flash'
                        }
                        db_manager.save_token_usage(user_id, history_id, token_data)
                        
                        print(f"✅ Saved processing history and token usage for user {user_id}")
                    else:
                        print(f"⚠️ Failed to save processing history for user {user_id}")
                except Exception as e:
                    print(f"⚠️ Error saving to database: {e}")
                    # Don't fail the request if database save fails
            
            return ApiResponse(success=True, data=results)
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    except Exception as e:
        return ApiResponse(success=False, error=str(e))


# Incremental processing endpoints
class StartProcessResponse(BaseModel):
    job_id: str

@app.post("/process/start", response_model=ApiResponse)
async def start_process(
    file: UploadFile = File(...),
    api_key: Optional[str] = Form(None),
    custom_prompt: Optional[str] = Form(None),
    user_id: Optional[int] = Form(None),
    custom_prompt_name: Optional[str] = Form(None)
):
    """Start processing and return a job_id immediately; progress is available via /process/status/{job_id}."""
    try:
        if not file.filename.endswith('.pdf'):
            return ApiResponse(success=False, error="Only PDF files are supported")

        # Determine effective API key
        effective_api_key = api_key
        if not effective_api_key and user_id and DATABASE_AVAILABLE:
            effective_api_key = db_manager.get_api_key_plaintext(user_id)
        if not effective_api_key or not validate_api_key(effective_api_key):
            return ApiResponse(success=False, error="Invalid or missing API key")

        # Save file to temp
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            temp_path = tmp_file.name

        job_id = uuid.uuid4().hex
        JOBS[job_id] = {
            'status': 'running',
            'steps': [
                {'step': 1, 'name': 'Extract Data', 'status': 'pending'},
                {'step': 2, 'name': 'Restructure', 'status': 'pending'},
                {'step': 3, 'name': 'Final Format', 'status': 'pending'},
            ],
            'data': {},
            'error': None,
            'token_usage': {
                'input_tokens': 0,
                'output_tokens': 0,
                'total_tokens': 0,
            }
        }

        async def run_job():
            try:
                total_tokens = JOBS[job_id]['token_usage']

                restructure_chain = ResumeRestructureChain(api_key=effective_api_key, custom_prompt=custom_prompt)
                formatter = ResumeFormatter(api_key=effective_api_key)

                # Step 1
                JOBS[job_id]['steps'][0]['status'] = 'processing'
                # yield control so status endpoint can serve
                await asyncio.sleep(0)
                request1 = ResumeProcessingRequest(
                    file_path=temp_path,
                    target_role="Software Engineer",
                    template_style="professional",
                    enhance_content=False,
                    ats_optimize=False
                )
                # Offload blocking call to thread
                step1_result = await asyncio.to_thread(formatter.format, request1)
                JOBS[job_id]['data']['step1_extracted_data'] = step1_result.extracted_data.model_dump()
                if hasattr(step1_result, 'processing_metadata') and step1_result.processing_metadata:
                    usage = step1_result.processing_metadata.get('usage_metadata', {})
                    total_tokens['input_tokens'] += usage.get('input_tokens', 0)
                    total_tokens['output_tokens'] += usage.get('output_tokens', 0)
                    total_tokens['total_tokens'] += usage.get('total_tokens', 0)
                JOBS[job_id]['steps'][0]['status'] = 'completed'
                await asyncio.sleep(0)

                # Step 2
                JOBS[job_id]['steps'][1]['status'] = 'processing'
                await asyncio.sleep(0)
                restructured_from_data = await asyncio.to_thread(
                    restructure_chain.restructure_from_data,
                    step1_result.extracted_data )
                JOBS[job_id]['data']['step2_restructured_text'] = restructured_from_data
                if hasattr(restructure_chain, 'last_usage_metadata') and restructure_chain.last_usage_metadata:
                    usage = restructure_chain.last_usage_metadata
                    total_tokens['input_tokens'] += usage.get('input_tokens', 0)
                    total_tokens['output_tokens'] += usage.get('output_tokens', 0)
                    total_tokens['total_tokens'] += usage.get('total_tokens', 0)
                JOBS[job_id]['steps'][1]['status'] = 'completed'
                await asyncio.sleep(0)

                # Step 3
                JOBS[job_id]['steps'][2]['status'] = 'processing'
                await asyncio.sleep(0)
                request3 = ResumeProcessingRequest(
                    file_path="",
                    content=restructured_from_data,
                    target_role="Software Engineer",
                    template_style="professional",
                    enhance_content=False,
                    ats_optimize=False
                )
                step3_result = await asyncio.to_thread(formatter.format, request3)
                JOBS[job_id]['data']['step3_final_data'] = step3_result.extracted_data.model_dump()
                JOBS[job_id]['data']['step3_final_formatted'] = step3_result.formatted_resume
                if hasattr(step3_result, 'processing_metadata') and step3_result.processing_metadata:
                    usage = step3_result.processing_metadata.get('usage_metadata', {})
                    total_tokens['input_tokens'] += usage.get('input_tokens', 0)
                    total_tokens['output_tokens'] += usage.get('output_tokens', 0)
                    total_tokens['total_tokens'] += usage.get('total_tokens', 0)

                input_cost = (total_tokens['input_tokens'] / 1000) * 0.000125
                output_cost = (total_tokens['output_tokens'] / 1000) * 0.000375
                total_cost = input_cost + output_cost
                JOBS[job_id]['data']['token_usage'] = {
                    'total_tokens': total_tokens,
                    'cost_estimation': {
                        'input_cost_usd': round(input_cost, 6),
                        'output_cost_usd': round(output_cost, 6),
                        'total_cost_usd': round(total_cost, 6),
                        'model': 'gemini-2.5-flash'
                    }
                }

                JOBS[job_id]['status'] = 'completed'
            except Exception as e:
                JOBS[job_id]['status'] = 'error'
                JOBS[job_id]['error'] = str(e)
            finally:
                try:
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                except Exception:
                    pass

        # Launch background task
        asyncio.create_task(run_job())

        return ApiResponse(success=True, data={'job_id': job_id})
    except Exception as e:
        return ApiResponse(success=False, error=str(e))


@app.get("/process/status/{job_id}", response_model=ApiResponse)
async def get_process_status(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return ApiResponse(success=False, error="Job not found")
    return ApiResponse(success=True, data=job)

@app.post("/export/docx")
async def export_docx(request: ExportDocxRequest):
    """Export resume data as DOCX file."""
    # try:
        # Create temporary file for DOCX
    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
        temp_path = tmp_file.name
    
    try:

        # Generate DOCX using existing generator
        generator = ResumeDocumentGenerator()  # Initialize with default page_height
        generator.generate_docx(json.dumps(request.data), temp_path)
        
        # Return file
        return FileResponse(
            temp_path,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            filename=request.filename
        )
        
    finally:
        # Note: File will be cleaned up after response is sent
        pass
    
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))

# History endpoints
@app.get("/history/{user_id}", response_model=ApiResponse)
async def get_processing_history(user_id: int, limit: int = 10):
    """Get processing history for user."""
    try:
        if DATABASE_AVAILABLE:
            history = db_manager.get_processing_history(user_id, limit)
            return ApiResponse(success=True, data=history)
        else:
            return ApiResponse(success=False, error="Database not available")
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

@app.get("/history/result/{history_id}", response_model=ApiResponse)
async def get_processing_result(history_id: int):
    """Get specific processing result."""
    try:
        if DATABASE_AVAILABLE:
            result = db_manager.get_processing_result(history_id)
            if result:
                return ApiResponse(success=True, data=result['result_data'])
            else:
                return ApiResponse(success=False, error="Result not found")
        else:
            return ApiResponse(success=False, error="Database not available")
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

@app.delete("/history/{history_id}", response_model=ApiResponse)
async def delete_history(history_id: int, user_id: int):
    """Delete processing history record."""
    try:
        if DATABASE_AVAILABLE:
            # TODO: Implement delete functionality in database manager
            return ApiResponse(success=True, message="Delete functionality not implemented yet")
        else:
            return ApiResponse(success=False, error="Database not available")
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

# Prompt management endpoints
@app.get("/prompts/{user_id}", response_model=ApiResponse)
async def get_custom_prompts(user_id: int):
    """Get custom prompts for user."""
    try:
        if DATABASE_AVAILABLE:
            prompts = db_manager.get_custom_prompts(user_id)
            return ApiResponse(success=True, data=prompts)
        else:
            return ApiResponse(success=False, error="Database not available")
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

@app.post("/prompts", response_model=ApiResponse)
async def save_custom_prompt(request: SavePromptRequest):
    """Save custom prompt."""
    try:
        if DATABASE_AVAILABLE:
            success = db_manager.save_custom_prompt(request.user_id, request.name, request.prompt_text)
            if success:
                return ApiResponse(success=True, message="Prompt saved successfully")
            else:
                return ApiResponse(success=False, error="Failed to save prompt")
        else:
            return ApiResponse(success=False, error="Database not available")
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

@app.delete("/prompts/{prompt_id}", response_model=ApiResponse)
async def delete_custom_prompt(prompt_id: int, user_id: int):
    """Delete custom prompt."""
    try:
        if DATABASE_AVAILABLE:
            success = db_manager.delete_custom_prompt(prompt_id, user_id)
            if success:
                return ApiResponse(success=True, message="Prompt deleted successfully")
            else:
                return ApiResponse(success=False, error="Failed to delete prompt")
        else:
            return ApiResponse(success=False, error="Database not available")
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

# Token usage endpoints
@app.get("/tokens/{user_id}", response_model=ApiResponse)
async def get_token_usage(user_id: int):
    """Get token usage history for user."""
    try:
        if DATABASE_AVAILABLE:
            usage = db_manager.get_token_usage_history(user_id)
            return ApiResponse(success=True, data=usage)
        else:
            return ApiResponse(success=False, error="Database not available")
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

@app.get("/tokens/stats/{user_id}", response_model=ApiResponse)
async def get_token_stats(user_id: int):
    """Get token usage statistics for user."""
    try:
        if DATABASE_AVAILABLE:
            stats = db_manager.get_token_usage_stats(user_id)
            return ApiResponse(success=True, data=stats)
        else:
            return ApiResponse(success=False, error="Database not available")
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

if __name__ == "__main__":
    print("🚀 Starting Resume Processor API Server...")
    print("📍 API will be available at: http://localhost:8000")
    print("📖 API docs available at: http://localhost:8000/docs")

    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
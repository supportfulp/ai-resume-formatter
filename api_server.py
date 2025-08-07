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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
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

# Resume processing endpoints
@app.post("/process/resume", response_model=ApiResponse)
async def process_resume(
    file: UploadFile = File(...),
    api_key: str = Form(...),
    custom_prompt: Optional[str] = Form(None)
):
    """Process resume through 3-step AI pipeline."""
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            return ApiResponse(success=False, error="Only PDF files are supported")
        
        # Validate API key
        if not validate_api_key(api_key):
            return ApiResponse(success=False, error="Invalid API key format")
        
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
            restructure_chain = ResumeRestructureChain(api_key=api_key, custom_prompt=custom_prompt)
            formatter = ResumeFormatter(api_key=api_key)
            
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
            
            return ApiResponse(success=True, data=results)
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    except Exception as e:
        return ApiResponse(success=False, error=str(e))

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
# Resume Processor API Backend

This is the FastAPI backend that provides REST API endpoints for the React frontend. It replicates all the functionality of the Streamlit app in a REST API format.

## Features

### 🔐 Authentication Endpoints
- **POST /auth/login** - User authentication
- **POST /auth/register** - User registration  
- **POST /auth/verify-api-key** - Google API key validation

### 📁 Resume Processing Endpoints
- **POST /process/resume** - 3-step AI resume processing
- **POST /export/docx** - Export resume as DOCX file

### 📊 History Management Endpoints
- **GET /history/{user_id}** - Get processing history
- **GET /history/result/{history_id}** - Get specific result
- **DELETE /history/{history_id}** - Delete history record

### 🔧 Prompt Management Endpoints
- **GET /prompts/{user_id}** - Get custom prompts
- **POST /prompts** - Save custom prompt
- **DELETE /prompts/{prompt_id}** - Delete custom prompt

### 💰 Token Usage Endpoints
- **GET /tokens/{user_id}** - Get token usage history
- **GET /tokens/stats/{user_id}** - Get usage statistics

## Quick Start

### 1. Install Dependencies
```bash
# Install API server dependencies
pip install -r api_requirements.txt

# Or use the startup script (recommended)
python start_api_server.py
```

### 2. Database Setup
Ensure your PostgreSQL database is running and configured:

```bash
# Environment variables (create .env file)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=resume_processor
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
```

### 3. Start the Server
```bash
# Using the startup script (recommended)
python start_api_server.py

# Or directly with uvicorn
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **Server**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

## Environment Setup

### Required Environment Variables
```bash
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=resume_processor
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# Optional: Google API Key (can also be set via API)
GOOGLE_API_KEY=your_google_api_key
```

### Conda Environment (Recommended)
```bash
# Activate the rf environment as per your memory
conda activate rf

# Install dependencies
pip install -r api_requirements.txt

# Start the server
python start_api_server.py
```

## API Documentation

### Authentication Flow
1. **Register/Login**: Create account or login with existing credentials
2. **Demo Mode**: Use username `demo` / password `demo123` for testing
3. **API Key Setup**: Provide Google API key for AI processing

### Resume Processing Flow
1. **Upload File**: POST multipart/form-data with PDF file
2. **Process**: Server runs 3-step AI pipeline
3. **Return Results**: JSON response with all processing steps
4. **Token Tracking**: Automatic cost and usage tracking

### Response Format
All endpoints return standardized responses:
```json
{
  "success": true,
  "data": {...},
  "error": null,
  "message": "Optional message"
}
```

## Development

### Project Structure
```
├── api_server.py              # Main FastAPI application
├── start_api_server.py        # Startup script with environment checks
├── api_requirements.txt       # API-specific dependencies
├── database.py                # Database operations (existing)
└── src/                       # Resume processing logic (existing)
    ├── chains/
    ├── models/
    ├── prompts/
    └── docx_export/
```

### Key Components

#### FastAPI App (`api_server.py`)
- CORS configuration for React frontend
- Request/response models with Pydantic
- Error handling and validation
- File upload handling
- Database integration

#### Database Integration
- Uses existing `database.py` module
- PostgreSQL with proper connection pooling
- Transaction management
- Error handling and logging

#### Processing Pipeline
- Integrates existing resume processing chains
- Token usage tracking
- Cost calculation
- Temporary file management

### Adding New Endpoints

1. **Define Pydantic Models**:
```python
class NewRequest(BaseModel):
    field1: str
    field2: Optional[int] = None
```

2. **Create Endpoint**:
```python
@app.post("/new-endpoint", response_model=ApiResponse)
async def new_endpoint(request: NewRequest):
    try:
        # Process request
        result = process_data(request)
        return ApiResponse(success=True, data=result)
    except Exception as e:
        return ApiResponse(success=False, error=str(e))
```

3. **Add Database Methods** (if needed):
```python
def new_database_method(self, param1: str) -> bool:
    try:
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SQL QUERY", (param1,))
                conn.commit()
                return True
    except Exception as e:
        logger.error(f"Error: {e}")
        return False
```

## Testing

### Manual Testing
Use the built-in FastAPI docs at http://localhost:8000/docs

### Example Requests

#### Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "demo123"}'
```

#### Process Resume
```bash
curl -X POST "http://localhost:8000/process/resume" \
  -F "file=@resume.pdf" \
  -F "api_key=your_google_api_key"
```

## Production Deployment

### Using Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . /app

RUN pip install -r api_requirements.txt
EXPOSE 8000

CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Using Gunicorn
```bash
pip install gunicorn
gunicorn api_server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Environment Variables for Production
```bash
# Database
POSTGRES_HOST=your_db_host
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password

# Security
SECRET_KEY=your_secret_key
ALLOWED_ORIGINS=https://your-frontend-domain.com

# API Settings
MAX_FILE_SIZE=10485760  # 10MB
UPLOAD_DIR=/tmp/uploads
```

## Monitoring and Logging

### Health Check
```bash
curl http://localhost:8000/health
```

### Logs
The server logs important events:
- Database connections
- Processing requests
- Token usage
- Errors and exceptions

### Metrics
Track these metrics in production:
- Request count and response times
- Database connection pool usage
- File upload sizes and processing times
- Token usage and costs

## Security Considerations

### API Key Handling
- Never log full API keys
- Store hashed versions in database
- Validate format before processing

### File Uploads
- Validate file types (PDF only)
- Limit file sizes
- Clean up temporary files
- Scan for malicious content in production

### Database Security
- Use connection pooling
- Parameterized queries (already implemented)
- Regular backups
- Access controls

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check PostgreSQL is running
   - Verify credentials in .env file
   - Check network connectivity

2. **Import Errors**
   - Ensure all dependencies are installed
   - Check Python path includes src/ directory
   - Verify conda environment is activated

3. **File Upload Issues**
   - Check file permissions
   - Verify disk space
   - Ensure proper CORS headers

4. **Processing Errors**
   - Validate Google API key
   - Check API quotas and limits
   - Monitor token usage

### Debug Mode
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Integration with React Frontend

The API is designed to work seamlessly with the React frontend:

1. **CORS**: Configured for localhost:3000
2. **Response Format**: Matches frontend expectations
3. **Error Handling**: Consistent error responses
4. **File Handling**: Supports React dropzone uploads

Start both servers:
```bash
# Terminal 1: API Server
python start_api_server.py

# Terminal 2: React Frontend
cd resume-processor-react
npm start
```

The complete application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
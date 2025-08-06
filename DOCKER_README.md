# Docker Setup for Resume Processor

This project now uses a modern architecture with:
- **React Frontend** - Modern UI with TypeScript and Tailwind CSS
- **FastAPI Backend** - RESTful API server
- **PostgreSQL Database** - Data persistence
- **Nginx** - Reverse proxy (production)

## Quick Start

### Development Mode
```bash
# Start with development React app (hot reload enabled)
./start_docker.sh development

# Or manually:
docker-compose --profile development up -d postgres api-server react-app
```

**Access URLs:**
- React App: http://localhost:3000
- API Server: http://localhost:8000
- Database: localhost:5432

### Production Mode
```bash
# Start with production React app (built and optimized)
./start_docker.sh production

# Or manually:
docker-compose --profile production up -d
```

**Access URLs:**
- Application: http://localhost (via nginx proxy)
- Database: localhost:5432

### Full Stack (with nginx proxy)
```bash
# Start all services including nginx reverse proxy
./start_docker.sh full

# Or manually:
docker-compose up -d
```

**Access URLs:**
- Application: http://localhost (nginx proxy)
- React App: http://localhost:3000
- API Server: http://localhost:8000
- Database: localhost:5432

## Services

### 1. PostgreSQL Database (`postgres`)
- **Port:** 5432
- **Database:** resume_processor
- **User:** postgres
- **Password:** password
- **Health Check:** Automatic with retry logic

### 2. FastAPI Backend (`api-server`)
- **Port:** 8000
- **Framework:** FastAPI with uvicorn
- **Features:** 
  - RESTful API endpoints
  - File upload processing
  - Database integration
  - Authentication
  - Token usage tracking
- **Health Check:** `/health` endpoint

### 3. React Frontend (`react-app` / `react-app-prod`)
- **Development Port:** 3000 (with hot reload)
- **Production Port:** 80 (built and served by nginx)
- **Framework:** React 18 with TypeScript
- **Styling:** Tailwind CSS
- **State Management:** Zustand
- **API Integration:** Axios with automatic proxy support

### 4. Nginx Reverse Proxy (`nginx`)
- **Port:** 80
- **Features:**
  - Routes `/api/*` to FastAPI backend
  - Routes all other requests to React app
  - Security headers
  - Gzip compression
  - Health check endpoint

## Docker Compose Profiles

### Development Profile
- `postgres` - Database
- `api-server` - FastAPI backend
- `react-app` - Development React app with hot reload

### Production Profile
- `postgres` - Database
- `api-server` - FastAPI backend
- `react-app-prod` - Production React app (built)
- `nginx` - Reverse proxy

## Environment Variables

### API Server
```env
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=resume_processor
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
PYTHONPATH=/app
```

### React App
```env
REACT_APP_API_URL=http://localhost:8000  # Development only
CHOKIDAR_USEPOLLING=true                 # Development only
```

## Development Workflow

1. **Start services:**
   ```bash
   ./start_docker.sh development
   ```

2. **Make changes to code:**
   - React changes auto-reload at http://localhost:3000
   - API changes auto-reload at http://localhost:8000

3. **View logs:**
   ```bash
   docker-compose logs -f [service-name]
   ```

4. **Stop services:**
   ```bash
   docker-compose down
   ```

## Production Deployment

1. **Build and start production:**
   ```bash
   ./start_docker.sh production
   ```

2. **Access the application:**
   - Main app: http://localhost
   - API docs: http://localhost/api/docs

3. **Monitor logs:**
   ```bash
   docker-compose logs -f
   ```

## Troubleshooting

### Common Issues

1. **Port conflicts:**
   ```bash
   # Check what's using the ports
   lsof -i :3000
   lsof -i :8000
   lsof -i :5432
   ```

2. **Database connection issues:**
   ```bash
   # Check database logs
   docker-compose logs postgres
   ```

3. **React app not loading:**
   ```bash
   # Check React app logs
   docker-compose logs react-app
   ```

4. **API server not responding:**
   ```bash
   # Check API server logs
   docker-compose logs api-server
   ```

### Reset Everything
```bash
# Stop and remove all containers, networks, and volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Start fresh
./start_docker.sh development
```

## File Structure

```
resume_project/
├── docker-compose.yml          # Main compose file
├── Dockerfile.api              # FastAPI backend Dockerfile
├── start_docker.sh             # Convenience script
├── nginx.conf                  # Nginx proxy configuration
├── resume-processor-react/
│   ├── Dockerfile              # Development React Dockerfile
│   ├── Dockerfile.prod         # Production React Dockerfile
│   └── nginx.conf              # React app nginx config
└── ...
```

## API Endpoints

When running behind nginx proxy, API endpoints are available at:
- `http://localhost/api/auth/*` - Authentication
- `http://localhost/api/process/*` - Resume processing
- `http://localhost/api/history/*` - Processing history
- `http://localhost/api/prompts/*` - Custom prompts
- `http://localhost/api/tokens/*` - Token usage
- `http://localhost/api/export/*` - Document export

In development mode, use direct API server URLs:
- `http://localhost:8000/auth/*`
- `http://localhost:8000/process/*`
- etc. 
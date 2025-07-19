# Docker Deployment Guide

This guide explains how to deploy the Resume Processing Tool using Docker and Docker Compose.

## 🐳 Quick Start

### Prerequisites
- Docker
- Docker Compose
- Google API Key for Gemini

### 1. Set Environment Variables
Create a `.env` file in the project root:
```bash
GOOGLE_API_KEY=your_google_api_key_here
```

### 2. Build and Run
```bash
# Development mode (with source code mounting)
docker-compose up --build

# Production mode (with nginx reverse proxy)
docker-compose --profile production up --build
```

### 3. Access the Application
- **Development**: http://localhost:8501
- **Production**: http://localhost:80

## 🏗️ Architecture

### Development Setup
```
┌─────────────────┐
│   Your Browser  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Streamlit App  │
│   Port: 8501    │
└─────────────────┘
```

### Production Setup
```
┌─────────────────┐
│   Your Browser  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│     Nginx       │
│   Port: 80      │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Streamlit App  │
│   Port: 8501    │
└─────────────────┘
```

## 📁 File Structure

```
├── Dockerfile              # Main application container
├── docker-compose.yml      # Multi-service orchestration
├── nginx.conf             # Nginx reverse proxy config
├── .dockerignore          # Docker build exclusions
├── .env                   # Environment variables (create this)
├── streamlit_app.py       # Main Streamlit application
├── src/                   # Application source code
├── requirements.txt       # Python dependencies
└── output/               # Persistent output directory
```

## 🔧 Configuration

### Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google API key for Gemini | Yes |

### Ports
| Service | Port | Description |
|---------|------|-------------|
| Streamlit | 8501 | Main application |
| Nginx | 80 | Reverse proxy (production) |

### Volumes
| Volume | Purpose |
|--------|---------|
| `./src:/app/src` | Source code mounting (development) |
| `./output:/app/output` | Persistent output storage |
| `./streamlit_app.py:/app/streamlit_app.py` | App mounting (development) |

## 🚀 Deployment Options

### Development Mode
```bash
# Start with source code mounting for live development
docker-compose up --build

# View logs
docker-compose logs -f resume-processor

# Stop services
docker-compose down
```

### Production Mode
```bash
# Start with nginx reverse proxy
docker-compose --profile production up --build

# Run in background
docker-compose --profile production up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose --profile production down
```

### Custom Configuration
```bash
# Use custom environment file
docker-compose --env-file .env.production up

# Override ports
docker-compose up -p 9001:8501

# Scale services (if needed)
docker-compose up --scale resume-processor=2
```

## 🔍 Monitoring & Health Checks

### Health Check Endpoints
- **Streamlit**: http://localhost:8501/_stcore/health
- **Nginx**: http://localhost/health

### Logs
```bash
# View all logs
docker-compose logs

# Follow logs
docker-compose logs -f

# View specific service logs
docker-compose logs resume-processor
docker-compose logs nginx
```

### Container Status
```bash
# Check container status
docker-compose ps

# Check resource usage
docker stats
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
lsof -i :8501

# Kill the process or change port in docker-compose.yml
```

#### 2. Permission Issues
```bash
# Fix output directory permissions
sudo chown -R $USER:$USER ./output
chmod 755 ./output
```

#### 3. API Key Issues
```bash
# Verify environment variable
docker-compose exec resume-processor env | grep GOOGLE_API_KEY

# Restart with new environment
docker-compose down
docker-compose up --build
```

#### 4. Build Failures
```bash
# Clean build
docker-compose down
docker system prune -f
docker-compose up --build --force-recreate
```

### Debug Mode
```bash
# Run with debug output
docker-compose up --build --verbose

# Access container shell
docker-compose exec resume-processor bash
```

## 🔒 Security Considerations

### Production Security
1. **Use HTTPS**: Configure SSL certificates in nginx
2. **Environment Variables**: Never commit `.env` files
3. **Network Security**: Use Docker networks for service isolation
4. **User Permissions**: Container runs as non-root user
5. **Security Headers**: Nginx includes security headers

### Security Headers (Nginx)
- X-Frame-Options: SAMEORIGIN
- X-XSS-Protection: 1; mode=block
- X-Content-Type-Options: nosniff
- Content-Security-Policy: configured

## 📊 Performance Optimization

### Resource Limits
Add to `docker-compose.yml`:
```yaml
services:
  resume-processor:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
```

### Caching
- Docker layer caching for faster builds
- Streamlit caching for processed results
- Nginx caching for static assets

## 🔄 CI/CD Integration

### GitHub Actions Example
```yaml
name: Deploy to Production
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy with Docker Compose
        run: |
          docker-compose --profile production up -d --build
```

## 📝 Maintenance

### Regular Tasks
1. **Update Dependencies**: `docker-compose build --no-cache`
2. **Clean Up**: `docker system prune -f`
3. **Backup Data**: Backup `./output` directory
4. **Monitor Logs**: Check for errors regularly
5. **Security Updates**: Update base images periodically

### Backup Strategy
```bash
# Backup output directory
tar -czf backup-$(date +%Y%m%d).tar.gz ./output

# Restore backup
tar -xzf backup-20231201.tar.gz
```

## 🆘 Support

For issues related to:
- **Docker**: Check Docker logs and documentation
- **Streamlit**: Check Streamlit documentation
- **Application**: Check application logs and error messages
- **API**: Verify Google API key and quotas 
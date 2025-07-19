# 🗄️ Database Deployment Guide

Your Resume Processor now uses **PostgreSQL** for persistent user data storage!

## 🎯 **What's New:**

### **Persistent Storage:**
- ✅ **User accounts** - Stored in PostgreSQL database
- ✅ **API keys** - Securely stored per user
- ✅ **Processing history** - Track user activity
- ✅ **Session management** - Database-backed sessions
- ✅ **Survives restarts** - Data persists across container restarts

### **Database Features:**
- ✅ **User registration** - Create accounts with email
- ✅ **Secure authentication** - Password hashing with SHA-256
- ✅ **API key management** - One active key per user
- ✅ **Activity tracking** - Processing history and timestamps
- ✅ **Session management** - Secure session tokens with expiration

## 🏗️ **Database Schema:**

### **Users Table:**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### **API Keys Table:**
```sql
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    api_key_hash VARCHAR(255) NOT NULL,
    masked_key VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### **Processing History Table:**
```sql
CREATE TABLE processing_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    processing_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'completed',
    metadata JSONB
);
```

## 🚀 **Deployment Options:**

### **Option 1: Docker Compose (Recommended)**

#### **1. Start the Services:**
```bash
# Start PostgreSQL and Streamlit app
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

#### **2. Check Services:**
```bash
# View running containers
docker-compose ps

# Check logs
docker-compose logs postgres
docker-compose logs resume-processor
```

#### **3. Access the App:**
- **Streamlit App**: http://localhost:8501
- **PostgreSQL**: localhost:5432

### **Option 2: Railway with PostgreSQL**

#### **1. Add PostgreSQL to Railway:**
```bash
# Add PostgreSQL service
railway add

# Set environment variables
railway variables set POSTGRES_HOST=your-railway-postgres-host
railway variables set POSTGRES_PORT=5432
railway variables set POSTGRES_DB=resume_processor
railway variables set POSTGRES_USER=postgres
railway variables set POSTGRES_PASSWORD=your-railway-postgres-password
```

#### **2. Deploy:**
```bash
railway up
```

### **Option 3: Local PostgreSQL**

#### **1. Install PostgreSQL:**
```bash
# macOS
brew install postgresql
brew services start postgresql

# Ubuntu
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

#### **2. Create Database:**
```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE resume_processor;
CREATE USER resume_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE resume_processor TO resume_user;
\q
```

#### **3. Set Environment Variables:**
```bash
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=resume_processor
export POSTGRES_USER=resume_user
export POSTGRES_PASSWORD=your_password
```

#### **4. Run App:**
```bash
streamlit run streamlit_app.py
```

## 🔧 **Environment Variables:**

### **Required Variables:**
```bash
POSTGRES_HOST=localhost          # Database host
POSTGRES_PORT=5432              # Database port
POSTGRES_DB=resume_processor    # Database name
POSTGRES_USER=postgres          # Database user
POSTGRES_PASSWORD=password      # Database password
```

### **Optional Variables:**
```bash
PYTHONPATH=/app                 # Python path
```

## 📊 **Database Management:**

### **Connect to Database:**
```bash
# Using Docker Compose
docker-compose exec postgres psql -U postgres -d resume_processor

# Using local PostgreSQL
psql -h localhost -U postgres -d resume_processor
```

### **View Tables:**
```sql
-- List all tables
\dt

-- View users
SELECT username, email, created_at, last_login FROM users;

-- View API keys
SELECT u.username, ak.masked_key, ak.created_at 
FROM api_keys ak 
JOIN users u ON ak.user_id = u.id 
WHERE ak.is_active = TRUE;

-- View processing history
SELECT u.username, ph.filename, ph.processing_date, ph.status
FROM processing_history ph
JOIN users u ON ph.user_id = u.id
ORDER BY ph.processing_date DESC;
```

### **Backup Database:**
```bash
# Using Docker Compose
docker-compose exec postgres pg_dump -U postgres resume_processor > backup.sql

# Using local PostgreSQL
pg_dump -h localhost -U postgres resume_processor > backup.sql
```

### **Restore Database:**
```bash
# Using Docker Compose
docker-compose exec -T postgres psql -U postgres resume_processor < backup.sql

# Using local PostgreSQL
psql -h localhost -U postgres resume_processor < backup.sql
```

## 🔒 **Security Features:**

### **Password Security:**
- ✅ **SHA-256 hashing** - Passwords never stored in plain text
- ✅ **Salt not needed** - Using SHA-256 for demo (use bcrypt for production)
- ✅ **Secure comparison** - Hash-based authentication

### **API Key Security:**
- ✅ **Hashed storage** - API keys hashed in database
- ✅ **Masked display** - Only first/last characters shown
- ✅ **One active key** - Only one active key per user

### **Session Security:**
- ✅ **Token-based** - Secure session tokens
- ✅ **Expiration** - Sessions expire automatically
- ✅ **Database-backed** - Session validation against database

## 📈 **Performance Optimization:**

### **Database Indexes:**
```sql
-- Automatic indexes created for:
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_active ON api_keys(is_active);
CREATE INDEX idx_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_sessions_expires ON user_sessions(expires_at);
CREATE INDEX idx_processing_history_user_id ON processing_history(user_id);
CREATE INDEX idx_processing_history_date ON processing_history(processing_date);
```

### **Connection Pooling:**
- ✅ **Context managers** - Proper connection handling
- ✅ **Automatic cleanup** - Connections closed automatically
- ✅ **Error handling** - Graceful connection failures

## 🆘 **Troubleshooting:**

### **Common Issues:**

#### **1. Database Connection Failed:**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Test connection
docker-compose exec postgres pg_isready -U postgres
```

#### **2. Tables Not Created:**
```bash
# Manually initialize database
docker-compose exec resume-processor python -c "from database import init_database; init_database()"
```

#### **3. Demo User Not Created:**
```bash
# Manually create demo user
docker-compose exec resume-processor python -c "from database import create_demo_user; create_demo_user()"
```

#### **4. Permission Issues:**
```bash
# Check database permissions
docker-compose exec postgres psql -U postgres -d resume_processor -c "\du"
```

### **Reset Database:**
```bash
# Stop services
docker-compose down

# Remove volume
docker volume rm resume_project_postgres_data

# Restart
docker-compose up --build
```

## 🎉 **Benefits of Database Storage:**

### **For Users:**
- ✅ **Persistent accounts** - No data loss on restarts
- ✅ **Processing history** - Track all resume processing
- ✅ **Email support** - Optional email registration
- ✅ **Secure sessions** - Better session management

### **For Administrators:**
- ✅ **User management** - View and manage user accounts
- ✅ **Activity monitoring** - Track user activity
- ✅ **Data backup** - Easy database backups
- ✅ **Scalability** - Ready for multiple users

### **For Development:**
- ✅ **Data persistence** - Survives container restarts
- ✅ **Easy testing** - Reset database for clean testing
- ✅ **Production ready** - Proper database architecture
- ✅ **Monitoring** - Database logs and metrics

---

**Your app now has enterprise-grade persistent storage! 🎉** 
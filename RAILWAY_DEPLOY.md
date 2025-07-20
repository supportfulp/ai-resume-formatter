# 🚂 Railway Deployment Guide

The **easiest way** to deploy your resume processor to a public URL!

## 🎯 Quick Deploy (5 minutes)

### 1. Install Railway CLI
```bash
npm install -g @railway/cli
```

### 2. Login to Railway
```bash
railway login
```

### 3. Initialize Project
```bash
railway init
```

### 4. Add PostgreSQL Database
```bash
# Add PostgreSQL service
railway add

# Select "PostgreSQL" from the list
# This will automatically set up all database environment variables
```

### 5. Set Environment Variables
```bash
railway variables set GOOGLE_API_KEY=your_google_api_key_here
```

### 6. Deploy
```bash
railway up
```

### 7. Get Your Public URL
```bash
railway domain
```

## 🎉 Done! 

Your app will be available at: `https://your-app-name.railway.app`

## 🗄️ Database Setup (Important!)

### Option A: Railway PostgreSQL (Recommended)
```bash
# Add PostgreSQL service
railway add

# Select "PostgreSQL" 
# Railway will automatically set these environment variables:
# - POSTGRES_HOST
# - POSTGRES_PORT  
# - POSTGRES_DB
# - POSTGRES_USER
# - POSTGRES_PASSWORD
```

### Option B: External Database
If using external PostgreSQL (like Supabase, Neon, etc.):
```bash
# Set database environment variables manually
railway variables set POSTGRES_HOST=your-db-host.com
railway variables set POSTGRES_PORT=5432
railway variables set POSTGRES_DB=your_database_name
railway variables set POSTGRES_USER=your_username
railway variables set POSTGRES_PASSWORD=your_password
```

### Option C: Demo Mode (No Database)
If you don't want to set up a database:
```bash
# The app will run in demo mode automatically
# No database environment variables needed
```

## 📋 What Railway Does Automatically:

- ✅ **Builds** your Docker container
- ✅ **Deploys** to their infrastructure  
- ✅ **Provides** HTTPS certificate
- ✅ **Scales** automatically
- ✅ **Monitors** your app health
- ✅ **Gives** you a public URL
- ✅ **Sets up** PostgreSQL environment variables (if you add PostgreSQL service)

## 🔧 Customization (Optional)

### Custom Domain
```bash
railway domain add yourdomain.com
```

### Environment Variables
```bash
# View all variables
railway variables

# Add more variables
railway variables set MY_VAR=value
```

### View Logs
```bash
railway logs
```

### Redeploy
```bash
railway up
```

## 💰 Pricing

- **Free Tier**: $5 credit/month (enough for small projects)
- **Paid**: Pay-as-you-use after free tier

## 🆘 Troubleshooting

### Database Connection Issues
```bash
# Check if PostgreSQL service is added
railway service

# Check database environment variables
railway variables | grep POSTGRES

# If no PostgreSQL variables, add the service:
railway add
# Select "PostgreSQL" from the list
```

### Build Fails
```bash
# Check logs
railway logs

# Rebuild
railway up --force
```

### App Not Starting
```bash
# Check environment variables
railway variables

# Check logs for database errors
railway logs

# Restart app
railway service restart
```

### Domain Issues
```bash
# Check domain status
railway domain

# Add custom domain
railway domain add yourdomain.com
```

## 🔄 Continuous Deployment

### GitHub Integration
1. Push your code to GitHub
2. Connect Railway to your GitHub repo
3. Automatic deployments on every push!

### Manual Deployment
```bash
# Deploy from current directory
railway up

# Deploy specific branch
railway up --branch main
```

## 📊 Monitoring

### View App Status
```bash
railway status
```

### View Metrics
- Go to Railway dashboard
- Check CPU, memory, and network usage

### Set Up Alerts
- Configure notifications in Railway dashboard
- Get alerts for downtime or errors

## 🚀 Production Tips

### 1. Use Production Profile
```bash
# Deploy with nginx (production mode)
railway up --profile production
```

### 2. Set Resource Limits
```bash
# In Railway dashboard, set:
# - Memory: 512MB
# - CPU: 0.5 cores
```

### 3. Enable Auto-scaling
- Railway automatically scales based on traffic
- No manual configuration needed

## 🎯 Alternative: Render.com

If Railway doesn't work for you:

### 1. Create render.yaml
```yaml
services:
  - type: web
    name: resume-processor
    env: docker
    dockerfilePath: ./Dockerfile
    envVars:
      - key: GOOGLE_API_KEY
        value: your_key_here
```

### 2. Deploy
- Connect GitHub repo to Render
- Automatic deployment on push

### 3. Get URL
- Render provides: `https://your-app.onrender.com`

## 🏆 Success Checklist

- [ ] App builds successfully
- [ ] Environment variables set
- [ ] App starts without errors
- [ ] Public URL accessible
- [ ] HTTPS working
- [ ] Can upload and process resumes

## 🆘 Need Help?

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **GitHub Issues**: Create issue in your repo

---

**Your resume processor will be live in minutes! 🎉** 

## 🔍 **Step 1: Get Database Connection Details**

Go to your Railway dashboard and find your PostgreSQL database. You should see connection details like:

- **Host**: `postgres-db.up.railway.app`
- **Port**: Usually `5432`
- **Database name**: Something like `railway` or custom name
- **Username**: Usually `postgres`
- **Password**: Generated password

## 🔧 **Step 2: Set Environment Variables**

You can set these in Railway dashboard or use the CLI. Let me help you with both methods:

### **Method A: Railway Dashboard (Easiest)**
1. Go to your Railway project dashboard
2. Click on your **web app service** (not the database)
3. Go to **Variables** tab
4. Add these environment variables:

```
<code_block_to_apply_changes_from>
```

### **Method B: Railway CLI (If you get it working)**
```bash
# Try this to see if npx works
npx @railway/cli login

# Then set variables
npx @railway/cli variables set POSTGRES_HOST=postgres-db.up.railway.app
npx @railway/cli variables set POSTGRES_PORT=5432
npx @railway/cli variables set POSTGRES_DB=railway
npx @railway/cli variables set POSTGRES_USER=postgres
npx @railway/cli variables set POSTGRES_PASSWORD=your_password
npx @railway/cli variables set GOOGLE_API_KEY=your_google_api_key
```

## 🎯 **Step 3: Test Connection**

Let me create a simple test script to verify your database connection:

```bash
POSTGRES_HOST=postgres-db.up.railway.app
POSTGRES_PORT=5432
POSTGRES_DB=railway
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_generated_password
GOOGLE_API_KEY=your_google_api_key
``` 
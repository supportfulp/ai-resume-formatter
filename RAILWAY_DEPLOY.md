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

### 4. Set Environment Variables
```bash
railway variables set GOOGLE_API_KEY=your_google_api_key_here
```

### 5. Deploy
```bash
railway up
```

### 6. Get Your Public URL
```bash
railway domain
```

## 🎉 Done! 

Your app will be available at: `https://your-app-name.railway.app`

## 📋 What Railway Does Automatically:

- ✅ **Builds** your Docker container
- ✅ **Deploys** to their infrastructure  
- ✅ **Provides** HTTPS certificate
- ✅ **Scales** automatically
- ✅ **Monitors** your app health
- ✅ **Gives** you a public URL

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
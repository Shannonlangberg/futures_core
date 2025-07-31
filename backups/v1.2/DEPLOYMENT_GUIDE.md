# 🚀 Futures Core - Deployment Guide

## 🔒 Security First Approach

### Step 1: Prepare Your Environment Variables

Create a `.env` file (NEVER commit this to Git):

```bash
# Flask Configuration
SECRET_KEY=your-super-secret-key-here-change-this
FLASK_ENV=production

# API Keys (Keep these secure!)
ANTHROPIC_API_KEY=your-anthropic-api-key
GOOGLE_SHEETS_CREDENTIALS={"type": "service_account", ...}

# Security Settings
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
LOG_LEVEL=INFO
```

### Step 2: Choose Your Hosting Platform

#### Option A: Railway (Recommended for Quick Demo)

1. **Sign up at [Railway.app](https://railway.app)**
2. **Connect your GitHub repository**
3. **Set environment variables in Railway dashboard**
4. **Deploy automatically**

#### Option B: Render

1. **Sign up at [Render.com](https://render.com)**
2. **Create new Web Service**
3. **Connect your GitHub repository**
4. **Set environment variables**
5. **Deploy**

#### Option C: Heroku

1. **Install Heroku CLI**
2. **Create new app: `heroku create your-app-name`**
3. **Set environment variables:**
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set ANTHROPIC_API_KEY=your-api-key
   heroku config:set GOOGLE_SHEETS_CREDENTIALS='{"type": "service_account", ...}'
   ```
4. **Deploy: `git push heroku main`**

### Step 3: Security Checklist

✅ **Environment Variables**: All sensitive data in env vars  
✅ **HTTPS**: Platform provides automatic SSL  
✅ **CORS**: Configured for your domain only  
✅ **Security Headers**: Added to all responses  
✅ **Rate Limiting**: Implemented  
✅ **Logging**: Request logging enabled  
✅ **Error Handling**: Proper error responses  

### Step 4: API Key Security

#### Anthropic API Key
1. **Get your API key from [Anthropic Console](https://console.anthropic.com)**
2. **Set as environment variable: `ANTHROPIC_API_KEY`**
3. **Never expose in code or logs**

#### Google Sheets Credentials
1. **Create service account in Google Cloud Console**
2. **Download JSON credentials**
3. **Set as environment variable: `GOOGLE_SHEETS_CREDENTIALS`**
4. **Share your Google Sheet with the service account email**

### Step 5: Domain and SSL

- **Custom Domain**: Configure in your hosting platform
- **SSL Certificate**: Automatic with most platforms
- **HTTPS Only**: Redirect all HTTP to HTTPS

### Step 6: Monitoring and Logs

- **Health Check**: `/health` endpoint for monitoring
- **Request Logging**: All requests logged
- **Error Tracking**: 500 errors logged
- **Performance**: Monitor response times

### Step 7: Testing Your Deployment

1. **Health Check**: Visit `https://yourdomain.com/health`
2. **Main Dashboard**: Test voice functionality
3. **Navigation**: Test all three pages
4. **Mobile**: Test on phone/tablet
5. **Security**: Check headers with browser dev tools

### Step 8: Demo Preparation

#### For Live Demos:
1. **Prepare test data** in your Google Sheet
2. **Test voice recognition** on demo device
3. **Have backup plan** if voice fails
4. **Prepare script** for demo flow

#### Demo Script:
```
1. "Show me the weekend review for South campus"
2. "What's the attendance at Paradise campus?"
3. "Give me a cross-campus comparison"
4. Navigate to Heartbeat Monitor
5. Navigate to Spiritual Journey
```

### Security Best Practices

🔒 **Never commit API keys to Git**  
🔒 **Use environment variables for all secrets**  
🔒 **Enable HTTPS only**  
🔒 **Set up proper CORS origins**  
🔒 **Monitor logs for suspicious activity**  
🔒 **Regular security updates**  
🔒 **Backup your data regularly**  

### Troubleshooting

**Common Issues:**
- **API Key Errors**: Check environment variables
- **CORS Errors**: Verify CORS_ORIGINS setting
- **Google Sheets Access**: Ensure service account has permissions
- **Voice Recognition**: Test microphone permissions

**Support:**
- Check platform logs for errors
- Verify all environment variables are set
- Test locally before deploying

### Cost Estimation

**Free Tiers Available:**
- Railway: $5/month after free tier
- Render: Free tier available
- Heroku: $7/month basic dyno
- DigitalOcean: $5/month droplet

**Recommended for Demo:**
- Railway or Render (easiest setup)
- Heroku (most reliable)
- DigitalOcean (most control)

---

## 🎯 Quick Start (Railway)

1. **Fork this repository to your GitHub**
2. **Sign up at Railway.app**
3. **Connect your GitHub repo**
4. **Add environment variables in Railway dashboard**
5. **Deploy automatically**
6. **Get your live URL**
7. **Test and demo!**

Your app will be live at: `https://your-app-name.railway.app` 
# 🚀 Church Voice Assistant

A modern, AI-powered voice assistant for church statistics and data management. Built with React, Flask, and Three.js for an immersive user experience.

## ✨ Features

- **🎤 Voice Recognition**: Natural language processing for church statistics
- **📊 Data Visualization**: Interactive dashboards and reports
- **🎨 Particle Effects**: Beautiful Three.js particle animations
- **🔐 User Management**: Role-based access control
- **📱 Responsive Design**: Works on desktop, tablet, and mobile
- **🔒 Secure**: Environment-based configuration and API key management

## 🛠️ Tech Stack

### Frontend
- **React 18** with Vite
- **Three.js** for 3D particle effects
- **Tailwind CSS** for styling
- **React Router** for navigation

### Backend
- **Flask** with Python 3.11
- **Anthropic Claude** for AI processing
- **Google Sheets API** for data storage
- **Flask-Login** for authentication
- **Gunicorn** for production deployment

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Git

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd church-voice-assistant
```

### 2. Set Up Environment Variables
Create a `.env` file in the root directory:
```bash
# Flask Configuration
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=development

# API Keys (Get these from the respective services)
ANTHROPIC_API_KEY=your-anthropic-api-key
GOOGLE_SHEETS_CREDENTIALS={"type": "service_account", ...}

# Security Settings
CORS_ORIGINS=http://localhost:3000,http://localhost:5002
LOG_LEVEL=INFO
```

### 3. Build and Run Locally

#### Option A: Automated Setup (Recommended)
```bash
# Build everything and set up local development
./build.sh

# Start local development
./deploy.sh local
```

#### Option B: Manual Setup
```bash
# Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py

# Frontend Setup (in a new terminal)
cd frontend
npm install
npm run dev
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5002

## 🌐 Deployment

### Automated Deployment

The project includes automated deployment scripts for multiple platforms:

```bash
# Show deployment options
./deploy.sh help

# Deploy to Railway (easiest)
./deploy.sh railway

# Deploy to Render
./deploy.sh render

# Deploy to Heroku
./deploy.sh heroku

# Deploy to DigitalOcean App Platform
./deploy.sh digitalocean
```

### Manual Deployment

#### Railway (Recommended for Quick Demo)
1. Sign up at [Railway.app](https://railway.app)
2. Connect your GitHub repository
3. Set environment variables in Railway dashboard
4. Deploy automatically

#### Render
1. Go to [Render.com](https://render.com)
2. Create new Web Service
3. Connect your GitHub repository
4. Set build command: `./build.sh`
5. Set start command: `gunicorn backend.app_deploy:app --bind 0.0.0.0:$PORT`
6. Add environment variables
7. Deploy!

### Environment Variables for Production

Set these in your hosting platform's dashboard:

**Required:**
- `SECRET_KEY`: Your Flask secret key
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `GOOGLE_SHEETS_CREDENTIALS`: Your Google service account JSON
- `CORS_ORIGINS`: Your domain URLs (comma-separated)

**Optional:**
- `FLASK_ENV`: production
- `LOG_LEVEL`: INFO
- `PORT`: 5002

## 🔧 Development Workflow

### Local Development
```bash
# Terminal 1: Backend
cd backend
python app.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Making Changes
1. Make your changes in the code
2. Test locally using the development setup
3. Build the project: `./build.sh`
4. Deploy: `./deploy.sh [platform]`

### Project Structure
```
church-voice-assistant/
├── backend/                 # Flask backend
│   ├── app.py              # Main Flask application
│   ├── app_deploy.py       # Production deployment entry
│   └── static/             # Built frontend files
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/         # Page components
│   │   └── App.jsx        # Main app component
│   └── package.json
├── build.sh               # Build script
├── deploy.sh              # Deployment script
├── requirements.txt       # Python dependencies
└── Procfile              # Heroku deployment config
```

## 🔑 API Keys Setup

### Anthropic API Key
1. Sign up at [Anthropic Console](https://console.anthropic.com)
2. Create an API key
3. Add to environment variables as `ANTHROPIC_API_KEY`

### Google Sheets Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable Google Sheets API
4. Create a service account
5. Download the JSON credentials
6. Add to environment variables as `GOOGLE_SHEETS_CREDENTIALS`
7. Share your Google Sheet with the service account email

## 🎯 Features Overview

### Voice Assistant
- Natural language processing for church statistics
- Voice-to-text conversion
- AI-powered insights and reports

### Dashboard
- Real-time statistics visualization
- Campus comparison tools
- Interactive charts and graphs

### User Management
- Role-based access control
- Multi-campus support
- Secure authentication

### Particle Effects
- Interactive Three.js animations
- Responsive to user interactions
- Beautiful visual feedback

## 🐛 Troubleshooting

### Common Issues

**Build Errors:**
```bash
# Clean and rebuild
rm -rf frontend/node_modules
rm -rf frontend/dist
cd frontend && npm install
cd .. && ./build.sh
```

**API Key Errors:**
- Check environment variables are set correctly
- Verify API keys are valid and have proper permissions

**CORS Errors:**
- Ensure CORS_ORIGINS includes your domain
- Check that frontend and backend URLs match

**Voice Recognition Issues:**
- Test microphone permissions in browser
- Check HTTPS requirement for voice features

### Support
- Check platform logs for detailed error messages
- Verify all environment variables are set
- Test locally before deploying

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Happy Coding! 🚀** 
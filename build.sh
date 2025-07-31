#!/bin/bash

# Church Voice Assistant - Build Script
# This script builds both frontend and backend for deployment

echo "🚀 Starting Church Voice Assistant Build Process..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[BUILD]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "backend/app.py" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_status "Building Frontend..."

# Navigate to frontend directory and build
cd frontend

# Check if node_modules exists, if not install dependencies
if [ ! -d "node_modules" ]; then
    print_status "Installing frontend dependencies..."
    npm install
fi

# Build the frontend
print_status "Building React app..."
npm run build

if [ $? -eq 0 ]; then
    print_status "Frontend build successful!"
else
    print_error "Frontend build failed!"
    exit 1
fi

# Copy built frontend to backend static directory
print_status "Copying frontend build to backend..."
cd ..
rm -rf backend/static/*
cp -r frontend/dist/* backend/static/

print_status "Backend preparation..."

# Create necessary directories
mkdir -p backend/temp_audio
mkdir -p backend/data

# Set up environment file if it doesn't exist
if [ ! -f ".env" ]; then
    print_warning "No .env file found. Creating template..."
    cat > .env << EOF
# Flask Configuration
SECRET_KEY=your-super-secret-key-here-change-this
FLASK_ENV=production

# API Keys (Keep these secure!)
ANTHROPIC_API_KEY=your-anthropic-api-key
GOOGLE_SHEETS_CREDENTIALS={"type": "service_account", ...}

# Security Settings
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
LOG_LEVEL=INFO
EOF
    print_warning "Please update .env file with your actual API keys and settings"
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment and install dependencies
print_status "Installing backend dependencies..."
source .venv/bin/activate
pip install -r requirements.txt

print_status "Build process completed successfully! 🎉"
print_status "Your app is ready for deployment."
print_status ""
print_status "Next steps:"
print_status "1. Update .env file with your API keys"
print_status "2. Deploy to your chosen platform (Railway, Render, Heroku, etc.)"
print_status "3. Set environment variables in your hosting platform"
print_status ""
print_status "For local development:"
print_status "- Backend: cd backend && python app.py"
print_status "- Frontend: cd frontend && npm run dev" 
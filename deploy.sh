#!/bin/bash

# Church Voice Assistant - Deployment Script
# This script handles deployment to various platforms

echo "🚀 Church Voice Assistant - Deployment Script"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[DEPLOY]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "backend/app.py" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Function to build the project
build_project() {
    print_status "Building project..."
    ./build.sh
    if [ $? -eq 0 ]; then
        print_status "Build completed successfully!"
    else
        print_error "Build failed!"
        exit 1
    fi
}

# Function to deploy to Railway
deploy_railway() {
    print_info "Deploying to Railway..."
    
    # Check if Railway CLI is installed
    if ! command -v railway &> /dev/null; then
        print_warning "Railway CLI not found. Installing..."
        npm install -g @railway/cli
    fi
    
    # Build the project
    build_project
    
    # Deploy to Railway
    print_status "Deploying to Railway..."
    railway up
    
    print_status "Railway deployment completed!"
    print_info "Your app should be live at: https://your-app-name.railway.app"
}

# Function to deploy to Render
deploy_render() {
    print_info "Deploying to Render..."
    
    # Build the project
    build_project
    
    print_status "Render deployment setup:"
    print_info "1. Go to https://render.com"
    print_info "2. Create a new Web Service"
    print_info "3. Connect your GitHub repository"
    print_info "4. Set build command: ./build.sh"
    print_info "5. Set start command: gunicorn backend.app_deploy:app --bind 0.0.0.0:$PORT"
    print_info "6. Add environment variables in Render dashboard"
    print_info "7. Deploy!"
}

# Function to deploy to Heroku
deploy_heroku() {
    print_info "Deploying to Heroku..."
    
    # Check if Heroku CLI is installed
    if ! command -v heroku &> /dev/null; then
        print_warning "Heroku CLI not found. Please install from: https://devcenter.heroku.com/articles/heroku-cli"
        exit 1
    fi
    
    # Build the project
    build_project
    
    # Check if Heroku app exists
    if ! heroku apps:info &> /dev/null; then
        print_status "Creating new Heroku app..."
        heroku create
    fi
    
    # Deploy to Heroku
    print_status "Deploying to Heroku..."
    git add .
    git commit -m "Deploy to Heroku"
    git push heroku main
    
    print_status "Heroku deployment completed!"
    print_info "Your app should be live at: https://your-app-name.herokuapp.com"
}

# Function to deploy to DigitalOcean App Platform
deploy_digitalocean() {
    print_info "Deploying to DigitalOcean App Platform..."
    
    # Build the project
    build_project
    
    print_status "DigitalOcean App Platform deployment setup:"
    print_info "1. Go to https://cloud.digitalocean.com/apps"
    print_info "2. Create a new app"
    print_info "3. Connect your GitHub repository"
    print_info "4. Set build command: ./build.sh"
    print_info "5. Set run command: gunicorn backend.app_deploy:app --bind 0.0.0.0:$PORT"
    print_info "6. Add environment variables in DigitalOcean dashboard"
    print_info "7. Deploy!"
}

# Function to show environment variables setup
setup_env() {
    print_info "Environment Variables Setup:"
    echo ""
    echo "Required Environment Variables:"
    echo "================================"
    echo "SECRET_KEY=your-super-secret-key-here"
    echo "ANTHROPIC_API_KEY=your-anthropic-api-key"
    echo "GOOGLE_SHEETS_CREDENTIALS={\"type\": \"service_account\", ...}"
    echo "CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com"
    echo ""
    echo "Optional Environment Variables:"
    echo "==============================="
    echo "FLASK_ENV=production"
    echo "LOG_LEVEL=INFO"
    echo "PORT=5002"
    echo ""
    print_warning "Make sure to set these in your hosting platform's dashboard!"
}

# Function to show local development setup
local_dev() {
    print_info "Local Development Setup:"
    echo ""
    echo "1. Backend (Terminal 1):"
    echo "   cd backend"
    echo "   python app.py"
    echo ""
    echo "2. Frontend (Terminal 2):"
    echo "   cd frontend"
    echo "   npm run dev"
    echo ""
    echo "3. Access the app:"
    echo "   Backend: http://localhost:5002"
    echo "   Frontend: http://localhost:3000"
    echo ""
    print_warning "Make sure to set up your .env file with API keys!"
}

# Main script logic
case "${1:-help}" in
    "railway")
        deploy_railway
        ;;
    "render")
        deploy_render
        ;;
    "heroku")
        deploy_heroku
        ;;
    "digitalocean")
        deploy_digitalocean
        ;;
    "build")
        build_project
        ;;
    "env")
        setup_env
        ;;
    "local")
        local_dev
        ;;
    "help"|*)
        echo ""
        echo "🚀 Church Voice Assistant - Deployment Script"
        echo "============================================="
        echo ""
        echo "Usage: ./deploy.sh [command]"
        echo ""
        echo "Commands:"
        echo "  railway      - Deploy to Railway"
        echo "  render       - Deploy to Render"
        echo "  heroku       - Deploy to Heroku"
        echo "  digitalocean - Deploy to DigitalOcean App Platform"
        echo "  build        - Build the project only"
        echo "  env          - Show environment variables setup"
        echo "  local        - Show local development setup"
        echo "  help         - Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./deploy.sh railway"
        echo "  ./deploy.sh render"
        echo "  ./deploy.sh env"
        echo ""
        print_warning "Make sure to set up your environment variables before deploying!"
        ;;
esac 
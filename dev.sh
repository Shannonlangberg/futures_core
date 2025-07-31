#!/bin/bash

# Church Voice Assistant - Development Script
# This script starts both frontend and backend for local development

echo "🚀 Starting Church Voice Assistant Development Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[DEV]${NC} $1"
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

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
print_status "Checking prerequisites..."

if ! command_exists python3; then
    print_error "Python 3 is not installed. Please install Python 3.11+"
    exit 1
fi

if ! command_exists node; then
    print_error "Node.js is not installed. Please install Node.js 18+"
    exit 1
fi

if ! command_exists npm; then
    print_error "npm is not installed. Please install npm"
    exit 1
fi

print_status "Prerequisites check passed!"

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning "No .env file found. Creating template..."
    cat > .env << EOF
# Flask Configuration
SECRET_KEY=dev-secret-key-change-in-production
FLASK_ENV=development

# API Keys (Get these from the respective services)
ANTHROPIC_API_KEY=your-anthropic-api-key
GOOGLE_SHEETS_CREDENTIALS={"type": "service_account", ...}

# Security Settings
CORS_ORIGINS=http://localhost:3000,http://localhost:5002
LOG_LEVEL=INFO
EOF
    print_warning "Please update .env file with your actual API keys"
fi

# Function to start backend
start_backend() {
    print_status "Starting backend server..."
    cd backend
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies if needed
    if [ ! -f "venv/lib/python*/site-packages/flask" ]; then
        print_status "Installing Python dependencies..."
        pip install -r ../requirements.txt
    fi
    
    # Start the backend server
    print_status "Backend starting on http://localhost:5002"
    python app.py
}

# Function to start frontend
start_frontend() {
    print_status "Starting frontend development server..."
    cd frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
    fi
    
    # Start the frontend development server
    print_status "Frontend starting on http://localhost:3000"
    npm run dev
}

# Function to show usage
show_usage() {
    echo ""
    echo "🚀 Church Voice Assistant - Development Script"
    echo "============================================="
    echo ""
    echo "Usage: ./dev.sh [command]"
    echo ""
    echo "Commands:"
    echo "  backend   - Start only the backend server"
    echo "  frontend  - Start only the frontend server"
    echo "  both      - Start both backend and frontend (default)"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./dev.sh both"
    echo "  ./dev.sh backend"
    echo "  ./dev.sh frontend"
    echo ""
    print_info "Access the app at:"
    print_info "- Frontend: http://localhost:3000"
    print_info "- Backend API: http://localhost:5002"
    echo ""
}

# Main script logic
case "${1:-both}" in
    "backend")
        start_backend
        ;;
    "frontend")
        start_frontend
        ;;
    "both")
        print_status "Starting both backend and frontend..."
        print_info "You'll need two terminal windows."
        print_info "In the first terminal, run: ./dev.sh backend"
        print_info "In the second terminal, run: ./dev.sh frontend"
        echo ""
        print_status "Starting backend in this terminal..."
        start_backend
        ;;
    "help"|*)
        show_usage
        ;;
esac 
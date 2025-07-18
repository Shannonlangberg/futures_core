#!/bin/bash

# 🔥 Futures Core - Setup Script
# This script automates the setup process for the voice assistant

set -e  # Exit on any error

echo "🔥 Setting up Futures Core Voice Assistant..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 is not installed. Please install Python 3.8+ first."
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    print_status "Creating virtual environment..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source venv/bin/activate
    print_success "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r backend/requirements.txt
    print_success "Dependencies installed"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p backend/data
    mkdir -p backend/logs
    mkdir -p backend/temp_audio
    print_success "Directories created"
}

# Check for required files
check_credentials() {
    print_status "Checking for required credentials..."
    
    if [ ! -f "backend/credentials.json" ]; then
        print_warning "credentials.json not found in backend directory"
        echo "Please download your Google Service Account credentials and save as 'backend/credentials.json'"
        echo "Instructions:"
        echo "1. Go to Google Cloud Console"
        echo "2. Create a service account"
        echo "3. Download the JSON key file"
        echo "4. Rename it to 'credentials.json' and place in the backend directory"
    else
        print_success "credentials.json found"
    fi
    
    if [ ! -f "backend/.env" ]; then
        print_warning ".env file not found"
        echo "Please create a .env file in the backend directory with your API keys:"
        echo "ANTHROPIC_API_KEY=your_anthropic_api_key_here"
        echo "GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json"
    else
        print_success ".env file found"
    fi
}

# Test the installation
test_installation() {
    print_status "Testing installation..."
    
    # Check if we can import the required modules
    python3 -c "
import sys
sys.path.append('backend')
try:
    import flask
    import anthropic
    import gspread
    print('✅ All required modules can be imported')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        print_success "Installation test passed"
    else
        print_error "Installation test failed"
        exit 1
    fi
}

# Display next steps
show_next_steps() {
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Ensure you have the required credentials:"
    echo "   - backend/credentials.json (Google Service Account)"
    echo "   - backend/.env (API keys)"
    echo ""
    echo "2. Start the application:"
    echo "   cd backend"
    echo "   python app.py"
    echo ""
    echo "3. Open your browser to:"
    echo "   http://localhost:5001"
    echo ""
    echo "4. Test the voice assistant by clicking the microphone button"
    echo ""
    echo "For more information, see README.md"
}

# Main setup process
main() {
    echo "🔥 Futures Core Voice Assistant Setup"
    echo "====================================="
    echo ""
    
    check_python
    create_venv
    activate_venv
    install_dependencies
    create_directories
    check_credentials
    test_installation
    show_next_steps
}

# Run the setup
main "$@" 
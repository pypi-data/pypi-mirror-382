#!/bin/bash

# LZaaS CLI Installation Script
# Version: 1.0.0
# Date: February 10, 2025

set -e  # Exit on any error

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main installation function
main() {
    echo ""
    echo "🚀 LZaaS CLI Installation"
    echo "========================"
    echo ""

    # Check prerequisites
    print_status "Checking prerequisites..."

    if ! command_exists python3; then
        print_error "Python 3 is required but not installed"
        print_status "Please install Python 3.8 or higher and try again"
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION found"

    if ! command_exists pip3; then
        print_error "pip3 is required but not installed"
        print_status "Please install pip3 and try again"
        exit 1
    fi

    print_success "pip3 found"

    # Check if we're in the correct directory (lzaas-cli root)
    if [ ! -f "setup.py" ] || [ ! -d "lzaas" ]; then
        print_error "setup.py or lzaas directory not found"
        print_status "Please run this script from the lzaas-cli root directory"
        exit 1
    fi

    # Check if virtual environment already exists
    if [ -d "lzaas-env" ]; then
        print_warning "Virtual environment 'lzaas-env' already exists"
        read -p "Do you want to remove it and create a fresh one? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Removing existing virtual environment..."
            rm -rf lzaas-env
        else
            print_status "Using existing virtual environment..."
        fi
    fi

    # Create virtual environment if it doesn't exist
    if [ ! -d "lzaas-env" ]; then
        print_status "Creating virtual environment 'lzaas-env'..."
        python3 -m venv lzaas-env
        print_success "Virtual environment created"
    fi

    # Activate virtual environment
    print_status "Activating virtual environment..."
    source lzaas-env/bin/activate

    # Verify activation
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        print_success "Virtual environment activated: $VIRTUAL_ENV"
    else
        print_error "Failed to activate virtual environment"
        exit 1
    fi

    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip --quiet

    # Install LZaaS CLI in development mode
    print_status "Installing LZaaS CLI in development mode..."
    pip install -e . --quiet

    # Verify installation
    print_status "Verifying installation..."

    if command_exists lzaas; then
        print_success "LZaaS CLI installed successfully!"

        # Show version and basic info
        echo ""
        echo "📋 Installation Summary"
        echo "======================"
        echo "• Virtual Environment: $(pwd)/lzaas-env"
        echo "• Python Version: $(python --version)"
        echo "• LZaaS CLI Version: $(lzaas --version 2>/dev/null || echo "1.0.0")"
        echo ""

        # Test basic functionality
        print_status "Testing basic functionality..."
        lzaas --help > /dev/null 2>&1
        print_success "Basic functionality test passed"

    else
        print_error "LZaaS CLI installation failed"
        exit 1
    fi

    # Check AWS CLI (optional)
    if command_exists aws; then
        print_success "AWS CLI found - ready for LZaaS operations"

        # Check if AWS is configured
        if aws sts get-caller-identity > /dev/null 2>&1; then
            print_success "AWS credentials configured"
        else
            print_warning "AWS credentials not configured"
            print_status "Run 'aws configure' to set up AWS credentials"
        fi
    else
        print_warning "AWS CLI not found"
        print_status "Install AWS CLI for full LZaaS functionality"
    fi

    # Show usage instructions
    echo ""
    echo "🎉 Installation Complete!"
    echo "========================"
    echo ""
    echo "📖 Quick Start:"
    echo "1. Activate environment: source lzaas-env/bin/activate"
    echo "2. Configure AWS:        aws configure"
    echo "3. Test LZaaS:          lzaas --help"
    echo "4. List templates:      lzaas template list"
    echo "5. List accounts:       lzaas account list"
    echo ""
    echo "📚 Documentation:"
    echo "• User Guide:          docs/USER_GUIDE.md"
    echo "• Quick Reference:     docs/QUICK_REFERENCE.md"
    echo "• Online Docs:         https://spitzkop.github.io/lzaas-cli/"
    echo ""
    echo "🔧 Daily Usage:"
    echo "• Start session:       source lzaas-env/bin/activate"
    echo "• End session:         deactivate"
    echo ""

    # Deactivate virtual environment
    deactivate

    print_success "Installation script completed successfully!"
    echo ""
}

# Run main function
main "$@"

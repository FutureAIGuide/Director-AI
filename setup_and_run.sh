#!/bin/bash

# URL Screenshot Processor Setup Script
# Usage: ./setup_and_run.sh [options]
# Options:
#   --clean     Remove existing virtual environment before setup
#   --verbose   Show detailed output
#   --help      Show this help message

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VENV_DIR="venv"
REQUIREMENTS_FILE="requirements.txt"
MAIN_SCRIPT="url_screenshot_processor.py"
VERBOSE=false
CLEAN=false

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

show_help() {
    cat << EOF
URL Screenshot Processor Setup Script

Usage: $0 [options]

Options:
    --clean     Remove existing virtual environment before setup
    --verbose   Show detailed output
    --help      Show this help message

This script will:
1. Create a Python virtual environment
2. Install required dependencies
3. Install Playwright browsers
4. Set up the main script

Prerequisites:
- Python 3.7 or higher
- pip package manager
EOF
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Python 3
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed or not in PATH"
        log_error "Please install Python 3.7 or higher"
        log_error "On macOS: brew install python3"
        exit 1
    fi
    
    # Check Python version
    local python_version
    if ! python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null); then
        log_error "Failed to get Python version"
        exit 1
    fi
    
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 7) else 1)" 2>/dev/null; then
        log_error "Python version $python_version is too old. Required: 3.7 or higher"
        log_error "Please upgrade Python: brew upgrade python3"
        exit 1
    fi
    
    log_success "Python $python_version found"
    
    # Check pip
    if ! python3 -m pip --version &> /dev/null; then
        log_error "pip is not available"
        log_error "Please install pip or ensure it's properly configured"
        log_error "Try: python3 -m ensurepip --upgrade"
        exit 1
    fi
    
    # Check requirements file
    if [[ ! -f "$REQUIREMENTS_FILE" ]]; then
        log_error "Requirements file '$REQUIREMENTS_FILE' not found"
        log_error "Please ensure the requirements.txt file exists in the current directory"
        exit 1
    fi
    
    # Check main script
    if [[ ! -f "$MAIN_SCRIPT" ]]; then
        log_warning "Main script '$MAIN_SCRIPT' not found"
        log_warning "Make sure it exists before running the processor"
    fi
}

cleanup_venv() {
    if [[ -d "$VENV_DIR" ]]; then
        log_info "Removing existing virtual environment..."
        rm -rf "$VENV_DIR"
        log_success "Virtual environment removed"
    fi
}

create_venv() {
    log_info "Creating virtual environment..."
    
    if python3 -m venv "$VENV_DIR"; then
        log_success "Virtual environment created in '$VENV_DIR'"
    else
        log_error "Failed to create virtual environment"
        exit 1
    fi
}

activate_venv() {
    log_info "Activating virtual environment..."
    
    local activate_script="$VENV_DIR/bin/activate"
    
    if [[ ! -f "$activate_script" ]]; then
        log_error "Virtual environment activation script not found: $activate_script"
        log_error "Virtual environment may be corrupted. Try running with --clean"
        exit 1
    fi
    
    # shellcheck source=/dev/null
    if source "$activate_script"; then
        log_success "Virtual environment activated"
        
        # Verify we're in the virtual environment
        if [[ "$VIRTUAL_ENV" != *"$VENV_DIR"* ]]; then
            log_warning "Virtual environment activation may have failed"
            log_warning "VIRTUAL_ENV: $VIRTUAL_ENV"
        fi
    else
        log_error "Failed to activate virtual environment"
        log_error "Try running with --clean to recreate the environment"
        exit 1
    fi
}

install_dependencies() {
    log_info "Installing Python dependencies..."
    
    # Upgrade pip first to avoid version warnings
    if [[ "$VERBOSE" == true ]]; then
        log_info "Upgrading pip..."
        pip install --upgrade pip
    else
        pip install --quiet --upgrade pip || log_warning "Failed to upgrade pip, continuing with current version"
    fi
    
    # Install dependencies
    if [[ "$VERBOSE" == true ]]; then
        pip install -r "$REQUIREMENTS_FILE"
    else
        pip install --quiet -r "$REQUIREMENTS_FILE"
    fi
    
    if [[ $? -eq 0 ]]; then
        log_success "Dependencies installed successfully"
    else
        log_error "Failed to install dependencies"
        log_error "Check that all packages in $REQUIREMENTS_FILE are available"
        log_error "Try running with --verbose for more details"
        exit 1
    fi
}

install_playwright() {
    log_info "Installing Playwright browsers..."
    
    # Check if playwright command is available
    if ! command -v playwright &> /dev/null; then
        log_error "Playwright command not found"
        log_error "Make sure 'playwright' is included in your requirements.txt"
        log_error "Or install it manually: pip install playwright"
        exit 1
    fi
    
    # Install browsers with error handling
    if [[ "$VERBOSE" == true ]]; then
        playwright install chromium
    else
        playwright install chromium --quiet 2>/dev/null || playwright install chromium
    fi
    
    if [[ $? -eq 0 ]]; then
        log_success "Playwright browsers installed successfully"
    else
        log_error "Failed to install Playwright browsers"
        log_error "This might be due to network issues or insufficient disk space"
        log_error "Try running the command manually: playwright install chromium"
        exit 1
    fi
}

setup_script() {
    if [[ -f "$MAIN_SCRIPT" ]]; then
        log_info "Setting up main script permissions..."
        if chmod +x "$MAIN_SCRIPT"; then
            log_success "Script permissions set"
        else
            log_warning "Failed to set script permissions"
        fi
    fi
}

show_usage() {
    echo
    echo -e "${GREEN}Setup complete!${NC}"
    echo
    echo -e "${BLUE}Usage Instructions:${NC}"
    echo "1. Prepare your data:"
    echo "   - Create a spreadsheet with URLs in column A (CSV or Excel format)"
    echo
    echo "2. Run the processor:"
    echo "   - With your file: python $MAIN_SCRIPT your_spreadsheet.xlsx"
    echo "   - Create sample:  python $MAIN_SCRIPT --create-sample"
    echo
    echo "3. Output:"
    echo "   - Screenshots saved in 'screenshots' directory"
    echo "   - Processed data saved in '*_processed' file"
    echo
    echo -e "${BLUE}Virtual Environment:${NC}"
    echo "- To activate manually: source $VENV_DIR/bin/activate"
    echo "- To deactivate: deactivate"
    echo
    echo -e "${BLUE}Troubleshooting:${NC}"
    echo "- Run with --clean to reset virtual environment"
    echo "- Run with --verbose for detailed output"
    echo "- Check that input files have URLs in column A"
    echo
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --clean)
            CLEAN=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Main execution
main() {
    echo -e "${BLUE}=== URL Screenshot Processor Setup ===${NC}"
    echo
    
    # Check if already in a virtual environment
    if [[ -n "${VIRTUAL_ENV:-}" ]]; then
        log_warning "Already in a virtual environment: $VIRTUAL_ENV"
        log_warning "This might interfere with the setup process"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Setup cancelled. Deactivate current environment and try again."
            exit 0
        fi
    fi
    
    check_prerequisites
    
    if [[ "$CLEAN" == true ]]; then
        cleanup_venv
    fi
    
    if [[ ! -d "$VENV_DIR" ]]; then
        create_venv
    else
        log_info "Using existing virtual environment"
    fi
    
    activate_venv
    install_dependencies
    install_playwright
    setup_script
    
    show_usage
}

# Error handling and cleanup
cleanup_on_exit() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        echo
        log_error "Setup failed with exit code $exit_code"
        log_info "For troubleshooting:"
        log_info "- Run with --verbose for detailed output"
        log_info "- Run with --clean to reset virtual environment"
        log_info "- Check that all prerequisites are installed"
    fi
}

trap cleanup_on_exit EXIT

# Run main function with error handling
if ! main "$@"; then
    exit 1
fi

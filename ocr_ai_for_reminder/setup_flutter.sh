#!/bin/bash

# Flutter OCR AI Reminder App - Setup Script
# This script sets up the Flutter app for development

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Flutter OCR AI Reminder App - Setup Script                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}➜${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check Flutter installation
print_step "Checking Flutter installation..."
if ! command -v flutter &> /dev/null; then
    print_error "Flutter is not installed!"
    exit 1
fi

FLUTTER_VERSION=$(flutter --version | head -n 1)
print_success "Flutter found: $FLUTTER_VERSION"
echo ""

# Check Dart installation
print_step "Checking Dart installation..."
if ! command -v dart &> /dev/null; then
    print_error "Dart is not installed!"
    exit 1
fi

DART_VERSION=$(dart --version 2>&1 | grep -oP 'Dart \K[0-9.]+')
print_success "Dart found: $DART_VERSION"
echo ""

# Navigate to project directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
print_step "Project directory: $PROJECT_DIR"
cd "$PROJECT_DIR"
echo ""

# Clean previous builds
print_step "Cleaning previous builds..."
flutter clean
print_success "Clean complete"
echo ""

# Get dependencies
print_step "Getting dependencies..."
flutter pub get
print_success "Dependencies installed"
echo ""

# Generate model code
print_step "Generating model serialization code..."
if flutter pub run build_runner build --delete-conflicting-outputs; then
    print_success "Model code generated"
else
    print_warning "Model code generation had warnings (this is usually OK)"
fi
echo ""

# Verify project structure
print_step "Verifying project structure..."
REQUIRED_DIRS=(
    "lib/models"
    "lib/services"
    "lib/providers"
    "lib/ui/screens"
    "lib/widgets"
    "lib/utils"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        print_success "Found: $dir"
    else
        print_error "Missing: $dir"
        exit 1
    fi
done
echo ""

# Check key files
print_step "Checking key files..."
REQUIRED_FILES=(
    "pubspec.yaml"
    "lib/main.dart"
    "lib/models/medication.dart"
    "lib/services/api_client.dart"
    "lib/providers/processing_provider.dart"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "Found: $file"
    else
        print_error "Missing: $file"
        exit 1
    fi
done
echo ""

# Run Flutter doctor
print_step "Running Flutter doctor..."
echo ""
flutter doctor
echo ""

# Summary
print_step "Setup Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Show next steps
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo "1. Start backend services:"
echo "   - OCR Service:"
echo "     cd /home/rayu/DasTern/ocr-service-anti"
echo "     python -m venv venv"
echo "     source venv/bin/activate"
echo "     pip install -r requirements.txt"
echo "     python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "   - AI LLM Service:"
echo "     cd /home/rayu/DasTern/ai-llm-service"
echo "     python -m venv venv"
echo "     source venv/bin/activate"
echo "     pip install -r requirements.txt"
echo "     python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001"
echo ""
echo "2. Update API configuration (if needed):"
echo "   Edit: lib/utils/constants.dart"
echo "   Update: apiBaseUrl = 'http://your-server:8000'"
echo ""
echo "3. Run the app:"
echo "   flutter run"
echo ""
echo "4. For release build:"
echo "   flutter build apk --release  (Android)"
echo "   flutter build ios --release  (iOS)"
echo ""

print_success "Setup complete! Ready for development."
print_warning "Make sure backend services are running before launching the app."

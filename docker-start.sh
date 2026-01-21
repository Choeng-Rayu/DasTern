#!/bin/bash

#########################################
# DasTern Docker Startup Script
# Optimized for slow networks
#########################################

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Stop any running containers
print_header "Stopping existing containers..."
docker compose down 2>/dev/null || true

# Clean up old builds
print_info "Cleaning Docker system..."
docker system prune -f >/dev/null 2>&1 || true

# Start PostgreSQL
print_header "Starting PostgreSQL Database"
docker compose up -d postgres
sleep 3

# Check PostgreSQL health
for i in {1..30}; do
    if docker compose exec -T postgres pg_isready -U dastern &> /dev/null; then
        print_success "PostgreSQL is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        print_warning "PostgreSQL took longer to start, continuing anyway..."
    fi
    echo -n "."
    sleep 1
done

# Verify database
print_info "Verifying database schema..."
TABLES=$(docker compose exec -T postgres psql -U dastern -d dastern -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" 2>/dev/null | grep -oP '\d+' | head -1)
print_success "Database has $TABLES tables imported ✓"

# Build and start services
print_header "Building Services (This may take 15-25 minutes on first run)"

echo -e "${YELLOW}Building Backend (Next.js)...${NC}"
docker compose build backend

echo -e "${YELLOW}Building OCR Service (Python + Tesseract)...${NC}"
docker compose build ocr-service

echo -e "${YELLOW}Building AI Service (Python + PyTorch)...${NC}"
docker compose build ai-llm-service

# Start all services
print_header "Starting All Services"
docker compose up -d

# Wait for services to be ready
print_info "Waiting for services to start..."
sleep 10

# Check service status
print_header "Service Status"
docker compose ps

# Show access information
print_header "🎉 DasTern is Ready!"

echo "Services are available at:"
echo ""
echo -e "${GREEN}Database${NC}"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  User: dastern"
echo "  Password: dastern_secure_password_2026"
echo ""
echo -e "${GREEN}Backend (Next.js)${NC}"
echo "  URL: http://localhost:3000"
echo ""
echo -e "${GREEN}OCR Service${NC}"
echo "  URL: http://localhost:8000"
echo "  Docs: http://localhost:8000/docs"
echo ""
echo -e "${GREEN}AI Service${NC}"
echo "  URL: http://localhost:8001"
echo "  Docs: http://localhost:8001/docs"
echo ""

# Useful commands
print_header "Useful Commands"
echo -e "${BLUE}View all logs:${NC}"
echo "  docker compose logs -f"
echo ""
echo -e "${BLUE}View specific service logs:${NC}"
echo "  docker compose logs -f backend"
echo "  docker compose logs -f ocr-service"
echo "  docker compose logs -f ai-llm-service"
echo "  docker compose logs -f postgres"
echo ""
echo -e "${BLUE}Stop services:${NC}"
echo "  docker compose stop"
echo ""
echo -e "${BLUE}Restart services:${NC}"
echo "  docker compose restart"
echo ""
echo -e "${BLUE}Connect to database:${NC}"
echo "  docker compose exec postgres psql -U dastern -d dastern"
echo ""

print_success "Setup complete!"

#!/bin/bash

# DasTern - Complete Deployment and Test Script
# This script builds, deploys, and tests the entire system

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}🚀 DasTern Deployment and Test${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""

# Change to project directory
cd "$(dirname "$0")"

echo -e "${YELLOW}Step 1: Stopping existing containers...${NC}"
docker compose down 2>/dev/null || true

echo -e "${YELLOW}Step 2: Building services...${NC}"
echo "This may take several minutes for OCR and AI services..."
docker compose build --no-cache 2>&1 | grep -E "^\[|Step|Successfully|ERROR|DONE|Image" || docker compose build

echo ""
echo -e "${YELLOW}Step 3: Starting services...${NC}"
docker compose up -d

echo ""
echo -e "${YELLOW}Step 4: Waiting for services to be healthy...${NC}"
sleep 5

# Wait for postgres
echo "Waiting for PostgreSQL..."
for i in {1..30}; do
    if docker compose exec -T postgres pg_isready -U dastern > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PostgreSQL is ready${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

# Wait for backend
echo "Waiting for Backend..."
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is ready${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

echo ""
echo -e "${YELLOW}Step 5: Running tests...${NC}"
echo ""

# Test 1: PostgreSQL
echo -n "Test 1: PostgreSQL Connection... "
TABLE_COUNT=$(docker compose exec -T postgres psql -U dastern -d dastern -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';" 2>/dev/null | tr -d ' ')
if [ "$TABLE_COUNT" = "17" ]; then
    echo -e "${GREEN}✅ PASS${NC} ($TABLE_COUNT tables)"
else
    echo -e "${RED}❌ FAIL${NC} (found $TABLE_COUNT tables, expected 17)"
fi

# Test 2: Backend Health
echo -n "Test 2: Backend Service... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ PASS${NC} (HTTP $HTTP_CODE)"
else
    echo -e "${RED}❌ FAIL${NC} (HTTP $HTTP_CODE)"
fi

# Test 3: Database INSERT
echo -n "Test 3: Database CRUD Operations... "
TEST_UUID=$(docker compose exec -T postgres psql -U dastern -d dastern -t -c "
INSERT INTO prescriptions (patient_id, original_image_url, ocr_raw_text, status)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'test://image.jpg',
    'Test prescription text',
    'completed'
)
RETURNING id;" 2>/dev/null | tr -d ' \n')

if [ ! -z "$TEST_UUID" ]; then
    docker compose exec -T postgres psql -U dastern -d dastern -c "DELETE FROM prescriptions WHERE id = '$TEST_UUID';" > /dev/null 2>&1
    echo -e "${GREEN}✅ PASS${NC} (Created and deleted test record)"
else
    echo -e "${RED}❌ FAIL${NC} (Could not insert test record)"
fi

# Test 4: Check OCR service
echo -n "Test 4: OCR Service... "
if docker ps | grep -q "dastern.*ocr"; then
    OCR_STATUS=$(curl -s http://localhost:8000/health 2>/dev/null || echo "down")
    if echo "$OCR_STATUS" | grep -q "healthy\|ok"; then
        echo -e "${GREEN}✅ PASS${NC} (Running and healthy)"
    else
        echo -e "${YELLOW}⚠️  WARN${NC} (Container running but health check failed)"
    fi
else
    echo -e "${YELLOW}⚠️  WARN${NC} (Container not running - still building?)"
fi

# Test 5: Check AI service
echo -n "Test 5: AI Service... "
if docker ps | grep -q "dastern.*ai"; then
    AI_STATUS=$(curl -s http://localhost:8001/health 2>/dev/null || echo "down")
    if echo "$AI_STATUS" | grep -q "healthy\|ok"; then
        echo -e "${GREEN}✅ PASS${NC} (Running and healthy)"
    else
        echo -e "${YELLOW}⚠️  WARN${NC} (Container running but health check failed)"
    fi
else
    echo -e "${YELLOW}⚠️  WARN${NC} (Container not running - still building?)"
fi

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}📊 Deployment Summary${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "Services Status:"
docker compose ps
echo ""
echo "Access Points:"
echo -e "  🌐 Frontend:  ${GREEN}http://localhost:3000${NC}"
echo -e "  🔬 OCR API:   ${GREEN}http://localhost:8000${NC}"
echo -e "  🤖 AI API:    ${GREEN}http://localhost:8001${NC}"
echo -e "  🗄️  Database:  ${GREEN}localhost:5432${NC}"
echo ""
echo "Useful Commands:"
echo "  View logs:    docker compose logs -f"
echo "  Stop all:     docker compose down"
echo "  Restart:      docker compose restart"
echo "  Test system:  ./test-system.sh"
echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""

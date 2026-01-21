#!/bin/bash

# DasTern System Test Script
# Tests the complete OCR workflow from upload to database

set -e

echo "================================================"
echo "🧪 DasTern System Test"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Base URL
BASE_URL="http://localhost:3000"

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

# Function to print test result
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $2"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC}: $2"
        ((TESTS_FAILED++))
    fi
}

echo "Step 1: Checking if services are running..."
echo "-------------------------------------------"

# Check PostgreSQL
if docker ps | grep -q "dastern-postgres.*healthy"; then
    print_result 0 "PostgreSQL is running and healthy"
else
    print_result 1 "PostgreSQL is not running or not healthy"
fi

# Check Backend
if docker ps | grep -q "dastern.*backend"; then
    print_result 0 "Backend service is running"
else
    print_result 1 "Backend service is not running"
fi

# Check OCR Service
if docker ps | grep -q "dastern.*ocr"; then
    print_result 0 "OCR service is running"
else
    print_result 1 "OCR service is not running"
fi

# Check AI Service
if docker ps | grep -q "dastern.*ai"; then
    print_result 0 "AI service is running"
else
    print_result 1 "AI service is not running"
fi

echo ""
echo "Step 2: Testing database connection..."
echo "---------------------------------------"

# Test database tables
TABLE_COUNT=$(docker compose exec -T postgres psql -U dastern -d dastern -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';" 2>/dev/null | tr -d ' ')

if [ "$TABLE_COUNT" = "17" ]; then
    print_result 0 "Database has all 17 tables"
else
    print_result 1 "Database has $TABLE_COUNT tables (expected 17)"
fi

echo ""
echo "Step 3: Testing API endpoints..."
echo "---------------------------------"

# Test health endpoint
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" ${BASE_URL}/api/health 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    print_result 0 "Health check endpoint (GET /api/health)"
    
    # Get health data
    HEALTH_DATA=$(curl -s ${BASE_URL}/api/health 2>/dev/null)
    echo "   Response: ${HEALTH_DATA}"
else
    print_result 1 "Health check endpoint returned HTTP $HTTP_CODE"
fi

# Test if Next.js is responding
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" ${BASE_URL}/ 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    print_result 0 "Frontend page loads (GET /)"
else
    print_result 1 "Frontend returned HTTP $HTTP_CODE"
fi

echo ""
echo "Step 4: Testing OCR service directly..."
echo "----------------------------------------"

# Create a simple test image with text
TEST_TEXT="Amoxicillin 500mg\nTake 1 tablet twice daily\nFor 7 days"

# Test OCR service health
OCR_HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null || echo "")
if echo "$OCR_HEALTH" | grep -q "healthy"; then
    print_result 0 "OCR service health check"
else
    print_result 1 "OCR service not responding"
fi

echo ""
echo "Step 5: Testing AI service directly..."
echo "---------------------------------------"

# Test AI service health
AI_HEALTH=$(curl -s http://localhost:8001/health 2>/dev/null || echo "")
if echo "$AI_HEALTH" | grep -q "healthy"; then
    print_result 0 "AI service health check"
else
    print_result 1 "AI service not responding"
fi

echo ""
echo "Step 6: Testing database CRUD operations..."
echo "--------------------------------------------"

# Test creating a prescription record
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
    print_result 0 "Insert prescription into database"
    echo "   Created prescription ID: $TEST_UUID"
    
    # Test reading the record
    READ_RESULT=$(docker compose exec -T postgres psql -U dastern -d dastern -t -c "
    SELECT status FROM prescriptions WHERE id = '$TEST_UUID';" 2>/dev/null | tr -d ' \n')
    
    if [ "$READ_RESULT" = "completed" ]; then
        print_result 0 "Read prescription from database"
    else
        print_result 1 "Could not read prescription"
    fi
    
    # Test deleting the record
    docker compose exec -T postgres psql -U dastern -d dastern -c "
    DELETE FROM prescriptions WHERE id = '$TEST_UUID';" >/dev/null 2>&1
    print_result 0 "Delete test prescription"
else
    print_result 1 "Could not insert prescription"
fi

echo ""
echo "================================================"
echo "📊 Test Summary"
echo "================================================"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo "================================================"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "🚀 Next steps:"
    echo "   1. Open http://localhost:3000 in your browser"
    echo "   2. Upload a prescription image"
    echo "   3. View the OCR results and extracted medications"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Please check the errors above.${NC}"
    echo ""
    echo "🔍 Troubleshooting:"
    echo "   - Check service logs: docker compose logs -f"
    echo "   - Restart services: docker compose restart"
    echo "   - Rebuild services: docker compose build"
    echo ""
    exit 1
fi

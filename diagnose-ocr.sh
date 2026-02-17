#!/bin/bash
# OCR Service Diagnostic Script
# Run this to check OCR service status and dependencies

echo "========================================"
echo "DasTern OCR Service Diagnostics"
echo "========================================"
echo ""

echo "1. Container Status:"
docker ps -a --filter "name=dastern-ocr" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "2. Latest Logs (Last 30 lines):"
docker logs dastern-ocr 2>&1 | tail -30
echo ""

echo "3. Check Required Libraries in Container:"
if docker ps --format '{{.Names}}' | grep -q "dastern-ocr"; then
    echo "Checking OpenCV dependencies..."
    docker exec dastern-ocr bash -c "ldd /usr/local/lib/python3.10/site-packages/cv2/cv2*.so 2>/dev/null | grep -E 'not found|libGL|libgthread'" || echo "✓ All libraries found"
else
    echo "Container not running - cannot check libraries"
fi
echo ""

echo "4. Image Build Info:"
docker images dastern-ocr-service --format "Built: {{.CreatedSince}}, Size: {{.Size}}"
echo ""

echo "5. Health Check Status:"
docker inspect dastern-ocr --format='{{.State.Health.Status}}' 2>/dev/null || echo "Container not found"
echo ""

echo "========================================"
echo "Common Issues:"
echo "========================================"
echo "- If 'not found' appears above, rebuild: docker compose build --no-cache ocr-service"
echo "- If container keeps restarting, check logs above for import errors"
echo "- If libGL/libgthread errors, dependencies are missing from Dockerfile"
echo ""

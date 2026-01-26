#!/bin/bash

# Stop all DasTern services

echo "🛑 Stopping DasTern services..."

# Stop OCR service (port 8004)
echo "Stopping OCR service..."
pkill -f "uvicorn.*8004" || echo "OCR service not running"

# Stop AI service (port 8005)
echo "Stopping AI service..."
pkill -f "uvicorn.*8005" || echo "AI service not running"

# Stop Backend (port 3000)
echo "Stopping Backend..."
pkill -f "npm run dev" || echo "Backend not running"

# Stop Ollama
echo "Stopping Ollama..."
pkill -f "ollama serve" || echo "Ollama not running"

echo "✅ All services stopped"

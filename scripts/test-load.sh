#!/bin/bash

# Simple load testing script to test HPA

echo "🧪 Load Testing Ollama HPA..."
echo "This will generate load to trigger autoscaling"
echo ""

# Check if hey is installed
if ! command -v hey &> /dev/null; then
    echo "Installing 'hey' load testing tool..."
    go install github.com/rakyll/hey@latest
fi

# Port forward to the service
echo "Setting up port forward..."
kubectl port-forward svc/fastapi-service 8000:8000 -n ai-assistant &
PORT_FORWARD_PID=$!

sleep 3

echo "Generating load..."
echo "Sending 1000 requests with 50 concurrent workers..."
echo ""

hey -n 1000 -c 50 -m POST \
    -H "Content-Type: application/json" \
    -d '{"query":"What is Kubernetes?"}' \
    http://localhost:8000/api/v1/chat

echo ""
echo "Watch HPA scaling:"
echo "  kubectl get hpa ollama-hpa -n ai-assistant --watch"

# Cleanup
kill $PORT_FORWARD_PID 2>/dev/null
#!/bin/bash

set -e

echo "🚀 Deploying AI Assistant to Kubernetes..."
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Navigate to project root
cd "${PROJECT_ROOT}"

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install it first."
    exit 1
fi

# Check if connected to a cluster
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Not connected to a Kubernetes cluster. Please configure kubectl."
    exit 1
fi

echo "✅ Connected to Kubernetes cluster"
echo ""

# Create namespace
echo "📦 Creating namespace..."
kubectl apply -f kubernetes/namespace.yaml
echo ""

# Deploy Ollama
echo "🤖 Deploying Ollama..."
kubectl apply -f kubernetes/ollama/deployment.yaml
kubectl apply -f kubernetes/ollama/service.yaml
kubectl apply -f kubernetes/ollama/hpa.yaml
echo ""

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama pods to be ready..."
kubectl wait --for=condition=ready pod -l app=ollama-qwen -n ai-assistant --timeout=300s || {
    echo "❌ Ollama pods failed to become ready. Check logs:"
    echo "   kubectl logs -l app=ollama-qwen -n ai-assistant"
    exit 1
}
echo "✅ Ollama is ready!"
echo ""

# Deploy Backend
echo "🚀 Deploying FastAPI Backend..."
kubectl apply -f kubernetes/backend/configmap.yaml
# Note: Apply secrets if you have them
# kubectl apply -f kubernetes/backend/secrets.yaml
kubectl apply -f kubernetes/backend/deployment.yaml
kubectl apply -f kubernetes/backend/service.yaml
echo ""

# Wait for Backend to be ready
echo "⏳ Waiting for Backend pods to be ready..."
kubectl wait --for=condition=ready pod -l app=fastapi-backend -n ai-assistant --timeout=180s || {
    echo "❌ Backend pods failed to become ready. Check logs:"
    echo "   kubectl logs -l app=fastapi-backend -n ai-assistant"
    exit 1
}
echo "✅ Backend is ready!"
echo ""

# Display deployment status
echo "📊 Deployment Status:"
echo ""
echo "Pods:"
kubectl get pods -n ai-assistant
echo ""
echo "Services:"
kubectl get svc -n ai-assistant
echo ""
echo "HPA:"
kubectl get hpa -n ai-assistant
echo ""

# Get the external IP/endpoint for the backend
echo "🌐 Backend Service Endpoint:"
kubectl get svc fastapi-service -n ai-assistant -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "Pending..."
echo ""
echo ""

echo "✅ Deployment complete!"
echo ""
echo "📝 Useful commands:"
echo "  View logs (Ollama):  kubectl logs -l app=ollama-qwen -n ai-assistant -f"
echo "  View logs (Backend): kubectl logs -l app=fastapi-backend -n ai-assistant -f"
echo "  Port forward:        kubectl port-forward svc/fastapi-service 8000:8000 -n ai-assistant"
echo "  Delete all:          kubectl delete namespace ai-assistant"
#!/bin/bash

set -e

# Configuration - UPDATE THESE
REGISTRY="your-dockerhub-username"  # e.g., "myusername" or "myacr.azurecr.io"
IMAGE_NAME="ollama-qwen"
TAG="latest"

echo "🔨 Building Ollama image with Qwen 2.5..."
echo "Registry: ${REGISTRY}"
echo "Image: ${IMAGE_NAME}:${TAG}"
echo ""

# Navigate to the Dockerfile location
cd "$(dirname "$0")/../kubernetes/ollama"

# Build the image
echo "📦 Building Docker image..."
docker build -t ${REGISTRY}/${IMAGE_NAME}:${TAG} .

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo ""
    echo "📤 Pushing to registry..."
    docker push ${REGISTRY}/${IMAGE_NAME}:${TAG}
    
    if [ $? -eq 0 ]; then
        echo "✅ Push successful!"
        echo ""
        echo "Image: ${REGISTRY}/${IMAGE_NAME}:${TAG}"
        echo ""
        echo "⚠️  Don't forget to update the image in kubernetes/ollama/deployment.yaml"
    else
        echo "❌ Push failed!"
        exit 1
    fi
else
    echo "❌ Build failed!"
    exit 1
fi
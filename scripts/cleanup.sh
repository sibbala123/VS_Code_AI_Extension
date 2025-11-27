#!/bin/bash

set -e

echo "🗑️  Cleaning up AI Assistant deployment..."
echo ""

read -p "Are you sure you want to delete the entire ai-assistant namespace? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Deleting namespace and all resources..."
    kubectl delete namespace ai-assistant
    
    echo ""
    echo "✅ Cleanup complete!"
else
    echo "❌ Cleanup cancelled."
fi
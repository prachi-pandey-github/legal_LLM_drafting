#!/bin/bash
# Deployment script for production

set -e

echo "🚀 Starting deployment process..."

# Build Docker images
echo "📦 Building Docker images..."
docker build -t legal-llm-api:latest .
docker build -f Dockerfile.streamlit -t legal-llm-frontend:latest .

# Tag for Docker Hub (optional)
# docker tag legal-llm-api:latest your-dockerhub/legal-llm-api:latest
# docker tag legal-llm-frontend:latest your-dockerhub/legal-llm-frontend:latest

# Push to registry (uncomment if using Docker Hub)
# docker push your-dockerhub/legal-llm-api:latest
# docker push your-dockerhub/legal-llm-frontend:latest

echo "✅ Deployment preparation complete!"
echo ""
echo "Next steps:"
echo "1. Set up your cloud provider (Railway, Heroku, AWS, etc.)"
echo "2. Configure environment variables"
echo "3. Deploy using platform-specific commands"
echo ""
echo "For Railway: Connect GitHub repo and set env vars"
echo "For Heroku: git push heroku main"
echo "For AWS: Use ECS with the provided task definition"
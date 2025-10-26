#!/bin/bash

# Email Phishing Backend - Google Cloud Run Deployment Script
# Usage: ./deploy.sh [PROJECT_ID] [REGION]

set -e  # Exit on error

# Configuration
PROJECT_ID=${1:-"your-project-id"}
REGION=${2:-"us-central1"}
SERVICE_NAME="email-phishing-backend"

echo "================================================"
echo "Deploying Email Phishing Backend to Cloud Run"
echo "================================================"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI not found. Please install it first:"
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo "✅ Google Cloud CLI found"

# Set project
echo "Setting project..."
gcloud config set project "$PROJECT_ID"

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable run.googleapis.com cloudbuild.googleapis.com --quiet

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "   Create a .env file with your environment variables"
    echo ""
fi

# Deploy to Cloud Run
echo ""
echo "🚀 Deploying to Cloud Run..."
echo ""

gcloud run deploy "$SERVICE_NAME" \
  --source . \
  --platform managed \
  --region "$REGION" \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10 \
  --timeout 300 \
  --quiet

echo ""
echo "================================================"
echo "✅ Deployment Complete!"
echo "================================================"

# Get service URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
  --region "$REGION" \
  --format 'value(status.url)')

echo ""
echo "🌐 Service URL: $SERVICE_URL"
echo ""
echo "📝 Next steps:"
echo "1. Set environment variables:"
echo "   gcloud run services update $SERVICE_NAME \\"
echo "     --region $REGION \\"
echo "     --set-env-vars \"EXT_API_KEY=your_key,GEMINI_API_KEY=your_key\""
echo ""
echo "2. Update Chrome extension with this URL:"
echo "   const API_URL = '$SERVICE_URL';"
echo ""
echo "3. Test the deployment:"
echo "   curl $SERVICE_URL/health"
echo ""
echo "4. View logs:"
echo "   gcloud run services logs tail $SERVICE_NAME --region $REGION"
echo ""

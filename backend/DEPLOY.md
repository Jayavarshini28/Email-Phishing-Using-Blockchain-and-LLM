# Deploy to Google Cloud Run

## Quick Deploy Script

Follow these steps to deploy your backend to Google Cloud Run:

### Prerequisites
1. Google Cloud account with billing enabled
2. Google Cloud CLI installed
3. Project created in Google Cloud Console

### Step 1: Setup
```bash
# Login to Google Cloud
gcloud auth login

# Set your project (replace YOUR_PROJECT_ID)
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### Step 2: Deploy
```bash
# Navigate to backend directory
cd backend

# Deploy to Cloud Run
gcloud run deploy email-phishing-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10 \
  --timeout 300
```

### Step 3: Set Environment Variables
```bash
# Set environment variables (replace with your actual values)
gcloud run services update email-phishing-backend \
  --region us-central1 \
  --set-env-vars "EXT_API_KEY=your_api_key_here" \
  --set-env-vars "GEMINI_API_KEY=your_gemini_key_here" \
  --set-env-vars "BLOCKCHAIN_NETWORK_ID=11155111"
```

### Step 4: Get Service URL
```bash
# Get your service URL
gcloud run services describe email-phishing-backend \
  --region us-central1 \
  --format 'value(status.url)'
```

### Step 5: Update Chrome Extension
Update the API URL in your Chrome extension files:
- `phish-analyzer-extension/popup.js`
- `phish-analyzer-extension/content_script.js`

Replace the API_URL with your Cloud Run URL:
```javascript
const API_URL = 'https://email-phishing-backend-XXXXX-uc.a.run.app';
```

### Optional: View Logs
```bash
# Stream logs
gcloud run services logs tail email-phishing-backend --region us-central1
```

### Optional: Use Secret Manager (Recommended for Production)
```bash
# Create secrets
echo -n "your_api_key" | gcloud secrets create EXT_API_KEY --data-file=-
echo -n "your_gemini_key" | gcloud secrets create GEMINI_API_KEY --data-file=-

# Update service to use secrets
gcloud run services update email-phishing-backend \
  --region us-central1 \
  --update-secrets EXT_API_KEY=EXT_API_KEY:latest \
  --update-secrets GEMINI_API_KEY=GEMINI_API_KEY:latest
```

## Monitoring & Management

### Check service status
```bash
gcloud run services list --region us-central1
```

### Update service (redeploy)
```bash
gcloud run deploy email-phishing-backend \
  --source . \
  --region us-central1
```

### Delete service
```bash
gcloud run services delete email-phishing-backend --region us-central1
```

## Cost Optimization Tips

1. **Use min-instances: 0** (default) - Scale to zero when not in use
2. **Set max-instances** - Prevent unexpected costs
3. **Monitor usage** - Check Cloud Console regularly
4. **Use appropriate memory** - 512Mi might be enough, test and adjust

## Troubleshooting

### Build fails
- Check Dockerfile syntax
- Ensure all dependencies are in requirements.txt
- Check Cloud Build logs in console

### Service crashes
- Check logs: `gcloud run services logs tail`
- Verify environment variables
- Check memory/CPU limits

### 502/503 errors
- Increase memory allocation
- Increase timeout
- Check application startup time

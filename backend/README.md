# Email Phishing Backend

Flask backend API for email phishing detection using AI and blockchain.

## Project Structure

```
backend/
├── app.py                      # Main Flask application
├── utils.py                    # ML models and analysis utilities
├── url_utils.py               # URL extraction and feature analysis
├── blockchain_integration.py  # Blockchain interaction layer
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration for Cloud Run
├── .dockerignore             # Files to exclude from Docker build
├── .env                      # Environment variables (not in git)
├── files/                    # ML model files and training data
└── blockchain/               # Smart contract and deployment scripts
    ├── contracts/
    ├── deploy.js
    ├── interact.js
    └── package.json
```

## Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file with:
   ```
   EXT_API_KEY=your_api_key
   GEMINI_API_KEY=your_gemini_key
   BLOCKCHAIN_NETWORK_ID=11155111
   # Add other required keys
   ```

3. **Install blockchain dependencies:**
   ```bash
   cd blockchain
   npm install
   cd ..
   ```

4. **Run locally:**
   ```bash
   python app.py
   ```

## Deployment to Google Cloud Run

1. **Install Google Cloud CLI:**
   ```bash
   # Follow instructions at: https://cloud.google.com/sdk/docs/install
   ```

2. **Authenticate:**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Deploy:**
   ```bash
   gcloud run deploy email-phishing-backend \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --memory 1Gi \
     --cpu 1 \
     --max-instances 10 \
     --set-env-vars EXT_API_KEY=your_key,GEMINI_API_KEY=your_key
   ```

4. **Update Chrome Extension:**
   After deployment, update the API URL in your extension files with the Cloud Run URL.

## API Endpoints

- `POST /analyze` - Analyze email content for phishing
- `GET /health` - Health check endpoint
- `GET /blockchain/status` - Blockchain connection status
- `POST /blockchain/report` - Report phishing domain to blockchain

## Environment Variables

Required:
- `EXT_API_KEY` - API key for extension authentication
- `GEMINI_API_KEY` - Google Gemini API key for LLM analysis

Optional:
- `PORT` - Server port (default: 8080 for Cloud Run)
- `AUTO_REPORT_CONFIDENT_CLASSIFICATIONS` - Auto-report to blockchain (default: true)
- `MIN_CONFIDENCE_FOR_BLOCKCHAIN_REPORT` - Minimum confidence threshold (default: 0.8)
- `BLOCKCHAIN_NETWORK_ID` - Ethereum network ID (default: 11155111 for Sepolia)

## Cost Estimation (Google Cloud Run)

- **Free Tier:** 2M requests/month, 360,000 GB-seconds/month
- **Expected Cost:** $5-10/month for moderate usage
- **Pricing:** Pay only when requests are being processed

## Security Notes

- Never commit `.env` file
- Use Cloud Run secrets for production
- Restrict CORS in production
- Implement rate limiting
- Use authenticated endpoints where appropriate

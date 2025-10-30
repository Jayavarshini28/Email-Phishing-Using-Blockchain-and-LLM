# Email Phishing Detection System

Advanced email phishing detection using Machine Learning, Large Language Models (LLM), and Blockchain technology.

## 🎯 Features

- ✅ **Multi-layer Detection**: ML models + Google Gemini LLM + Blockchain
- ✅ **Chrome Extension**: Real-time Gmail email analysis
- ✅ **Blockchain Integration**: Decentralized domain reputation on Ethereum
- ✅ **Smart Caching**: Blockchain-first strategy (70% faster)
- ✅ **Auto-reporting**: Confidence-based classification storage
- ✅ **User Feedback**: Community-driven learning system.

## 📁 Project Structure

```
Email-Phishing-Using-Blockchain-and-LLM/
├── backend/                          # Flask backend API
│   ├── app.py                       # Main Flask application
│   ├── utils.py                     # ML models & utilities
│   ├── blockchain_integration.py    # Blockchain layer
│   ├── requirements.txt             # Python dependencies
│   ├── Dockerfile                   # Cloud Run deployment
│   ├── README.md                    # Backend documentation
│   ├── DEPLOY.md                    # Deployment guide
│   ├── files/                       # ML models & training data
│   └── blockchain/                  # Smart contracts & scripts
│       ├── contracts/
│       ├── deploy.js
│       └── interact.js
├── phish-analyzer-extension/        # Chrome extension
│   ├── manifest.json
│   ├── popup.html
│   ├── popup.js
│   ├── content_script.js
│   └── background.js
├── DOCUMENTATION.md                 # Complete system documentation
├── CHANGELOG.md                     # Version history
└── ANSWERS.md                       # Q&A and troubleshooting
```

## 🚀 Quick Start

### Backend Setup

1. **Navigate to backend:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   Create `.env` file:
   ```env
   EXT_API_KEY=your_api_key
   GEMINI_API_KEY=your_gemini_key
   BLOCKCHAIN_NETWORK_ID=11155111
   ```

4. **Run locally:**
   ```bash
   python app.py
   ```

### Chrome Extension Setup

1. **Open Chrome Extensions:**
   - Navigate to `chrome://extensions/`
   - Enable "Developer mode"

2. **Load Extension:**
   - Click "Load unpacked"
   - Select `phish-analyzer-extension/` folder

3. **Configure:**
   - Update API URL in extension if backend is deployed remotely

## 🌐 Deployment

### Deploy to Google Cloud Run

See detailed guide in [`backend/DEPLOY.md`](backend/DEPLOY.md)

**Quick deploy:**
```bash
cd backend
gcloud run deploy email-phishing-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi
```

**Cost:** ~$5-10/month for moderate usage (2M free requests/month)

### Chrome Web Store

1. Prepare extension package
2. Create developer account ($5 one-time fee)
3. Submit for review
4. Ensure backend is deployed and accessible

## 📖 Documentation

- **[DOCUMENTATION.md](DOCUMENTATION.md)** - Complete system documentation
- **[backend/README.md](backend/README.md)** - Backend API reference
- **[backend/DEPLOY.md](backend/DEPLOY.md)** - Deployment guide
- **[CHANGELOG.md](CHANGELOG.md)** - Version history
- **[ANSWERS.md](ANSWERS.md)** - FAQ and troubleshooting

## 🔧 Technology Stack

- **Backend:** Flask, Python, Gunicorn
- **ML:** scikit-learn, sentence-transformers
- **LLM:** Google Gemini API
- **Blockchain:** Ethereum (Sepolia), Hardhat, Web3.js
- **Frontend:** Chrome Extension (vanilla JS)
- **Deployment:** Google Cloud Run
- **Smart Contracts:** Solidity

## 🔐 Security

- API key authentication
- CORS protection
- Rate limiting (recommended for production)
- Environment-based configuration
- No sensitive data in repository

## 📊 API Endpoints

- `POST /analyze` - Analyze email for phishing
- `GET /health` - Health check
- `GET /blockchain/status` - Blockchain connection status
- `POST /blockchain/report` - Report phishing domain

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

This project is for educational purposes.

## 🙏 Acknowledgments

- Google Gemini for LLM capabilities
- Ethereum blockchain for decentralized storage
- scikit-learn for ML models
- Flask framework

## 📞 Support

For issues and questions, see [ANSWERS.md](ANSWERS.md) or create an issue on GitHub.

---

**Note:** This is a demonstration project. For production use, implement additional security measures, rate limiting, and proper key management.

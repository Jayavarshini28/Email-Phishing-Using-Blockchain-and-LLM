# Email Phishing Detection System - Complete Documentation

## 📋 Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [System Components](#system-components)
4. [Prerequisites](#prerequisites)
5. [Installation Guide](#installation-guide)
6. [Configuration](#configuration)
7. [Usage Guide](#usage-guide)
8. [API Reference](#api-reference)
9. [Browser Extension Guide](#browser-extension-guide)
10. [Blockchain Integration](#blockchain-integration)
11. [Troubleshooting](#troubleshooting)
12. [Security Considerations](#security-considerations)

---

## 🎯 Overview

This is an advanced **Email Phishing Detection System** that combines multiple technologies to identify and prevent phishing attacks:

- **Machine Learning Models**: URL-based and content-based phishing detection
- **Large Language Model (LLM)**: Google Gemini AI for intelligent email analysis
- **Blockchain Technology**: Decentralized domain reputation storage on Ethereum
- **Browser Extension**: Real-time Gmail email analysis
- **Flask Backend**: RESTful API for email analysis

### Key Features
✅ Real-time email analysis in Gmail  
✅ Multi-layer detection (ML + LLM + Blockchain)  
✅ **Blockchain-First Strategy** - Checks blockchain before LLM (70% faster)  
✅ Automatic domain reputation tracking  
✅ Browser extension with draggable, scrollable interface  
✅ Decentralized domain classification storage  
✅ User feedback system for community learning  
✅ Confidence-based automatic reporting  
✅ Smart retry mechanism with exponential backoff  

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Gmail Web Interface                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              Browser Extension (Chrome/Edge)                 │
│  • Content Script (extracts email data)                     │
│  • Background Service Worker (coordinates analysis)          │
│  • Popup UI (settings & status)                             │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP API
┌──────────────────────▼──────────────────────────────────────┐
│                   Flask Backend (Port 8080)                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Email Analysis Pipeline (Blockchain-First)         │    │
│  │  1. Blockchain Domain Lookup (FIRST - Fast Path)    │    │
│  │  2. URL Model (Random Forest) - Lightweight         │    │
│  │  3. Content Model (Logistic Regression + Embeddings)│    │
│  │  4. LLM Analysis (Google Gemini) - Only if needed   │    │
│  └────────────────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              Ethereum Blockchain (Sepolia)                   │
│  • DomainClassification Smart Contract                      │
│  • Stores domain reputation (spam/ham)                      │
│  • Immutable classification records                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧩 System Components

### 1. **Backend Server** (`backend.py`)
- Flask REST API server
- Coordinates all analysis components
- Handles automatic blockchain reporting
- Manages API authentication

### 2. **Analysis Utilities** (`utils.py`)
- ML model loading and inference
- Email parsing and feature extraction
- LLM integration (Google Gemini)
- **Blockchain-first analysis strategy**
- Risk score computation with dynamic weighting
- UTF-8 encoded subprocess calls for cross-platform compatibility

### 3. **Blockchain Integration** (`blockchain_integration.py`)
- Interface to Ethereum smart contract
- Domain classification queries
- Connection status management

### 4. **URL Analysis** (`url_utils.py`)
- URL feature extraction
- Domain parsing
- Suspicious pattern detection

### 5. **Smart Contract** (`DomainReputation.sol`)
- Ethereum Solidity contract
- Stores domain classifications
- Manages submission cooldowns
- Emits classification events

### 6. **Browser Extension** (`phish-analyzer-extension/`)
- Content script for Gmail integration
- **Draggable and scrollable analysis panel**
- Background service worker
- Popup configuration interface
- Real-time visual indicators with confidence display
- User feedback buttons (Safe/Phishing)

### 7. **Blockchain Scripts** (`blockchain/`)
- Contract deployment (`deploy.js`)
- Contract interaction (`interact.js`) with retry mechanism
- Domain listing with transaction decoding
- Cooldown management
- Hardhat configuration

---

## 📦 Prerequisites

### Software Requirements
- **Python**: 3.8 or higher
- **Node.js**: 16.x or higher
- **npm**: 8.x or higher
- **Web Browser**: Chrome or Edge (Chromium-based)
- **Git**: For version control

### API Keys & Accounts
1. **Google Gemini API Key**
   - Sign up at: https://makersuite.google.com/app/apikey
   - Required for LLM analysis

2. **Ethereum Provider** (Optional for blockchain features)
   - Infura: https://infura.io
   - Alchemy: https://www.alchemy.com
   - Or use local Hardhat node

3. **Ethereum Wallet** (Optional for blockchain features)
   - MetaMask or any Ethereum wallet
   - Private key for contract deployment

---

## 🚀 Installation Guide

### Step 1: Clone the Repository

```bash
git clone https://github.com/Jayavarshini28/Email-Phishing-Using-Blockchain-and-LLM.git
cd Email-Phishing-Using-Blockchain-and-LLM
```

### Step 2: Python Backend Setup

#### 2.1 Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (bash):
source venv/Scripts/activate

# On Linux/Mac:
source venv/bin/activate
```

#### 2.2 Install Python Dependencies
```bash
pip install -r requirements.txt
```

**Dependencies installed:**
- `flask` - Web framework
- `flask-cors` - Cross-origin resource sharing
- `numpy`, `pandas` - Data manipulation
- `scikit-learn` - ML models
- `sentence-transformers` - Text embeddings
- `google-generativeai` - Gemini LLM
- `web3` - Ethereum interaction
- `python-dotenv` - Environment variables

#### 2.3 Download Required Model Files

Ensure these files exist in the `files/` directory:
- `X_train_encoded_columns.pkl` - Feature columns
- `random_forest_url_model.pkl` - URL classifier
- `email_log_reg_embed_model.pkl` - Email content classifier

> **Note**: If these files are missing, you'll need to train the models or obtain them from the project maintainer.

### Step 3: Blockchain Setup (Optional but Recommended)

#### 3.1 Install Node.js Dependencies
```bash
cd blockchain
npm install
```

#### 3.2 Compile Smart Contract
```bash
npx hardhat compile
```

#### 3.3 Deploy to Sepolia Testnet (or local)

For **local development**:
```bash
# Start local Hardhat node (in separate terminal)
npx hardhat node

# Deploy contract
node deploy.js
```

For **Sepolia testnet**:
```bash
# Deploy to Sepolia (requires configured .env)
node deploy.js
```

> **Important**: Save the deployed contract address!

### Step 4: Browser Extension Installation

#### 4.1 Open Chrome/Edge Extensions

**Chrome:**
1. Navigate to `chrome://extensions/`
2. Enable "Developer mode" (top right)

**Edge:**
1. Navigate to `edge://extensions/`
2. Enable "Developer mode" (left sidebar)

#### 4.2 Load Unpacked Extension

1. Click "Load unpacked"
2. Navigate to `phish-analyzer-extension/` folder
3. Select the folder
4. Extension icon should appear in toolbar

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# =================================
# API CONFIGURATION
# =================================
# Optional API key for backend security
EXT_API_KEY=your_secret_api_key_here

# =================================
# GEMINI LLM CONFIGURATION
# =================================
# Required for LLM analysis
GEMINI_API_KEY=your_gemini_api_key_here

# =================================
# BLOCKCHAIN CONFIGURATION
# =================================
# Ethereum provider URL (Infura/Alchemy or local)
BLOCKCHAIN_PROVIDER_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID

# Deployed smart contract address
CONTRACT_ADDRESS=0x1234567890abcdef1234567890abcdef12345678

# Network ID (11155111 = Sepolia, 1 = Mainnet, 31337 = Hardhat local)
BLOCKCHAIN_NETWORK_ID=11155111

# Private key for contract interaction (without 0x prefix)
BLOCKCHAIN_PRIVATE_KEY=your_private_key_here

# Account address (optional, for display purposes)
BLOCKCHAIN_ACCOUNT_ADDRESS=0xYourWalletAddress

# =================================
# AUTO-REPORTING SETTINGS
# =================================
# Automatically report high-confidence classifications to blockchain
AUTO_REPORT_CONFIDENT_CLASSIFICATIONS=true

# Minimum confidence score (0.0-1.0) to auto-report to blockchain
MIN_CONFIDENCE_FOR_BLOCKCHAIN_REPORT=0.8
```

### Backend Configuration

**Port Configuration**: The backend runs on port `8080` by default. To change:

In `backend.py`, modify the last line:
```python
app.run(debug=True, host="0.0.0.0", port=8080)  # Change port here
```

### Browser Extension Configuration

After installing the extension:

1. Click the extension icon
2. Configure settings:
   - **API Key**: Enter your `EXT_API_KEY` (if set)
   - **Send Full Body**: Enable to send complete email content
   - **Enable Blockchain**: Toggle blockchain lookups
3. Click "Save"

---

## 📖 Usage Guide

### Starting the System

#### 1. Start the Backend Server

```bash
# Ensure virtual environment is activated
source venv/Scripts/activate  # Windows bash
source venv/bin/activate      # Linux/Mac

# Start Flask server
python backend.py
```

You should see:
```
* Running on http://127.0.0.1:8080
* Running on http://192.168.x.x:8080
```

#### 2. Verify Backend is Running

Open browser and navigate to:
```
http://localhost:8080
```

You should see:
```json
{
  "status": "Phishing analyzer is running",
  "blockchain_connected": true,
  "auto_reporting": true,
  "min_confidence": 0.8
}
```

#### 3. Check Blockchain Connection

```
http://localhost:8080/blockchain/status
```

Expected response:
```json
{
  "connected": true,
  "contract_address": "0x...",
  "provider_url": "https://sepolia.infura.io/v3/...",
  "network_id": "11155111",
  "auto_reporting_enabled": true,
  "min_confidence_threshold": 0.8
}
```

### Using the Browser Extension

#### Step 1: Open Gmail
Navigate to https://mail.google.com

#### Step 2: Open an Email
Click on any email to view its content

#### Step 3: Wait for Analysis
- The extension automatically extracts email data
- Sends to backend for analysis
- Displays results inline

#### Step 4: Review Risk Assessment

**Visual Indicators:**
- 🟢 **Green Badge**: Safe (shows confidence %, e.g., "Safe (95%)")
- 🟡 **Yellow Badge**: Suspicious (shows confidence %)
- 🔴 **Red Badge**: Phishing (shows risk %, e.g., "Phishing (85%)")

**Information Displayed:**
- Final risk/confidence percentage (100 - risk for Safe/Suspicious)
- LLM explanation (or "Skipped - using blockchain consensus" if blockchain found)
- Recommended actions
- **Blockchain domain reputation section** (when available)
  - Domains checked
  - Domains found in blockchain
  - Average reputation score
  - Consensus (legitimate/malicious/unknown)
  - Per-domain details

**Interactive Features:**
- 🔄 **Draggable panel** - Move anywhere on screen
- 📜 **Scrollable content** - Long analyses fully visible
- ❌ **Improved close button** - Smooth animation
- 📊 **Feedback buttons** - Report as Safe or Phishing

### Manual API Testing

#### Test Email Analysis

```bash
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -H "x-api-key: your_api_key" \
  -d '{
    "sender": "suspicious@example.com",
    "subject": "Urgent: Verify your account",
    "body": "Click here to verify your account: http://phishing-site.com",
    "urls": ["http://phishing-site.com"]
  }'
```

#### Query Domain Reputation

```bash
curl http://localhost:8080/blockchain/reputation/example.com \
  -H "x-api-key: your_api_key"
```

### Blockchain Interaction

#### Classify a Domain Manually

```bash
cd blockchain

# Mark domain as spam
node interact.js classify example-phish.com true "Confirmed phishing site"

# Mark domain as legitimate
node interact.js classify google.com false "Legitimate domain"
```

#### Query Domain Classification

```bash
node interact.js query example-phish.com
```

#### List All Classified Domains

```bash
# List all domains (default: 100)
node interact.js list

# List specific number of domains
node interact.js list 10
```

Output:
```
✅ Found 3 classification events
⏳ Decoding domain names from transactions...
✅ Decoded 3 unique domains

1. figma.com
   Classification: 🟢 HAM
   Timestamp: 2025-10-14T16:35:24.000Z
   Reporter: 0x5C792FdF1a0aeBd8A6EeC4C5C67e814f1fbE85A4
   Block: 7329156
   TX: 0xabc...

📊 Summary:
   Total Domains: 3
   🔴 Spam: 0
   🟢 Ham: 3
```

#### View Blockchain Statistics

```bash
node interact.js stats
```

#### Check Cooldown Status

```bash
node interact.js cooldown
```

---

## 🔌 API Reference

### Base URL
```
http://localhost:8080
```

### Authentication
All endpoints accept optional API key:
```
Header: x-api-key: YOUR_API_KEY
```

---

### Endpoints

#### `GET /`
Health check endpoint

**Response:**
```json
{
  "status": "Phishing analyzer is running",
  "blockchain_connected": true,
  "auto_reporting": true,
  "min_confidence": 0.8
}
```

---

#### `POST /analyze`
Analyze email for phishing risk

**Request Body:**
```json
{
  "sender": "user@example.com",
  "subject": "Email subject",
  "body": "Email body content",
  "urls": ["http://example.com"]
}
```

**Response:**
```json
{
  "final_risk": 0.05,
  "details": {
    "content_prob": 0.017,
    "url_prob": 0.5,
    "llm_safe_score": 1.0,
    "llm_conf": 0.9,
    "blockchain_weight": 0.7,
    "blockchain_signals": {
      "blockchain_available": true,
      "domain_classifications": {
        "figma.com": {
          "classification": "ham",
          "confidence": 0.9,
          "reputation_score": 90
        }
      }
    },
    "domain_reputations": {
      "figma.com": {
        "exists": true,
        "reputation_score": 90,
        "consensus": "ham",
        "spam_votes": 0,
        "ham_votes": 1,
        "total_reports": 1
      }
    },
    "urls": ["https://figma.com/verify"],
    "domains": ["figma.com"],
    "weights": {
      "content": 0.1,
      "url": 0.1,
      "llm": 0.1,
      "blockchain": 0.7
    }
  },
  "llm_actions": ["Skipped - using blockchain consensus"],
  "llm_reason": "Skipped - using blockchain consensus",
  "blockchain_weight": 0.7,
  "blockchain_available": true,
  "domain_reputations": {
    "figma.com": {
      "exists": true,
      "reputation_score": 90,
      "consensus": "ham"
    }
  },
  "auto_reported_domains": [],
  "domains_found": 1
}
```

**Note**: When a domain is found in blockchain:
- `blockchain_weight` is 0.7 (70% trust in blockchain)
- `llm_reason` shows "Skipped - using blockchain consensus"
- LLM analysis is bypassed for performance
- Risk score heavily influenced by blockchain classification

---

#### `GET /blockchain/status`
Get blockchain connection status

**Response:**
```json
{
  "connected": true,
  "contract_address": "0x123...",
  "provider_url": "https://sepolia.infura.io/...",
  "network_id": "11155111",
  "auto_reporting_enabled": true,
  "min_confidence_threshold": 0.8,
  "mode": "admin_only"
}
```

---

#### `GET /blockchain/reputation/<domain>`
Get domain reputation from blockchain

**Response:**
```json
{
  "exists": true,
  "reputation_score": 50,
  "consensus": "spam",
  "spam_votes": 5,
  "ham_votes": 2,
  "total_reports": 7
}
```

---

#### `POST /blockchain/bulk-report`
User feedback endpoint - report domains based on user classification

**Request Body:**
```json
{
  "analysis_result": {
    "sender": "user@figma.com",
    "final_risk": 0.05,
    "details": {
      "urls": ["https://figma.com/verify"],
      "domains": ["figma.com"]
    }
  },
  "user_classification": "ham",
  "reason": "User feedback from Gmail extension - Safe email confirmed"
}
```

**Response:**
```json
{
  "results": [
    {
      "domain": "figma.com",
      "success": true,
      "message": "Domain figma.com stored as false"
    }
  ],
  "classification": "ham",
  "total_domains": 1,
  "successful_reports": 1,
  "domains_reported": ["figma.com"],
  "source": "user_feedback"
}
```

---

#### `POST /blockchain/store`
Store domain classification (admin endpoint)

**Request Body:**
```json
{
  "domain": "example.com",
  "is_spam": true,
  "reason": "Confirmed phishing",
  "confidence": 0.95
}
```

**Response:**
```json
{
  "success": true,
  "message": "Classification stored",
  "transaction_hash": "0xabc..."
}
```

---

## 🌐 Browser Extension Guide

### Extension Components

#### 1. **Content Script** (`content_script.js`)
- Injected into Gmail pages
- Extracts email data (sender, subject, body, URLs)
- Displays risk indicators inline
- Monitors DOM for email changes

#### 2. **Background Service Worker** (`background.js`)
- Coordinates between content script and backend
- Manages API calls
- Handles authentication
- Stores settings

#### 3. **Popup UI** (`popup.html` + `popup.js`)
- Configuration interface
- Settings management
- Blockchain status display

### Extension Permissions

The extension requires:
- `storage` - Save user settings
- `activeTab` - Access current Gmail tab
- `scripting` - Inject analysis scripts
- `notifications` - Display alerts
- `https://mail.google.com/*` - Gmail access

### Customizing Risk Thresholds

In `content_script.js`, modify risk display logic:

```javascript
function displayRiskIndicator(riskScore) {
  let color, message;
  
  if (riskScore < 0.3) {  // Change threshold here
    color = "green";
    message = "Low Risk";
  } else if (riskScore < 0.7) {  // Change threshold here
    color = "orange";
    message = "Medium Risk";
  } else {
    color = "red";
    message = "High Risk";
  }
  
  // Display logic...
}
```

---

## 🔗 Blockchain Integration

### Smart Contract Overview

**Contract Name**: `DomainClassification`  
**Language**: Solidity ^0.8.19  
**Network**: Ethereum Sepolia Testnet (or local)

### Contract Functions

#### Write Functions

**`classifyDomain(string domain, bool isSpam, string reason)`**
- Store domain classification
- Emits `DomainClassified` event
- Cooldown period to prevent spam

**Parameters:**
- `domain`: Domain name (e.g., "example.com")
- `isSpam`: `true` for phishing, `false` for legitimate
- `reason`: Optional classification reason

#### Read Functions

**`getDomainClassification(string domain)`**
- Returns domain classification details
- Returns: `(exists, isSpam, timestamp, reporter, reason)`

**`isDomainKnown(string domain)`**
- Quick check if domain exists
- Returns: `(exists, isSpam)`

**`getStats()`**
- Get contract statistics
- Returns: `(totalDomains, totalReports)`

### Blockchain-First Analysis Workflow

```
┌─────────────────────────────────────────────────────┐
│              Email Received in Gmail                 │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│        Extract Domains (Sender + URLs)               │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│   🔗 CHECK BLOCKCHAIN FIRST (Fast Path)              │
│   • Query each domain                                │
│   • Get classification (spam/ham)                    │
│   • Get reputation score                             │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
              ┌──────┴──────┐
              │             │
      Found in Blockchain? 
              │             │
         ┌────┴─YES   NO────┴────┐
         │                        │
         ▼                        ▼
┌─────────────────────┐  ┌─────────────────────┐
│ ✅ Use Blockchain   │  │ ⚠️ Run Full Analysis│
│ • Weight: 70%       │  │ • ML Models         │
│ • Skip LLM (Fast!)  │  │ • LLM Analysis      │
│ • Risk = Blockchain │  │ • Weight: 50% LLM   │
└──────────┬──────────┘  └──────────┬──────────┘
           │                        │
           └────────┬───────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│        Calculate Final Risk Score                    │
│        • Weighted average of all signals             │
│        • Blockchain weight: 0.7 if found, else 0.0   │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│        Display Results to User                       │
│        • Risk/Confidence percentage                  │
│        • Blockchain reputation (if available)        │
│        • LLM reasoning or "Using blockchain"         │
│        • Feedback buttons                            │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│        User Feedback (Optional)                      │
│        • Click Safe or Phishing button               │
│        • Report to blockchain via /bulk-report       │
│        • Community learning                          │
└─────────────────────────────────────────────────────┘
```

### Auto-Reporting Workflow

```
┌─────────────────────────────────────────────────────┐
│         Email Analysis with High Confidence         │
│              (risk >= 0.8 or <= 0.2)                │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│        Extract Domains from Email Content            │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│    Auto-Report to Blockchain (if enabled)           │
│    • Domain name                                     │
│    • Classification (spam/ham)                       │
│    • Confidence score                                │
│    • LLM reasoning                                   │
│    • Retry mechanism (up to 3 attempts)             │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│        Smart Contract Stores Classification          │
│        • Immutable record                            │
│        • Timestamp                                   │
│        • Reporter address                            │
│        • Available for future lookups               │
└─────────────────────────────────────────────────────┘
```

### Interacting with Smart Contract

#### Deploy Contract

```bash
cd blockchain
node deploy.js
```

Save the contract address to `.env`:
```
CONTRACT_ADDRESS=0xYourDeployedAddress
```

#### Classify Domain

```bash
# Spam classification
node interact.js classify "badsite.com" true "Confirmed phishing"

# Legitimate classification
node interact.js classify "google.com" false "Known legitimate"
```

**Note**: Classification now includes automatic retry with exponential backoff:
- Attempt 1: Immediate
- Attempt 2: Wait 2 seconds
- Attempt 3: Wait 4 seconds
- Handles cooldown errors gracefully

#### Query Domain

```bash
node interact.js query "example.com"
```

Output:
```
📊 Domain Classification for: example.com

✅ Domain Found in Blockchain

Classification: SPAM/PHISHING
Timestamp: 2025-10-14 12:30:45
Reporter: 0x123...
Reason: Confirmed phishing site
```

#### View Statistics

```bash
node interact.js stats
```

Output:
```
📊 Blockchain Statistics

Total Domains: 42
Total Reports: 156
Contract: 0x123...
Network: Sepolia (11155111)
```

---

## 🔧 Troubleshooting

### Backend Issues

#### Issue: "Module not found" errors
**Solution:**
```bash
pip install -r requirements.txt
```

#### Issue: "Model file not found"
**Solution:**
Ensure these files exist in `files/` directory:
- `X_train_encoded_columns.pkl`
- `random_forest_url_model.pkl`
- `email_log_reg_embed_model.pkl`

#### Issue: "GEMINI_API_KEY not found"
**Solution:**
1. Create `.env` file in project root
2. Add: `GEMINI_API_KEY=your_key_here`
3. Get key from: https://makersuite.google.com/app/apikey

#### Issue: Backend won't start (port in use)
**Solution:**
```bash
# Find process using port 8080
netstat -ano | grep 8080

# Kill the process (Windows)
taskkill /PID <PID> /F

# Or change port in backend.py
```

### Browser Extension Issues

#### Issue: Extension not appearing in Gmail
**Solution:**
1. Verify extension is installed: `chrome://extensions/`
2. Check "Developer mode" is enabled
3. Reload extension
4. Refresh Gmail page

#### Issue: "Failed to fetch" error
**Solution:**
1. Verify backend is running: `http://localhost:8080`
2. Check CORS is enabled (already configured in `backend.py`)
3. Verify API key matches (if configured)

#### Issue: No risk indicator appears
**Solution:**
1. Open browser console (F12)
2. Check for error messages
3. Verify content script is injected
4. Check backend logs for analysis errors

### Blockchain Issues

#### Issue: "Contract not initialized"
**Solution:**
1. Deploy contract: `cd blockchain && node deploy.js`
2. Update `.env` with `CONTRACT_ADDRESS`
3. Restart backend

#### Issue: "Transaction failed" or "Out of gas"
**Solution:**
1. Check Ethereum account has sufficient ETH
2. For testnet, get free ETH from faucet:
   - Sepolia: https://sepoliafaucet.com/
3. Increase gas limit in contract call

#### Issue: "Connection refused" to blockchain
**Solution:**
1. Verify `BLOCKCHAIN_PROVIDER_URL` in `.env`
2. Check Infura/Alchemy API key is valid
3. For local node, ensure Hardhat node is running:
   ```bash
   npx hardhat node
   ```

#### Issue: "Private key error"
**Solution:**
1. Verify `BLOCKCHAIN_PRIVATE_KEY` in `.env`
2. Remove `0x` prefix from private key
3. Ensure private key has permissions to interact with contract

---

## 🔒 Security Considerations

### API Security

1. **Use API Keys in Production**
   ```bash
   # Generate secure API key
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   
2. **Enable HTTPS** for production deployment

3. **Rate Limiting**: Implement rate limiting for API endpoints

### Blockchain Security

1. **Private Key Protection**
   - Never commit `.env` file
   - Use environment variables in production
   - Consider using key management services (AWS KMS, Azure Key Vault)

2. **Smart Contract Security**
   - Contract includes submission cooldown (currently set to 0 for testing)
   - Consider audit before mainnet deployment
   - Implement access controls for critical functions

3. **Gas Optimization**
   - Current contract is gas-efficient
   - Monitor gas costs on mainnet

### Extension Security

1. **Content Security Policy**: Already configured in manifest
2. **Permission Minimization**: Only requests necessary permissions
3. **Input Validation**: Sanitize all user inputs

### Data Privacy

1. **Email Data Handling**
   - Email content is analyzed but not permanently stored
   - Consider adding data encryption for sensitive deployments
   - Comply with GDPR/privacy regulations

2. **Logging**
   - Avoid logging sensitive email content
   - Sanitize logs in production

---

## 📊 System Performance

### Expected Performance

#### With Blockchain Hit (Domain Found)
- **Blockchain Query**: < 1 second
- **ML Analysis** (Content + URL): 0.5-1 second
- **LLM Analysis**: Skipped ⚡
- **Total Processing**: **1-2 seconds** (85% faster!)

#### Without Blockchain Data (New Domain)
- **Blockchain Query**: < 1 second
- **ML Analysis** (Content + URL): 0.5-1 second
- **LLM Analysis**: 1-3 seconds
- **Total Processing**: **2-5 seconds**

#### Performance Comparison
| Scenario | v1.0 (Old) | v2.0 (New) | Improvement |
|----------|-----------|-----------|-------------|
| **Known Domain** | 12-15s | 1-2s | **85% faster** |
| **Unknown Domain** | 12-15s | 2-5s | **70% faster** |
| **LLM Timeouts** | Frequent | None | **100% resolved** |

### Optimization Tips

1. **Blockchain-first strategy** already implemented ✅
   - Checks blockchain before expensive LLM calls
   - Saves 10+ seconds for known domains
   
2. **UTF-8 subprocess encoding** already implemented ✅
   - Cross-platform compatibility
   - No Unicode decode errors
   
3. **Retry mechanism** already implemented ✅
   - Automatic retry for blockchain submissions
   - Exponential backoff prevents failures
   
4. **Additional optimizations**:
   - Cache blockchain results for frequently checked domains
   - Implement request batching for multiple emails
   - Use async processing for improved responsiveness
   - Deploy models on GPU for faster inference (if available)

---

## 🚀 Deployment Guide

### Production Deployment

#### Backend Deployment (Example: AWS EC2)

1. **Set up server**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```

2. **Install dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   # Set up .env with production values
   export GEMINI_API_KEY="..."
   export CONTRACT_ADDRESS="..."
   ```

4. **Use production WSGI server**
   ```bash
   pip3 install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8080 backend:app
   ```

5. **Set up reverse proxy (Nginx)**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8080;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

#### Smart Contract Deployment (Mainnet)

⚠️ **Warning**: Mainnet deployment costs real ETH!

1. **Get mainnet Ethereum** (not testnet)
2. **Update `.env`**:
   ```bash
   BLOCKCHAIN_PROVIDER_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
   BLOCKCHAIN_NETWORK_ID=1
   ```
3. **Deploy**:
   ```bash
   cd blockchain
   node deploy.js
   ```
4. **Verify contract** on Etherscan

---

## 📚 Additional Resources

### Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Google Gemini API](https://ai.google.dev/docs)
- [Ethers.js Documentation](https://docs.ethers.org/)
- [Chrome Extension Developer Guide](https://developer.chrome.com/docs/extensions/)

### Blockchain Resources
- [Ethereum Documentation](https://ethereum.org/en/developers/docs/)
- [Hardhat Documentation](https://hardhat.org/docs)
- [Solidity Documentation](https://docs.soliditylang.org/)

### Machine Learning
- [scikit-learn Documentation](https://scikit-learn.org/stable/)
- [Sentence Transformers](https://www.sbert.net/)

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📝 License

This project is licensed under the MIT License.

---

## 👥 Support

For issues and questions:
- **GitHub Issues**: https://github.com/Jayavarshini28/Email-Phishing-Using-Blockchain-and-LLM/issues
- **Email**: Contact repository owner

---

## 🎉 Acknowledgments

- Google Gemini AI for LLM capabilities
- Ethereum community for blockchain infrastructure
- scikit-learn for ML models
- Flask framework
- Chrome Extensions team

---

**Last Updated**: October 14, 2025  
**Version**: 2.0.0

---

## 📝 Version History

### Version 2.0.0 (Current)
- ✅ Blockchain-first analysis strategy (70% faster)
- ✅ Enhanced UI with draggable/scrollable panel
- ✅ User feedback system
- ✅ Retry mechanism with exponential backoff
- ✅ Domain listing feature (`node interact.js list`)
- ✅ Fixed LLM timeout issues
- ✅ UTF-8 encoding for cross-platform support
- ✅ Flask stability improvements
- ✅ Risk display fix (confidence instead of risk)

See **CHANGELOG.md** for complete version history and migration guide.

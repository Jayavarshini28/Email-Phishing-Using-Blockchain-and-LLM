# Smart Contract Deployment Guide

## Prerequisites
- Node.js and npm installed
- Hardhat setup in `backend/blockchain/`
- Blockchain network configured (Sepolia testnet or local)
- Private key and RPC URL in `.env`

## Step 1: Navigate to Blockchain Directory

```bash
cd backend/blockchain
```

## Step 2: Install Dependencies (if not already done)

```bash
npm install
```

## Step 3: Compile the Updated Contract

```bash
npx hardhat compile
```

**Expected Output:**
```
Compiled 1 Solidity file successfully (evm target: paris).
```

## Step 4: Deploy the Contract

### For Sepolia Testnet:
```bash
node deploy.js
```

### For Local Hardhat Network:
```bash
# Terminal 1: Start local node
npx hardhat node

# Terminal 2: Deploy
npx hardhat run deploy.js --network localhost
```

## Step 5: Update Environment Variables

After deployment, you'll see output like:
```
✅ Contract deployed to: 0x1234567890abcdef1234567890abcdef12345678
```

Update your `.env` file:
```env
CONTRACT_ADDRESS=0x1234567890abcdef1234567890abcdef12345678
BLOCKCHAIN_PROVIDER_URL=https://sepolia.infura.io/v3/YOUR_KEY
BLOCKCHAIN_PRIVATE_KEY=your_private_key_here
BLOCKCHAIN_NETWORK_ID=11155111
```

## Step 6: Test the Contract

Run a quick test to ensure it works:

```bash
# Query a sender email (should return "not found")
node interact.js query test@example.com

# Classify a sender email
node interact.js classify test@example.com true "Test classification"

# Query again (should return "SPAM")
node interact.js query test@example.com
```

**Expected Output:**
```
🔍 Querying sender email: test@example.com
❓ Sender email not found in blockchain cache
UNKNOWN

📝 Classifying sender email: test@example.com as SPAM
✅ Transaction confirmed in block: 12345
SUCCESS

🔍 Querying sender email: test@example.com
📊 Sender email found:
   Classification: SPAM
   Timestamp: 2025-10-26T...
   Reporter: 0x...
SPAM
```

## Step 7: Restart Backend

```bash
cd ../..
python backend/app.py
```

Check the startup logs:
```
✅ Connected to blockchain: https://sepolia.infura.io/v3/...
✅ Contract loaded: 0x1234567890abcdef1234567890abcdef12345678
🚀 Starting Email Phishing Detection Backend
```

## Step 8: Test the Full Flow

### Test 1: First Email Analysis
```bash
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -H "x-api-key: your_api_key" \
  -d '{
    "sender": "test@example.com",
    "subject": "Test Email",
    "body": "This is a test email",
    "force_llm": false
  }'
```

**Expected Response:**
```json
{
  "final_risk": 0.42,
  "llm_reason": "Analysis completed...",
  "from_previous_incident": false,
  "sender_reputation": {
    "exists": false
  }
}
```

### Test 2: Second Email from Same Sender (After Reporting)

First, report the sender:
```bash
curl -X POST http://localhost:8080/blockchain/bulk-report \
  -H "Content-Type: application/json" \
  -H "x-api-key: your_api_key" \
  -d '{
    "analysis_result": {
      "sender": "test@example.com",
      "final_risk": 0.95
    },
    "user_classification": "spam",
    "reason": "Test report"
  }'
```

Then analyze again:
```bash
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -H "x-api-key: your_api_key" \
  -d '{
    "sender": "test@example.com",
    "subject": "Another Test",
    "body": "Another test email",
    "force_llm": false
  }'
```

**Expected Response:**
```json
{
  "final_risk": 1.0,
  "llm_reason": "Based on previous incidents, this sender was marked as spam...",
  "from_previous_incident": true,
  "sender_reputation": {
    "exists": true,
    "consensus": "spam",
    "reputation_score": 10
  },
  "force_llm_used": false
}
```

### Test 3: Force Fresh LLM Analysis

```bash
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -H "x-api-key: your_api_key" \
  -d '{
    "sender": "test@example.com",
    "subject": "Force LLM Test",
    "body": "Testing force LLM",
    "force_llm": true
  }'
```

**Expected Response:**
```json
{
  "final_risk": 0.45,
  "llm_reason": "Fresh LLM analysis result...",
  "from_previous_incident": true,
  "force_llm_used": true
}
```

## Verification Checklist

- [ ] Contract compiles without errors
- [ ] Contract deploys successfully
- [ ] `CONTRACT_ADDRESS` updated in `.env`
- [ ] Backend connects to contract
- [ ] Can query unknown sender (returns "not found")
- [ ] Can classify a sender email
- [ ] Can query classified sender (returns classification)
- [ ] First email analysis works (no blockchain data)
- [ ] Can report sender via API
- [ ] Second analysis shows "previous incident"
- [ ] Force LLM analysis works
- [ ] Extension shows "Run Fresh LLM Analysis" button

## Troubleshooting

### Contract Deployment Fails
```
Error: insufficient funds for gas
```
**Solution:** Ensure your wallet has enough testnet ETH. Get free Sepolia ETH from:
- https://sepoliafaucet.com/
- https://www.alchemy.com/faucets/ethereum-sepolia

### Backend Can't Connect to Contract
```
❌ Blockchain connection failed
```
**Solution:**
1. Check `CONTRACT_ADDRESS` in `.env`
2. Verify `BLOCKCHAIN_PROVIDER_URL` is correct
3. Ensure network is accessible

### Query Returns "UNKNOWN"
```
❓ Sender email not found in blockchain cache
UNKNOWN
```
**Solution:** This is expected for new sender emails. Classify them first.

### Transaction Timeout
```
⏱️ Blockchain storage timeout
```
**Solution:**
1. Check network congestion
2. Increase gas price in contract
3. Wait and retry

## Maintenance

### Check Contract Stats
```bash
node interact.js stats
```

### Query Specific Sender
```bash
node interact.js query sender@example.com
```

### Classify Sender Manually
```bash
node interact.js classify sender@example.com true "Manual spam classification"
node interact.js classify sender@example.com false "Manual ham classification"
```

## Security Notes

- ⚠️ Never commit `.env` file with private keys
- ⚠️ Use testnet for development
- ⚠️ Implement rate limiting in production
- ⚠️ Add authentication to admin endpoints
- ⚠️ Monitor contract for abuse

---

**Deployment Complete!** 🚀

Your system now stores sender email addresses in the blockchain and prevents false positives from common domains!

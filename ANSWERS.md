# 🔐 Blockchain Integration Deep Dive - Complete Technical Analysis

## Table of Contents
1. Why JavaScript for Blockchain?
2. Role of Private Key & Contract Address
3. Complete Low-Level Workflow

---

## 1. Why JavaScript for Blockchain Integration?

### 🤔 The Question
You're using **Python** for the backend (Flask), but **JavaScript (Node.js)** for blockchain interactions. Why this design choice?

### ✅ The Answer: Technical & Practical Reasons

#### **1.1 Ethers.js is the Industry Standard**

```javascript
// JavaScript (Node.js) with Ethers.js
import { ethers } from "ethers";

const provider = new ethers.JsonRpcProvider("https://sepolia.infura.io/v3/...");
const wallet = new ethers.Wallet(privateKey, provider);
const contract = new ethers.Contract(address, abi, wallet);

// Clean, mature, well-documented
const tx = await contract.classifyDomain("example.com", true, "Phishing");
await tx.wait(); // Wait for confirmation
```

**Why Ethers.js?**
- ✅ **Battle-tested**: Used by 90% of Web3 projects
- ✅ **Active development**: Weekly updates, bug fixes
- ✅ **Comprehensive**: Handles all Ethereum operations (signing, encoding, events)
- ✅ **TypeScript support**: Type safety for complex operations
- ✅ **Event handling**: Easy to listen to contract events
- ✅ **Transaction management**: Automatic nonce, gas estimation

#### **1.2 Python Blockchain Libraries Are Immature**

```python
# Python with Web3.py (alternative)
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://sepolia.infura.io/v3/..."))
contract = w3.eth.contract(address=address, abi=abi)

# More verbose, less intuitive
tx_hash = contract.functions.classifyDomain("example.com", True, "Phishing").transact({
    'from': account,
    'gas': 200000,
    'gasPrice': w3.toWei('50', 'gwei')
})
# Manual transaction receipt handling
receipt = w3.eth.waitForTransactionReceipt(tx_hash)
```

**Problems with Web3.py:**
- ❌ **Less documentation**: Smaller community, fewer examples
- ❌ **More boilerplate**: Requires manual gas estimation, nonce management
- ❌ **Event parsing complexity**: Harder to decode indexed parameters
- ❌ **Slower updates**: Lags behind Ethereum protocol changes
- ❌ **Type conversion issues**: Python types ↔ Solidity types require manual handling

#### **1.3 Subprocess Architecture Benefits**

Your current architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                      Python Backend                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Flask API  (handles HTTP, ML, analysis logic)        │  │
│  └─────────────────────┬─────────────────────────────────┘  │
│                        │ subprocess.run()                    │
│                        ▼                                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Call: node interact.js classify "domain.com" true    │  │
│  └─────────────────────┬─────────────────────────────────┘  │
└────────────────────────┼─────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│                  Node.js Blockchain Layer                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  interact.js (Ethers.js + Contract ABI)               │  │
│  │  • Signs transactions with private key                │  │
│  │  • Encodes function calls                             │  │
│  │  • Sends to Ethereum network                          │  │
│  │  • Waits for confirmation                             │  │
│  │  • Decodes events and responses                       │  │
│  └─────────────────────┬─────────────────────────────────┘  │
└────────────────────────┼─────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│              Ethereum Blockchain (Sepolia)                    │
│  Smart Contract: 0x14B9A3Fd9502528a7Bdf7780eE75b387b942b0D3 │
└───────────────────────────────────────────────────────────────┘
```

**Advantages:**
- ✅ **Separation of concerns**: Python = business logic, JS = blockchain
- ✅ **Independent scaling**: Can run multiple Node.js workers
- ✅ **Language-specific strengths**: Python for ML/AI, JS for Web3
- ✅ **Isolated failures**: Blockchain errors don't crash Flask
- ✅ **Easy replacement**: Can swap blockchain layer without touching Python

#### **1.4 Hardhat Ecosystem Integration**

```javascript
// hardhat.config.cjs
module.exports = {
  solidity: "0.8.19",
  networks: {
    sepolia: {
      url: process.env.BLOCKCHAIN_PROVIDER_URL,
      accounts: [process.env.BLOCKCHAIN_PRIVATE_KEY],
    }
  }
};
```

**Why Hardhat?**
- ✅ **Compile Solidity**: `npx hardhat compile`
- ✅ **Deploy contracts**: `node deploy.js`
- ✅ **Testing framework**: Built-in test suite
- ✅ **Local blockchain**: `npx hardhat node`
- ✅ **Debugging**: Stack traces, console.log in Solidity
- ✅ **Contract verification**: Etherscan integration

**Python equivalent?** Brownie (deprecated) or Ape (experimental)

#### **1.5 Real-World Production Pattern**

This architecture is used by major Web3 companies:

```
OpenSea (NFT marketplace):
  Frontend: React.js → Backend: Python (API) → Blockchain: Node.js (Ethers.js)

Uniswap (DEX):
  Frontend: React.js → Backend: GraphQL (Node.js) → Blockchain: Ethers.js

Your project:
  Frontend: Browser Extension → Backend: Flask (Python) → Blockchain: Node.js
```

---

## 2. Role of Private Key & Contract Address in Codebase

### 🔑 Understanding the .env File

```bash
# .env file
CONTRACT_ADDRESS=0x14B9A3Fd9502528a7Bdf7780eE75b387b942b0D3
BLOCKCHAIN_PRIVATE_KEY=abc123def456...
BLOCKCHAIN_PROVIDER_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
```

### 2.1 **CONTRACT_ADDRESS** - The Smart Contract Location

#### **What is it?**
- **Ethereum address** where your smart contract code lives on the blockchain
- **Unique identifier** for your deployed `DomainClassification.sol` contract
- **Permanent**: Once deployed, this address never changes

#### **How it's generated:**

```javascript
// deploy.js
async function deployContract() {
  const contractFactory = new ethers.ContractFactory(
    contractABI,        // Smart contract interface
    contractBytecode,   // Compiled Solidity code
    wallet              // Your account (signs deployment)
  );
  
  const contract = await contractFactory.deploy();
  await contract.waitForDeployment();
  
  const contractAddress = await contract.getAddress();
  // Returns: 0x14B9A3Fd9502528a7Bdf7780eE75b387b942b0D3
}
```

**Deployment creates:**
1. Contract bytecode stored at blockchain address
2. Contract storage (state variables)
3. Immutable code (can't be changed)

#### **Where it's used in codebase:**

**File: interact.js**
```javascript
class DomainClassificationContract {
  constructor() {
    this.contractAddress = process.env.CONTRACT_ADDRESS;
    
    // Connect to the contract at this address
    this.contract = new ethers.Contract(
      this.contractAddress,  // Where to find the contract
      this.contractABI,      // How to talk to it (function signatures)
      this.wallet            // Who is calling (signed with private key)
    );
  }
}
```

**File: backend.py** (indirectly)
```python
# backend.py passes contract address to Node.js
subprocess.run([
    'node', 'blockchain/interact.js', 
    'classify',  # Command
    'domain.com',  # Domain name
    'true',  # Is spam?
    'Phishing detected'  # Reason
])

# interact.js reads CONTRACT_ADDRESS from .env
# Uses it to create contract instance
```

**File: blockchain_integration.py**
```python
def get_blockchain_instance():
    _blockchain_instance.contract_address = os.getenv('CONTRACT_ADDRESS')
    # Used for status checks and reporting
```

#### **What happens if CONTRACT_ADDRESS is wrong?**

```javascript
// Wrong address (contract doesn't exist)
const contract = new ethers.Contract("0xWRONGADDRESS", abi, wallet);

// When you call a function:
await contract.classifyDomain("test.com", true, "Test");
// ❌ Error: "contract call reverted" or "invalid address"
```

---

### 2.2 **BLOCKCHAIN_PRIVATE_KEY** - Your Identity & Signing Power

#### **What is it?**
- **64-character hexadecimal string** (256 bits of randomness)
- **Cryptographic secret** that proves you own an Ethereum account
- **Signing key** for all blockchain transactions

#### **The Public-Private Key Relationship:**

```
Private Key (SECRET):
  abc123def456789... (64 hex chars)
         ↓ Elliptic Curve Cryptography (ECDSA)
Public Key:
  04a1b2c3d4e5f6... (128 hex chars - uncompressed)
         ↓ Keccak-256 Hash → Take last 20 bytes
Ethereum Address (PUBLIC):
  0x5C792FdF1a0aeBd8A6EeC4C5C67e814f1fbE85A4
```

**Analogy:**
- Private Key = Your password (NEVER share)
- Public Address = Your username (safe to share)

#### **How it's used in codebase:**

**File: interact.js**
```javascript
class DomainClassificationContract {
  constructor() {
    // Create wallet from private key
    this.wallet = new ethers.Wallet(
      process.env.BLOCKCHAIN_PRIVATE_KEY,  // Your secret key
      this.provider  // Connection to Ethereum network
    );
    
    // Wallet can now:
    // 1. Sign transactions
    // 2. Pay gas fees (from account balance)
    // 3. Prove ownership when calling contract functions
  }
  
  async classifyDomain(domain, isSpam, reason) {
    // When you call contract function:
    const tx = await this.contract.classifyDomain(domain, isSpam, reason);
    
    // Behind the scenes:
    // 1. Ethers.js creates transaction data
    // 2. Signs it with BLOCKCHAIN_PRIVATE_KEY
    // 3. Sends signed transaction to network
    // 4. Miners verify signature matches wallet.address
    // 5. Execute contract function if valid
  }
}
```

#### **Transaction Signing Process (Deep Dive):**

```javascript
// Step 1: Create unsigned transaction
const unsignedTx = {
  to: "0x14B9A3Fd9502528a7Bdf7780eE75b387b942b0D3",  // Contract address
  data: "0x1234abcd...",  // Encoded function call
  gasLimit: 200000,
  gasPrice: ethers.parseUnits("50", "gwei"),
  nonce: 42,  // Transaction count from your account
  chainId: 11155111  // Sepolia network
};

// Step 2: Sign with private key
const signature = wallet.signTransaction(unsignedTx);
// Uses ECDSA algorithm to create signature
// Signature = sign(unsignedTx, BLOCKCHAIN_PRIVATE_KEY)

// Step 3: Broadcast signed transaction
const signedTx = {
  ...unsignedTx,
  v: signature.v,  // Recovery ID
  r: signature.r,  // Signature component 1
  s: signature.s   // Signature component 2
};

// Network can verify:
// ecrecover(signedTx) == wallet.address
```

#### **Security Implications:**

**If private key is leaked:**
```python
# Attacker can:
attacker_wallet = ethers.Wallet("YOUR_LEAKED_PRIVATE_KEY")

# 1. Steal all ETH from your account
await attacker_wallet.sendTransaction({
    to: "attacker_address",
    value: ethers.parseEther("all your ETH")
})

# 2. Submit fake domain classifications
await contract.classifyDomain("google.com", True, "Fake spam report")

# 3. Drain gas fees by spamming transactions
```

**Protection in code:**
```python
# backend.py - Private key NEVER exposed to API
# .env file in .gitignore
# Only Node.js subprocess has access
```

---

### 2.3 **BLOCKCHAIN_PROVIDER_URL** - Gateway to Ethereum

#### **What is it?**
- **RPC endpoint** (Remote Procedure Call) to communicate with Ethereum network
- **API gateway** to read/write blockchain data

#### **How it works:**

```javascript
const provider = new ethers.JsonRpcProvider(
  "https://sepolia.infura.io/v3/YOUR_PROJECT_ID"
);

// Provider can:
await provider.getBlockNumber();  // Read blockchain state
await provider.getBalance(address);  // Check account balance
await provider.sendTransaction(signedTx);  // Submit transaction
await provider.getTransactionReceipt(txHash);  // Check if confirmed
```

**Architecture:**

```
Your Code (interact.js)
         ↓ HTTPS Request
Infura API (https://sepolia.infura.io)
         ↓ Connects to
Sepolia Ethereum Network (thousands of nodes)
         ↓ Stores data in
Blockchain (immutable ledger)
```

#### **Why Infura/Alchemy instead of running your own node?**

**Running your own Ethereum node:**
```bash
# Requires:
- 500GB+ disk space (full node)
- 16GB RAM
- 24/7 uptime
- Constant syncing with network
- Maintenance and updates
```

**Using Infura:**
```bash
# Requires:
- Free API key
- 100,000 requests/day (free tier)
- Instant access
- No maintenance
```

---

### 2.4 Complete Flow: How They Work Together

```javascript
// STEP 1: Initialize connection
const provider = new ethers.JsonRpcProvider(
  process.env.BLOCKCHAIN_PROVIDER_URL  // Gateway to blockchain
);

// STEP 2: Create wallet with private key
const wallet = new ethers.Wallet(
  process.env.BLOCKCHAIN_PRIVATE_KEY,  // Your identity
  provider  // Connected to network
);

// STEP 3: Connect to smart contract
const contract = new ethers.Contract(
  process.env.CONTRACT_ADDRESS,  // Where the code lives
  contractABI,  // How to talk to it
  wallet  // Who is calling (signed with private key)
);

// STEP 4: Call contract function
const tx = await contract.classifyDomain("example.com", true, "Phishing");
// What happens:
// 1. Ethers.js encodes function call into transaction data
// 2. Signs transaction with BLOCKCHAIN_PRIVATE_KEY
// 3. Sends via BLOCKCHAIN_PROVIDER_URL to network
// 4. Contract at CONTRACT_ADDRESS executes function
// 5. State changes stored on blockchain

// STEP 5: Wait for confirmation
const receipt = await tx.wait();
// Transaction included in block on Sepolia network
```

---

## 3. Complete Low-Level Workflow Diagram

### 🔄 End-to-End Flow: From Email Click to Blockchain Storage

---

### **3.1 Initial Setup Phase (One-Time)**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DEVELOPER SETUP (ONE-TIME)                        │
└─────────────────────────────────────────────────────────────────────┘

1. Install Dependencies
   ├── Backend: pip install -r requirements.txt
   ├── Blockchain: cd blockchain && npm install
   └── Extension: Load in Chrome

2. Create .env File
   ├── GEMINI_API_KEY=...
   ├── EXT_API_KEY=... (optional)
   ├── BLOCKCHAIN_PROVIDER_URL=https://sepolia.infura.io/v3/...
   ├── BLOCKCHAIN_PRIVATE_KEY=... (get from MetaMask)
   └── BLOCKCHAIN_NETWORK_ID=11155111

3. Deploy Smart Contract
   ├── cd blockchain
   ├── npx hardhat compile
   │   └── Creates: artifacts/contracts/DomainReputation.sol/DomainClassification.json
   ├── node deploy.js
   │   ├── Reads: DomainClassification.json (ABI + bytecode)
   │   ├── Creates: ContractFactory with ABI + bytecode
   │   ├── wallet.deploy(ContractFactory)
   │   ├── Signs deployment transaction with BLOCKCHAIN_PRIVATE_KEY
   │   ├── Sends via BLOCKCHAIN_PROVIDER_URL to Sepolia network
   │   ├── Miners include transaction in block
   │   ├── Contract code stored at new address
   │   └── Returns: CONTRACT_ADDRESS (e.g., 0x14B9A...)
   └── Update .env with CONTRACT_ADDRESS

4. Start Backend
   python backend.py
   ├── Loads .env variables
   ├── Initializes models:
   │   ├── embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
   │   ├── content_model = pickle.load('email_log_reg_embed_model.pkl')
   │   ├── url_model = pickle.load('random_forest_url_model.pkl')
   │   └── llm_model = genai.GenerativeModel('gemini-2.5-flash')
   ├── Connects to blockchain:
   │   ├── subprocess.run(['node', 'interact.js', 'stats'])
   │   └── Logs: ✅ Connected to blockchain
   └── Starts Flask server on http://127.0.0.1:8080

5. Load Extension
   ├── Open chrome://extensions/
   ├── Enable Developer Mode
   ├── Click "Load unpacked"
   ├── Select: phish-analyzer-extension/
   └── Extension loads:
       ├── background.js (service worker)
       ├── content_script.js (Gmail injection)
       └── popup.js (settings UI)
```

---

### **3.2 User Opens Email (Email Analysis Flow)**

```
┌─────────────────────────────────────────────────────────────────────┐
│          PHASE 1: USER OPENS EMAIL IN GMAIL                          │
└─────────────────────────────────────────────────────────────────────┘

Step 1: Gmail Page Load
  User navigates to Gmail
         ↓
  content_script.js injected by Chrome
         ↓
  MutationObserver watches for DOM changes
         ↓
  Detects: div[data-message-id] (email opened)

Step 2: Create "Analyze" Button
  content_script.js:
  ├── const analyzeBtn = document.createElement('button')
  ├── analyzeBtn.textContent = 'Analyze'
  ├── analyzeBtn.onclick = () => analyzeEmail()
  └── Insert button into Gmail toolbar

Step 3: User Clicks "Analyze"
  analyzeEmail() function triggered
         ↓
  Extract email data from DOM:
  ├── sender = document.querySelector('[email]').getAttribute('email')
  │   └── Example: "support@figma.com"
  ├── subject = document.querySelector('[data-subject]').innerText
  │   └── Example: "We've updated our Terms of Service"
  ├── body = document.querySelector('[data-message-body]').innerText
  │   └── Example: "Dear user, click here to review..."
  └── urls = extractUrls(body)
      └── Regex: /https?:\/\/[^\s<>"{}|\\^`\[\]]+/g
      └── Example: ["https://click.figma.com/accept"]

Step 4: Show Loading Indicator
  content_script.js:
  ├── showOverlay({ loading: true })
  ├── Create panel div with:
  │   ├── Spinner animation
  │   └── "Analyzing email..." text
  └── Insert into Gmail DOM

Step 5: Send to Backend
  const response = await fetch('http://127.0.0.1:8080/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': apiKey  // From chrome.storage
    },
    body: JSON.stringify({
      sender: "support@figma.com",
      subject: "We've updated our Terms of Service",
      body: "Dear user, click here...",
      urls: ["https://click.figma.com/accept"]
    })
  });
```

---

### **3.3 Backend Analysis Pipeline**

```
┌─────────────────────────────────────────────────────────────────────┐
│      PHASE 2: BACKEND RECEIVES REQUEST & ANALYZES EMAIL              │
└─────────────────────────────────────────────────────────────────────┘

Step 1: Flask Receives Request
  backend.py @app.route("/analyze", methods=["POST"])
         ↓
  API key validation (if EXT_API_KEY set):
  ├── provided_key = request.headers.get("x-api-key")
  ├── if provided_key != EXT_API_KEY:
  │   └── return 403 Forbidden
  └── Continue if valid

Step 2: Extract Data from Request
  data = request.json
  ├── sender = data.get("sender")  # "support@figma.com"
  ├── subject = data.get("subject")  # "We've updated..."
  ├── body = data.get("body")  # Email content
  └── urls = data.get("urls", [])  # ["https://click.figma.com/accept"]

Step 3: Call Analysis Function
  final_risk, details = compute_final_risk(
    body=body,
    sender=sender,
    subject=subject
  )
```

---

### **3.4 Blockchain-First Analysis (Most Important!)**

```
┌─────────────────────────────────────────────────────────────────────┐
│   PHASE 3: BLOCKCHAIN-FIRST DOMAIN REPUTATION CHECK (FAST PATH)     │
└─────────────────────────────────────────────────────────────────────┘

Step 1: Extract Domains
  utils.py → compute_final_risk()
  ├── Extract URLs from content:
  │   ├── full_content = f"{subject} {body}"
  │   ├── url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
  │   ├── urls = re.findall(url_pattern, full_content)
  │   └── Found: ["https://click.figma.com/accept"]
  │
  ├── Extract domains from URLs:
  │   ├── For each URL:
  │   │   ├── parsed = urlparse(url)
  │   │   ├── domain = parsed.netloc  # "click.figma.com"
  │   │   └── if domain.startswith('www.'): domain = domain[4:]
  │   └── domains = ["click.figma.com"]
  │
  └── Add sender domain:
      ├── sender = "support@figma.com"
      ├── sender_domain = sender.split('@')[1]  # "figma.com"
      └── domains = ["click.figma.com", "figma.com"]

Step 2: Query Blockchain for EACH Domain
  For domain in ["click.figma.com", "figma.com"]:
  
    ┌─────────────────────────────────────────────────┐
    │  Blockchain Query for: figma.com                 │
    └─────────────────────────────────────────────────┘
    
    2.1: Python calls Node.js subprocess
         utils.py → get_blockchain_domain_reputation(domain)
         ├── script_path = "blockchain/interact.js"
         └── result = subprocess.run(
               ['node', script_path, 'query', domain],
               capture_output=True,
               text=True,
               timeout=10,
               encoding='utf-8'  # ✅ Fixes Unicode errors
             )
    
    2.2: Node.js script initializes
         interact.js → args = ['query', 'figma.com']
         ├── Load .env variables:
         │   ├── CONTRACT_ADDRESS
         │   ├── BLOCKCHAIN_PRIVATE_KEY
         │   └── BLOCKCHAIN_PROVIDER_URL
         │
         ├── Create provider:
         │   ├── provider = new ethers.JsonRpcProvider(PROVIDER_URL)
         │   └── Establishes HTTPS connection to Infura
         │
         ├── Create wallet:
         │   ├── wallet = new ethers.Wallet(PRIVATE_KEY, provider)
         │   └── Derives public address from private key
         │
         └── Create contract instance:
             ├── contract = new ethers.Contract(
             │     CONTRACT_ADDRESS,  # Where contract lives
             │     contractABI,       # Function signatures
             │     wallet             # Who is calling
             │   )
             └── Contract ready to call
    
    2.3: Call smart contract function
         interact.js → contract.getDomainClassification("figma.com")
         
         ├── Ethers.js encodes function call:
         │   ├── functionSelector = keccak256("getDomainClassification(string)")[:4]
         │   ├── encodedParams = abi.encode(["figma.com"])
         │   └── callData = functionSelector + encodedParams
         │
         ├── Create eth_call request:
         │   ├── {
         │   │   "jsonrpc": "2.0",
         │   │   "method": "eth_call",
         │   │   "params": [{
         │   │     "to": "0x14B9A3Fd9502528a7Bdf7780eE75b387b942b0D3",
         │   │     "data": callData
         │   │   }, "latest"],
         │   │   "id": 1
         │   │ }
         │   └── This is a READ-ONLY call (no transaction, no gas)
         │
         └── Send HTTPS request to Infura
    
    2.4: Infura processes request
         ├── Receives eth_call request
         ├── Forwards to Sepolia network nodes
         └── Nodes execute contract code:
             ├── Load contract bytecode from CONTRACT_ADDRESS
             ├── Execute getDomainClassification(domain) function
             ├── Read from contract storage:
             │   ├── mapping(string => DomainInfo) domains;
             │   └── domains["figma.com"] = ?
             └── Return result
    
    2.5: Smart contract executes
         DomainReputation.sol:
         
         function getDomainClassification(string memory _domain) 
           external view returns (
             bool exists,
             bool isSpam,
             uint256 timestamp,
             address reporter,
             string memory reason
           ) 
         {
           DomainInfo storage info = domains[_domain];
           
           if (info.reporter == address(0)) {
             // Domain not found in mapping
             return (false, false, 0, address(0), "");
           }
           
           // Domain found, return its data
           return (
             true,
             info.isSpam,        // true = spam, false = ham
             info.timestamp,     // When classified
             info.reporter,      // Who classified it
             info.reason         // Why classified
           );
         }
    
    2.6: Result returned through layers
         Smart Contract
              ↓ (exists=true, isSpam=false, timestamp=1697280000, ...)
         Ethereum Node
              ↓ RLP encoded response
         Infura API
              ↓ JSON-RPC response
         Ethers.js provider.call()
              ↓ Decoded using ABI
         interact.js
              ↓ Parse and format
         
         if (result && result.exists) {
           console.log(result.isSpam ? "SPAM" : "HAM");
           // Prints: HAM
         } else {
           console.log("UNKNOWN");
         }
    
    2.7: Python receives stdout
         utils.py:
         ├── stdout = "🔍 Querying domain: figma.com\n📊 Domain found:\nHAM"
         ├── lines = stdout.strip().split('\n')
         ├── classification = lines[-1]  # "HAM"
         │
         └── return {
               "exists": True,
               "reputation_score": 90,  # HAM = high score
               "consensus": "ham",
               "spam_votes": 0,
               "ham_votes": 1,
               "total_reports": 1
             }

Step 3: Calculate Blockchain Weight
  If ANY domain found in blockchain:
  ├── blockchain_weight = 0.7  # 70% weight!
  └── Skip expensive LLM analysis
  
  If NO domains found:
  ├── blockchain_weight = 0.0
  └── Run full ML + LLM analysis

Step 4: Compute Risk Score (Blockchain Found)
  
  ┌─────────────────────────────────────────────────────┐
  │  SCENARIO A: Domain Found in Blockchain (figma.com) │
  └─────────────────────────────────────────────────────┘
  
  weights = {
    'content': 0.10,    # ML content analysis
    'url': 0.10,        # ML URL analysis  
    'llm': 0.10,        # LLM (minimal weight)
    'blockchain': 0.70  # BLOCKCHAIN DOMINANT!
  }
  
  # Content ML (always runs, fast)
  content_prob = 0.017  # 1.7% risk
  
  # URL ML (always runs, fast)
  url_prob = 0.500  # 50% risk (neutral)
  
  # LLM (SKIPPED!)
  llm_score = 0.5  # Not computed, use neutral
  llm_reason = "Skipped - using blockchain consensus"
  llm_actions = ["Skipped - using blockchain consensus"]
  
  # Blockchain
  blockchain_score = 0.0  # figma.com is HAM (legitimate)
  
  # Final calculation
  final_risk = (
    0.10 * 0.017 +  # content
    0.10 * 0.500 +  # url
    0.10 * 0.500 +  # llm (neutral)
    0.70 * 0.000    # blockchain (HAM = 0% risk)
  )
  final_risk = 0.001 + 0.05 + 0.05 + 0.0 = 0.101
  final_risk = 10.1% ≈ 10% risk → SAFE
  
  ⏱️  Analysis time: ~1-2 seconds (blockchain query only!)
```

---

### **3.5 Full ML+LLM Analysis (Blockchain Not Found)**

```
┌─────────────────────────────────────────────────────────────────────┐
│  SCENARIO B: Domain NOT in Blockchain (example-unknown-site.com)    │
└─────────────────────────────────────────────────────────────────────┘

Step 1: ML Content Analysis
  utils.py → analyze_content_with_ml(body)
  
  ├── embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
  ├── embedding = embedding_model.encode([body])
  │   └── Converts text to 384-dimensional vector
  │       Example: [0.123, -0.456, 0.789, ...]
  │
  ├── content_model = LogisticRegression (pre-trained)
  ├── proba = content_model.predict_proba(embedding)[0]
  │   └── [0.921, 0.079]  # [ham_prob, spam_prob]
  │
  ├── spam_prob = proba[1] = 0.079  # 7.9% spam
  ├── confidence = max(proba) = 0.921  # 92.1% confident
  └── return (0.079, 0.921)

Step 2: ML URL Analysis
  utils.py → analyze_urls_with_ml(urls)
  
  For each URL in ["https://example-unknown-site.com/offer"]:
  
  ├── Extract features:
  │   ├── len(url) = 45
  │   ├── domain_length = 25
  │   ├── num_dots = 1
  │   ├── num_hyphens = 2
  │   ├── has_ip = 0
  │   ├── has_https = 1
  │   └── ... (50 features total)
  │
  ├── url_model = RandomForestClassifier (pre-trained)
  ├── features_array = np.array(features).reshape(1, -1)
  ├── score = url_model.predict_proba(features_array)[0][1]
  │   └── 0.650  # 65% spam probability
  └── return 0.650

Step 3: LLM Analysis (Google Gemini)
  utils.py → analyze_with_llm(body, sender, subject)
  
  3.1: Construct prompt
       prompt = f"""
       Analyze this email for phishing indicators. 
       Provide a risk score from 0.0 (safe) to 1.0 (definitely phishing).
       
       Subject: {subject}
       From: {sender}
       Content: {body[:1000]}...
       
       Consider:
       1. Urgency and fear tactics
       2. Suspicious links or attachments
       3. Poor grammar/spelling
       4. Sender authenticity
       5. Request for sensitive information
       
       Respond with:
       RISK_SCORE: [0.0-1.0]
       REASON: [brief explanation]
       CONFIDENCE: [0.0-1.0]
       """
  
  3.2: Call Gemini API
       ├── import google.generativeai as genai
       ├── genai.configure(api_key=GEMINI_API_KEY)
       ├── llm_model = genai.GenerativeModel('gemini-2.5-flash')
       │
       └── response = llm_model.generate_content(prompt)
           ├── Sends HTTPS POST to:
           │   └── https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent
           ├── Request body:
           │   {
           │     "contents": [{"parts": [{"text": prompt}]}],
           │     "generationConfig": {
           │       "temperature": 0.7,
           │       "maxOutputTokens": 1024
           │     }
           │   }
           └── Gemini processes (2-5 seconds)
  
  3.3: Gemini Response
       {
         "candidates": [{
           "content": {
             "parts": [{
               "text": "RISK_SCORE: 0.75\nREASON: Email contains urgency tactics ('Act now!'), suspicious shortened URL, and requests personal information.\nCONFIDENCE: 0.85"
             }]
           },
           "finishReason": "STOP"
         }]
       }
  
  3.4: Parse response
       text = response.text
       # "RISK_SCORE: 0.75\nREASON: ...\nCONFIDENCE: 0.85"
       
       risk_score = 0.75
       reason = "Email contains urgency tactics..."
       confidence = 0.85
       
       return (0.75, reason, 0.85)

Step 4: Combine All Scores
  utils.py → compute_final_risk()
  
  weights = {
    'content': 0.30,
    'url': 0.20,
    'llm': 0.50,
    'blockchain': 0.00  # Not found
  }
  
  final_risk = (
    0.30 * 0.079 +  # Content ML
    0.20 * 0.650 +  # URL ML
    0.50 * 0.750 +  # LLM
    0.00 * 0.500    # Blockchain (not used)
  )
  final_risk = 0.024 + 0.130 + 0.375 + 0.0 = 0.529
  final_risk = 52.9% risk → SUSPICIOUS
  
  ⏱️  Analysis time: ~5-8 seconds (LLM is slow)
```

---

### **3.6 Auto-Reporting to Blockchain (High Confidence Results)**

```
┌─────────────────────────────────────────────────────────────────────┐
│   PHASE 4: AUTO-REPORT HIGH-CONFIDENCE RESULTS TO BLOCKCHAIN        │
└─────────────────────────────────────────────────────────────────────┘

Step 1: Check Auto-Report Criteria
  backend.py:
  
  confidence = 0.85  # From analysis
  AUTO_REPORT_ENABLED = True
  MIN_CONFIDENCE_THRESHOLD = 0.8
  
  if confidence >= MIN_CONFIDENCE_THRESHOLD and AUTO_REPORT_ENABLED:
    # Automatically store to blockchain
    for domain in domains:
      is_spam = (final_risk > 0.5)
      store_classification_to_blockchain(
        domain=domain,
        is_spam=is_spam,
        reason="Auto-reported by ML/AI analysis"
      )

Step 2: Store to Blockchain
  utils.py → store_classification_to_blockchain()
  
  2.1: Call Node.js script
       classification = 'true' if is_spam else 'false'
       
       result = subprocess.run(
         [
           'node',
           'blockchain/interact.js',
           'classify',
           'example-unknown-site.com',  # Domain
           'true',                       # Is spam
           'Auto-reported by ML/AI analysis'  # Reason
         ],
         capture_output=True,
         text=True,
         timeout=60,  # Increased for blockchain confirmation
         encoding='utf-8'
       )
  
  2.2: Node.js receives command
       interact.js:
       ├── args = ['classify', 'example-unknown-site.com', 'true', 'Auto-reported...']
       ├── domain = args[1]
       ├── isSpam = (args[2] === 'true')
       └── reason = args[3]
  
  2.3: Call classifyDomain with retry
       contract.classifyDomain(domain, isSpam, reason, maxRetries=3)
       
       ┌──────────────────────────────────────────────────┐
       │  Attempt 1: Submit Transaction                   │
       └──────────────────────────────────────────────────┘
       
       ├── Check cooldown:
       │   ├── canSubmit = await contract.canUserSubmit(wallet.address)
       │   └── If cooldown active: wait or retry later
       │
       ├── Encode function call:
       │   ├── functionFragment = contract.interface.getFunction('classifyDomain')
       │   ├── encodedData = contract.interface.encodeFunctionData(
       │   │     'classifyDomain',
       │   │     ['example-unknown-site.com', true, 'Auto-reported...']
       │   │   )
       │   └── data = "0x1234abcd..." (hex encoded)
       │
       ├── Create transaction:
       │   ├── const tx = await contract.classifyDomain(domain, isSpam, reason)
       │   │
       │   │   Behind the scenes:
       │   │   ├── Get current gas price:
       │   │   │   └── gasPrice = await provider.getFeeData()
       │   │   │
       │   │   ├── Get nonce (transaction count):
       │   │   │   └── nonce = await provider.getTransactionCount(wallet.address)
       │   │   │
       │   │   ├── Estimate gas:
       │   │   │   └── gasLimit = await contract.estimateGas.classifyDomain(...)
       │   │   │
       │   │   ├── Build unsigned transaction:
       │   │   │   {
       │   │   │     to: "0x14B9A3Fd9502528a7Bdf7780eE75b387b942b0D3",
       │   │   │     data: encodedData,
       │   │   │     gasLimit: 150000,
       │   │   │     maxFeePerGas: "50 gwei",
       │   │   │     maxPriorityFeePerGas: "2 gwei",
       │   │   │     nonce: 42,
       │   │   │     chainId: 11155111
       │   │   │   }
       │   │   │
       │   │   ├── Sign transaction:
       │   │   │   ├── txHash = keccak256(serialize(unsignedTx))
       │   │   │   ├── signature = sign(txHash, BLOCKCHAIN_PRIVATE_KEY)
       │   │   │   └── signedTx = { ...unsignedTx, ...signature }
       │   │   │
       │   │   └── Broadcast transaction:
       │   │       ├── provider.sendTransaction(signedTx)
       │   │       ├── POST to Infura API:
       │   │       │   {
       │   │       │     "jsonrpc": "2.0",
       │   │       │     "method": "eth_sendRawTransaction",
       │   │       │     "params": ["0x...signedTxData"],
       │   │       │     "id": 1
       │   │       │   }
       │   │       └── Infura forwards to Sepolia network
       │   │
       │   └── tx = { hash: "0xabc123...", ... }
       │
       └── console.log(`⏳ Transaction submitted: ${tx.hash}`)
  
  2.4: Wait for confirmation
       const receipt = await tx.wait()
       
       ├── Ethers.js polls Infura every 2 seconds:
       │   ├── eth_getTransactionReceipt(txHash)
       │   └── Null while pending
       │
       ├── Sepolia miners:
       │   ├── Pick up transaction from mempool
       │   ├── Validate signature
       │   ├── Execute smart contract function:
       │   │   ├── Load contract bytecode
       │   │   ├── Execute classifyDomain():
       │   │   │   {
       │   │   │     require(block.timestamp >= lastSubmissionTime[msg.sender] + submissionCooldown);
       │   │   │     domains[_domain] = DomainInfo({
       │   │   │       isSpam: true,
       │   │   │       timestamp: block.timestamp,
       │   │   │       reporter: msg.sender,
       │   │   │       reason: "Auto-reported..."
       │   │   │     });
       │   │   │     lastSubmissionTime[msg.sender] = block.timestamp;
       │   │   │     emit DomainClassified(_domain, true, msg.sender, block.timestamp);
       │   │   │   }
       │   │   └── State changes written to blockchain
       │   ├── Include transaction in block
       │   └── Block propagated to network
       │
       └── receipt = {
             blockNumber: 9411250,
             blockHash: "0xdef456...",
             transactionHash: "0xabc123...",
             gasUsed: 125000,
             status: 1  // Success
           }
  
  2.5: Return success
       console.log(`✅ Transaction confirmed in block: ${receipt.blockNumber}`)
       
       return {
         success: true,
         txHash: tx.hash,
         blockNumber: receipt.blockNumber
       }
  
  2.6: Python receives result
       utils.py
       ├── stdout = "✅ Transaction confirmed in block: 9411250"
       ├── if result.returncode == 0:
       │   └── logger.info(f"Successfully stored {domain} as {classification}")
       └── return (True, f"Domain {domain} stored as {classification}")
Searched codebase for "1. Why are we using JS for interacting with the blockchain contract?
2. WE have our priv key and contrct addrss in .env, what roles do they play in #codebase ?
3. I do not want a high level worflow diagram, but instead low levle workflow diagram consisting of every single steps from the start to end.

I need answers for all these questions in a very detailed manner. You can even create a md for this", 17 results

I'll create a comprehensive detailed document answering all your questions about blockchain integration, private keys, and the complete low-level workflow.

```markdown
# 🔐 Blockchain Integration Deep Dive - Complete Technical Analysis

## Table of Contents
1. [Why JavaScript for Blockchain?](#1-why-javascript-for-blockchain)
2. [Role of Private Key & Contract Address](#2-role-of-private-key--contract-address)
3. [Complete Low-Level Workflow](#3-complete-low-level-workflow)

---

## 1. Why JavaScript for Blockchain Integration?

### 🤔 The Question
You're using **Python** for the backend (Flask), but **JavaScript (Node.js)** for blockchain interactions. Why this design choice?

### ✅ The Answer: Technical & Practical Reasons

#### **1.1 Ethers.js is the Industry Standard**

```javascript
// JavaScript (Node.js) with Ethers.js
import { ethers } from "ethers";

const provider = new ethers.JsonRpcProvider("https://sepolia.infura.io/v3/...");
const wallet = new ethers.Wallet(privateKey, provider);
const contract = new ethers.Contract(address, abi, wallet);

// Clean, mature, well-documented
const tx = await contract.classifyDomain("example.com", true, "Phishing");
await tx.wait(); // Wait for confirmation
```

**Why Ethers.js?**
- ✅ **Battle-tested**: Used by 90% of Web3 projects
- ✅ **Active development**: Weekly updates, bug fixes
- ✅ **Comprehensive**: Handles all Ethereum operations (signing, encoding, events)
- ✅ **TypeScript support**: Type safety for complex operations
- ✅ **Event handling**: Easy to listen to contract events
- ✅ **Transaction management**: Automatic nonce, gas estimation

#### **1.2 Python Blockchain Libraries Are Immature**

```python
# Python with Web3.py (alternative)
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://sepolia.infura.io/v3/..."))
contract = w3.eth.contract(address=address, abi=abi)

# More verbose, less intuitive
tx_hash = contract.functions.classifyDomain("example.com", True, "Phishing").transact({
    'from': account,
    'gas': 200000,
    'gasPrice': w3.toWei('50', 'gwei')
})
# Manual transaction receipt handling
receipt = w3.eth.waitForTransactionReceipt(tx_hash)
```

**Problems with Web3.py:**
- ❌ **Less documentation**: Smaller community, fewer examples
- ❌ **More boilerplate**: Requires manual gas estimation, nonce management
- ❌ **Event parsing complexity**: Harder to decode indexed parameters
- ❌ **Slower updates**: Lags behind Ethereum protocol changes
- ❌ **Type conversion issues**: Python types ↔ Solidity types require manual handling

#### **1.3 Subprocess Architecture Benefits**

Your current architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                      Python Backend                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Flask API  (handles HTTP, ML, analysis logic)        │  │
│  └─────────────────────┬─────────────────────────────────┘  │
│                        │ subprocess.run()                    │
│                        ▼                                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Call: node interact.js classify "domain.com" true    │  │
│  └─────────────────────┬─────────────────────────────────┘  │
└────────────────────────┼─────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│                  Node.js Blockchain Layer                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  interact.js (Ethers.js + Contract ABI)               │  │
│  │  • Signs transactions with private key                │  │
│  │  • Encodes function calls                             │  │
│  │  • Sends to Ethereum network                          │  │
│  │  • Waits for confirmation                             │  │
│  │  • Decodes events and responses                       │  │
│  └─────────────────────┬─────────────────────────────────┘  │
└────────────────────────┼─────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│              Ethereum Blockchain (Sepolia)                    │
│  Smart Contract: 0x14B9A3Fd9502528a7Bdf7780eE75b387b942b0D3 │
└───────────────────────────────────────────────────────────────┘
```

**Advantages:**
- ✅ **Separation of concerns**: Python = business logic, JS = blockchain
- ✅ **Independent scaling**: Can run multiple Node.js workers
- ✅ **Language-specific strengths**: Python for ML/AI, JS for Web3
- ✅ **Isolated failures**: Blockchain errors don't crash Flask
- ✅ **Easy replacement**: Can swap blockchain layer without touching Python

#### **1.4 Hardhat Ecosystem Integration**

```javascript
// hardhat.config.cjs
module.exports = {
  solidity: "0.8.19",
  networks: {
    sepolia: {
      url: process.env.BLOCKCHAIN_PROVIDER_URL,
      accounts: [process.env.BLOCKCHAIN_PRIVATE_KEY],
    }
  }
};
```

**Why Hardhat?**
- ✅ **Compile Solidity**: `npx hardhat compile`
- ✅ **Deploy contracts**: `node deploy.js`
- ✅ **Testing framework**: Built-in test suite
- ✅ **Local blockchain**: `npx hardhat node`
- ✅ **Debugging**: Stack traces, console.log in Solidity
- ✅ **Contract verification**: Etherscan integration

**Python equivalent?** Brownie (deprecated) or Ape (experimental)

#### **1.5 Real-World Production Pattern**

This architecture is used by major Web3 companies:

```
OpenSea (NFT marketplace):
  Frontend: React.js → Backend: Python (API) → Blockchain: Node.js (Ethers.js)

Uniswap (DEX):
  Frontend: React.js → Backend: GraphQL (Node.js) → Blockchain: Ethers.js

Your project:
  Frontend: Browser Extension → Backend: Flask (Python) → Blockchain: Node.js
```

---

## 2. Role of Private Key & Contract Address in Codebase

### 🔑 Understanding the .env File

```bash
# .env file
CONTRACT_ADDRESS=0x14B9A3Fd9502528a7Bdf7780eE75b387b942b0D3
BLOCKCHAIN_PRIVATE_KEY=abc123def456...
BLOCKCHAIN_PROVIDER_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
```

### 2.1 **CONTRACT_ADDRESS** - The Smart Contract Location

#### **What is it?**
- **Ethereum address** where your smart contract code lives on the blockchain
- **Unique identifier** for your deployed `DomainClassification.sol` contract
- **Permanent**: Once deployed, this address never changes

#### **How it's generated:**

```javascript
// deploy.js
async function deployContract() {
  const contractFactory = new ethers.ContractFactory(
    contractABI,        // Smart contract interface
    contractBytecode,   // Compiled Solidity code
    wallet              // Your account (signs deployment)
  );
  
  const contract = await contractFactory.deploy();
  await contract.waitForDeployment();
  
  const contractAddress = await contract.getAddress();
  // Returns: 0x14B9A3Fd9502528a7Bdf7780eE75b387b942b0D3
}
```

**Deployment creates:**
1. Contract bytecode stored at blockchain address
2. Contract storage (state variables)
3. Immutable code (can't be changed)

#### **Where it's used in codebase:**

**File: interact.js**
```javascript
class DomainClassificationContract {
  constructor() {
    this.contractAddress = process.env.CONTRACT_ADDRESS;
    
    // Connect to the contract at this address
    this.contract = new ethers.Contract(
      this.contractAddress,  // Where to find the contract
      this.contractABI,      // How to talk to it (function signatures)
      this.wallet            // Who is calling (signed with private key)
    );
  }
}
```

**File: backend.py** (indirectly)
```python
# backend.py passes contract address to Node.js
subprocess.run([
    'node', 'blockchain/interact.js', 
    'classify',  # Command
    'domain.com',  # Domain name
    'true',  # Is spam?
    'Phishing detected'  # Reason
])

# interact.js reads CONTRACT_ADDRESS from .env
# Uses it to create contract instance
```

**File: blockchain_integration.py**
```python
def get_blockchain_instance():
    _blockchain_instance.contract_address = os.getenv('CONTRACT_ADDRESS')
    # Used for status checks and reporting
```

#### **What happens if CONTRACT_ADDRESS is wrong?**

```javascript
// Wrong address (contract doesn't exist)
const contract = new ethers.Contract("0xWRONGADDRESS", abi, wallet);

// When you call a function:
await contract.classifyDomain("test.com", true, "Test");
// ❌ Error: "contract call reverted" or "invalid address"
```

---

### 2.2 **BLOCKCHAIN_PRIVATE_KEY** - Your Identity & Signing Power

#### **What is it?**
- **64-character hexadecimal string** (256 bits of randomness)
- **Cryptographic secret** that proves you own an Ethereum account
- **Signing key** for all blockchain transactions

#### **The Public-Private Key Relationship:**

```
Private Key (SECRET):
  abc123def456789... (64 hex chars)
         ↓ Elliptic Curve Cryptography (ECDSA)
Public Key:
  04a1b2c3d4e5f6... (128 hex chars - uncompressed)
         ↓ Keccak-256 Hash → Take last 20 bytes
Ethereum Address (PUBLIC):
  0x5C792FdF1a0aeBd8A6EeC4C5C67e814f1fbE85A4
```

**Analogy:**
- Private Key = Your password (NEVER share)
- Public Address = Your username (safe to share)

#### **How it's used in codebase:**

**File: interact.js**
```javascript
class DomainClassificationContract {
  constructor() {
    // Create wallet from private key
    this.wallet = new ethers.Wallet(
      process.env.BLOCKCHAIN_PRIVATE_KEY,  // Your secret key
      this.provider  // Connection to Ethereum network
    );
    
    // Wallet can now:
    // 1. Sign transactions
    // 2. Pay gas fees (from account balance)
    // 3. Prove ownership when calling contract functions
  }
  
  async classifyDomain(domain, isSpam, reason) {
    // When you call contract function:
    const tx = await this.contract.classifyDomain(domain, isSpam, reason);
    
    // Behind the scenes:
    // 1. Ethers.js creates transaction data
    // 2. Signs it with BLOCKCHAIN_PRIVATE_KEY
    // 3. Sends signed transaction to network
    // 4. Miners verify signature matches wallet.address
    // 5. Execute contract function if valid
  }
}
```

#### **Transaction Signing Process (Deep Dive):**

```javascript
// Step 1: Create unsigned transaction
const unsignedTx = {
  to: "0x14B9A3Fd9502528a7Bdf7780eE75b387b942b0D3",  // Contract address
  data: "0x1234abcd...",  // Encoded function call
  gasLimit: 200000,
  gasPrice: ethers.parseUnits("50", "gwei"),
  nonce: 42,  // Transaction count from your account
  chainId: 11155111  // Sepolia network
};

// Step 2: Sign with private key
const signature = wallet.signTransaction(unsignedTx);
// Uses ECDSA algorithm to create signature
// Signature = sign(unsignedTx, BLOCKCHAIN_PRIVATE_KEY)

// Step 3: Broadcast signed transaction
const signedTx = {
  ...unsignedTx,
  v: signature.v,  // Recovery ID
  r: signature.r,  // Signature component 1
  s: signature.s   // Signature component 2
};

// Network can verify:
// ecrecover(signedTx) == wallet.address
```

#### **Security Implications:**

**If private key is leaked:**
```python
# Attacker can:
attacker_wallet = ethers.Wallet("YOUR_LEAKED_PRIVATE_KEY")

# 1. Steal all ETH from your account
await attacker_wallet.sendTransaction({
    to: "attacker_address",
    value: ethers.parseEther("all your ETH")
})

# 2. Submit fake domain classifications
await contract.classifyDomain("google.com", True, "Fake spam report")

# 3. Drain gas fees by spamming transactions
```

**Protection in code:**
```python
# backend.py - Private key NEVER exposed to API
# .env file in .gitignore
# Only Node.js subprocess has access
```

---

### 2.3 **BLOCKCHAIN_PROVIDER_URL** - Gateway to Ethereum

#### **What is it?**
- **RPC endpoint** (Remote Procedure Call) to communicate with Ethereum network
- **API gateway** to read/write blockchain data

#### **How it works:**

```javascript
const provider = new ethers.JsonRpcProvider(
  "https://sepolia.infura.io/v3/YOUR_PROJECT_ID"
);

// Provider can:
await provider.getBlockNumber();  // Read blockchain state
await provider.getBalance(address);  // Check account balance
await provider.sendTransaction(signedTx);  // Submit transaction
await provider.getTransactionReceipt(txHash);  // Check if confirmed
```

**Architecture:**

```
Your Code (interact.js)
         ↓ HTTPS Request
Infura API (https://sepolia.infura.io)
         ↓ Connects to
Sepolia Ethereum Network (thousands of nodes)
         ↓ Stores data in
Blockchain (immutable ledger)
```

#### **Why Infura/Alchemy instead of running your own node?**

**Running your own Ethereum node:**
```bash
# Requires:
- 500GB+ disk space (full node)
- 16GB RAM
- 24/7 uptime
- Constant syncing with network
- Maintenance and updates
```

**Using Infura:**
```bash
# Requires:
- Free API key
- 100,000 requests/day (free tier)
- Instant access
- No maintenance
```

---

### 2.4 Complete Flow: How They Work Together

```javascript
// STEP 1: Initialize connection
const provider = new ethers.JsonRpcProvider(
  process.env.BLOCKCHAIN_PROVIDER_URL  // Gateway to blockchain
);

// STEP 2: Create wallet with private key
const wallet = new ethers.Wallet(
  process.env.BLOCKCHAIN_PRIVATE_KEY,  // Your identity
  provider  // Connected to network
);

// STEP 3: Connect to smart contract
const contract = new ethers.Contract(
  process.env.CONTRACT_ADDRESS,  // Where the code lives
  contractABI,  // How to talk to it
  wallet  // Who is calling (signed with private key)
);

// STEP 4: Call contract function
const tx = await contract.classifyDomain("example.com", true, "Phishing");
// What happens:
// 1. Ethers.js encodes function call into transaction data
// 2. Signs transaction with BLOCKCHAIN_PRIVATE_KEY
// 3. Sends via BLOCKCHAIN_PROVIDER_URL to network
// 4. Contract at CONTRACT_ADDRESS executes function
// 5. State changes stored on blockchain

// STEP 5: Wait for confirmation
const receipt = await tx.wait();
// Transaction included in block on Sepolia network
```

---

## 3. Complete Low-Level Workflow Diagram

### 🔄 End-to-End Flow: From Email Click to Blockchain Storage

---

### **3.1 Initial Setup Phase (One-Time)**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DEVELOPER SETUP (ONE-TIME)                        │
└─────────────────────────────────────────────────────────────────────┘

1. Install Dependencies
   ├── Backend: pip install -r requirements.txt
   ├── Blockchain: cd blockchain && npm install
   └── Extension: Load in Chrome

2. Create .env File
   ├── GEMINI_API_KEY=...
   ├── EXT_API_KEY=... (optional)
   ├── BLOCKCHAIN_PROVIDER_URL=https://sepolia.infura.io/v3/...
   ├── BLOCKCHAIN_PRIVATE_KEY=... (get from MetaMask)
   └── BLOCKCHAIN_NETWORK_ID=11155111

3. Deploy Smart Contract
   ├── cd blockchain
   ├── npx hardhat compile
   │   └── Creates: artifacts/contracts/DomainReputation.sol/DomainClassification.json
   ├── node deploy.js
   │   ├── Reads: DomainClassification.json (ABI + bytecode)
   │   ├── Creates: ContractFactory with ABI + bytecode
   │   ├── wallet.deploy(ContractFactory)
   │   ├── Signs deployment transaction with BLOCKCHAIN_PRIVATE_KEY
   │   ├── Sends via BLOCKCHAIN_PROVIDER_URL to Sepolia network
   │   ├── Miners include transaction in block
   │   ├── Contract code stored at new address
   │   └── Returns: CONTRACT_ADDRESS (e.g., 0x14B9A...)
   └── Update .env with CONTRACT_ADDRESS

4. Start Backend
   python backend.py
   ├── Loads .env variables
   ├── Initializes models:
   │   ├── embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
   │   ├── content_model = pickle.load('email_log_reg_embed_model.pkl')
   │   ├── url_model = pickle.load('random_forest_url_model.pkl')
   │   └── llm_model = genai.GenerativeModel('gemini-2.5-flash')
   ├── Connects to blockchain:
   │   ├── subprocess.run(['node', 'interact.js', 'stats'])
   │   └── Logs: ✅ Connected to blockchain
   └── Starts Flask server on http://127.0.0.1:8080

5. Load Extension
   ├── Open chrome://extensions/
   ├── Enable Developer Mode
   ├── Click "Load unpacked"
   ├── Select: phish-analyzer-extension/
   └── Extension loads:
       ├── background.js (service worker)
       ├── content_script.js (Gmail injection)
       └── popup.js (settings UI)
```

---

### **3.2 User Opens Email (Email Analysis Flow)**

```
┌─────────────────────────────────────────────────────────────────────┐
│          PHASE 1: USER OPENS EMAIL IN GMAIL                          │
└─────────────────────────────────────────────────────────────────────┘

Step 1: Gmail Page Load
  User navigates to Gmail
         ↓
  content_script.js injected by Chrome
         ↓
  MutationObserver watches for DOM changes
         ↓
  Detects: div[data-message-id] (email opened)

Step 2: Create "Analyze" Button
  content_script.js:
  ├── const analyzeBtn = document.createElement('button')
  ├── analyzeBtn.textContent = 'Analyze'
  ├── analyzeBtn.onclick = () => analyzeEmail()
  └── Insert button into Gmail toolbar

Step 3: User Clicks "Analyze"
  analyzeEmail() function triggered
         ↓
  Extract email data from DOM:
  ├── sender = document.querySelector('[email]').getAttribute('email')
  │   └── Example: "support@figma.com"
  ├── subject = document.querySelector('[data-subject]').innerText
  │   └── Example: "We've updated our Terms of Service"
  ├── body = document.querySelector('[data-message-body]').innerText
  │   └── Example: "Dear user, click here to review..."
  └── urls = extractUrls(body)
      └── Regex: /https?:\/\/[^\s<>"{}|\\^`\[\]]+/g
      └── Example: ["https://click.figma.com/accept"]

Step 4: Show Loading Indicator
  content_script.js:
  ├── showOverlay({ loading: true })
  ├── Create panel div with:
  │   ├── Spinner animation
  │   └── "Analyzing email..." text
  └── Insert into Gmail DOM

Step 5: Send to Backend
  const response = await fetch('http://127.0.0.1:8080/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': apiKey  // From chrome.storage
    },
    body: JSON.stringify({
      sender: "support@figma.com",
      subject: "We've updated our Terms of Service",
      body: "Dear user, click here...",
      urls: ["https://click.figma.com/accept"]
    })
  });
```

---

### **3.3 Backend Analysis Pipeline**

```
┌─────────────────────────────────────────────────────────────────────┐
│      PHASE 2: BACKEND RECEIVES REQUEST & ANALYZES EMAIL              │
└─────────────────────────────────────────────────────────────────────┘

Step 1: Flask Receives Request
  backend.py @app.route("/analyze", methods=["POST"])
         ↓
  API key validation (if EXT_API_KEY set):
  ├── provided_key = request.headers.get("x-api-key")
  ├── if provided_key != EXT_API_KEY:
  │   └── return 403 Forbidden
  └── Continue if valid

Step 2: Extract Data from Request
  data = request.json
  ├── sender = data.get("sender")  # "support@figma.com"
  ├── subject = data.get("subject")  # "We've updated..."
  ├── body = data.get("body")  # Email content
  └── urls = data.get("urls", [])  # ["https://click.figma.com/accept"]

Step 3: Call Analysis Function
  final_risk, details = compute_final_risk(
    body=body,
    sender=sender,
    subject=subject
  )
```

---

### **3.4 Blockchain-First Analysis (Most Important!)**

```
┌─────────────────────────────────────────────────────────────────────┐
│   PHASE 3: BLOCKCHAIN-FIRST DOMAIN REPUTATION CHECK (FAST PATH)     │
└─────────────────────────────────────────────────────────────────────┘

Step 1: Extract Domains
  utils.py → compute_final_risk()
  ├── Extract URLs from content:
  │   ├── full_content = f"{subject} {body}"
  │   ├── url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
  │   ├── urls = re.findall(url_pattern, full_content)
  │   └── Found: ["https://click.figma.com/accept"]
  │
  ├── Extract domains from URLs:
  │   ├── For each URL:
  │   │   ├── parsed = urlparse(url)
  │   │   ├── domain = parsed.netloc  # "click.figma.com"
  │   │   └── if domain.startswith('www.'): domain = domain[4:]
  │   └── domains = ["click.figma.com"]
  │
  └── Add sender domain:
      ├── sender = "support@figma.com"
      ├── sender_domain = sender.split('@')[1]  # "figma.com"
      └── domains = ["click.figma.com", "figma.com"]

Step 2: Query Blockchain for EACH Domain
  For domain in ["click.figma.com", "figma.com"]:
  
    ┌─────────────────────────────────────────────────┐
    │  Blockchain Query for: figma.com                 │
    └─────────────────────────────────────────────────┘
    
    2.1: Python calls Node.js subprocess
         utils.py → get_blockchain_domain_reputation(domain)
         ├── script_path = "blockchain/interact.js"
         └── result = subprocess.run(
               ['node', script_path, 'query', domain],
               capture_output=True,
               text=True,
               timeout=10,
               encoding='utf-8'  # ✅ Fixes Unicode errors
             )
    
    2.2: Node.js script initializes
         interact.js → args = ['query', 'figma.com']
         ├── Load .env variables:
         │   ├── CONTRACT_ADDRESS
         │   ├── BLOCKCHAIN_PRIVATE_KEY
         │   └── BLOCKCHAIN_PROVIDER_URL
         │
         ├── Create provider:
         │   ├── provider = new ethers.JsonRpcProvider(PROVIDER_URL)
         │   └── Establishes HTTPS connection to Infura
         │
         ├── Create wallet:
         │   ├── wallet = new ethers.Wallet(PRIVATE_KEY, provider)
         │   └── Derives public address from private key
         │
         └── Create contract instance:
             ├── contract = new ethers.Contract(
             │     CONTRACT_ADDRESS,  # Where contract lives
             │     contractABI,       # Function signatures
             │     wallet             # Who is calling
             │   )
             └── Contract ready to call
    
    2.3: Call smart contract function
         interact.js → contract.getDomainClassification("figma.com")
         
         ├── Ethers.js encodes function call:
         │   ├── functionSelector = keccak256("getDomainClassification(string)")[:4]
         │   ├── encodedParams = abi.encode(["figma.com"])
         │   └── callData = functionSelector + encodedParams
         │
         ├── Create eth_call request:
         │   ├── {
         │   │   "jsonrpc": "2.0",
         │   │   "method": "eth_call",
         │   │   "params": [{
         │   │     "to": "0x14B9A3Fd9502528a7Bdf7780eE75b387b942b0D3",
         │   │     "data": callData
         │   │   }, "latest"],
         │   │   "id": 1
         │   │ }
         │   └── This is a READ-ONLY call (no transaction, no gas)
         │
         └── Send HTTPS request to Infura
    
    2.4: Infura processes request
         ├── Receives eth_call request
         ├── Forwards to Sepolia network nodes
         └── Nodes execute contract code:
             ├── Load contract bytecode from CONTRACT_ADDRESS
             ├── Execute getDomainClassification(domain) function
             ├── Read from contract storage:
             │   ├── mapping(string => DomainInfo) domains;
             │   └── domains["figma.com"] = ?
             └── Return result
    
    2.5: Smart contract executes
         DomainReputation.sol:
         
         function getDomainClassification(string memory _domain) 
           external view returns (
             bool exists,
             bool isSpam,
             uint256 timestamp,
             address reporter,
             string memory reason
           ) 
         {
           DomainInfo storage info = domains[_domain];
           
           if (info.reporter == address(0)) {
             // Domain not found in mapping
             return (false, false, 0, address(0), "");
           }
           
           // Domain found, return its data
           return (
             true,
             info.isSpam,        // true = spam, false = ham
             info.timestamp,     // When classified
             info.reporter,      // Who classified it
             info.reason         // Why classified
           );
         }
    
    2.6: Result returned through layers
         Smart Contract
              ↓ (exists=true, isSpam=false, timestamp=1697280000, ...)
         Ethereum Node
              ↓ RLP encoded response
         Infura API
              ↓ JSON-RPC response
         Ethers.js provider.call()
              ↓ Decoded using ABI
         interact.js
              ↓ Parse and format
         
         if (result && result.exists) {
           console.log(result.isSpam ? "SPAM" : "HAM");
           // Prints: HAM
         } else {
           console.log("UNKNOWN");
         }
    
    2.7: Python receives stdout
         utils.py:
         ├── stdout = "🔍 Querying domain: figma.com\n📊 Domain found:\nHAM"
         ├── lines = stdout.strip().split('\n')
         ├── classification = lines[-1]  # "HAM"
         │
         └── return {
               "exists": True,
               "reputation_score": 90,  # HAM = high score
               "consensus": "ham",
               "spam_votes": 0,
               "ham_votes": 1,
               "total_reports": 1
             }

Step 3: Calculate Blockchain Weight
  If ANY domain found in blockchain:
  ├── blockchain_weight = 0.7  # 70% weight!
  └── Skip expensive LLM analysis
  
  If NO domains found:
  ├── blockchain_weight = 0.0
  └── Run full ML + LLM analysis

Step 4: Compute Risk Score (Blockchain Found)
  
  ┌─────────────────────────────────────────────────────┐
  │  SCENARIO A: Domain Found in Blockchain (figma.com) │
  └─────────────────────────────────────────────────────┘
  
  weights = {
    'content': 0.10,    # ML content analysis
    'url': 0.10,        # ML URL analysis  
    'llm': 0.10,        # LLM (minimal weight)
    'blockchain': 0.70  # BLOCKCHAIN DOMINANT!
  }
  
  # Content ML (always runs, fast)
  content_prob = 0.017  # 1.7% risk
  
  # URL ML (always runs, fast)
  url_prob = 0.500  # 50% risk (neutral)
  
  # LLM (SKIPPED!)
  llm_score = 0.5  # Not computed, use neutral
  llm_reason = "Skipped - using blockchain consensus"
  llm_actions = ["Skipped - using blockchain consensus"]
  
  # Blockchain
  blockchain_score = 0.0  # figma.com is HAM (legitimate)
  
  # Final calculation
  final_risk = (
    0.10 * 0.017 +  # content
    0.10 * 0.500 +  # url
    0.10 * 0.500 +  # llm (neutral)
    0.70 * 0.000    # blockchain (HAM = 0% risk)
  )
  final_risk = 0.001 + 0.05 + 0.05 + 0.0 = 0.101
  final_risk = 10.1% ≈ 10% risk → SAFE
  
  ⏱️  Analysis time: ~1-2 seconds (blockchain query only!)
```

---

### **3.5 Full ML+LLM Analysis (Blockchain Not Found)**

```
┌─────────────────────────────────────────────────────────────────────┐
│  SCENARIO B: Domain NOT in Blockchain (example-unknown-site.com)    │
└─────────────────────────────────────────────────────────────────────┘

Step 1: ML Content Analysis
  utils.py → analyze_content_with_ml(body)
  
  ├── embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
  ├── embedding = embedding_model.encode([body])
  │   └── Converts text to 384-dimensional vector
  │       Example: [0.123, -0.456, 0.789, ...]
  │
  ├── content_model = LogisticRegression (pre-trained)
  ├── proba = content_model.predict_proba(embedding)[0]
  │   └── [0.921, 0.079]  # [ham_prob, spam_prob]
  │
  ├── spam_prob = proba[1] = 0.079  # 7.9% spam
  ├── confidence = max(proba) = 0.921  # 92.1% confident
  └── return (0.079, 0.921)

Step 2: ML URL Analysis
  utils.py → analyze_urls_with_ml(urls)
  
  For each URL in ["https://example-unknown-site.com/offer"]:
  
  ├── Extract features:
  │   ├── len(url) = 45
  │   ├── domain_length = 25
  │   ├── num_dots = 1
  │   ├── num_hyphens = 2
  │   ├── has_ip = 0
  │   ├── has_https = 1
  │   └── ... (50 features total)
  │
  ├── url_model = RandomForestClassifier (pre-trained)
  ├── features_array = np.array(features).reshape(1, -1)
  ├── score = url_model.predict_proba(features_array)[0][1]
  │   └── 0.650  # 65% spam probability
  └── return 0.650

Step 3: LLM Analysis (Google Gemini)
  utils.py → analyze_with_llm(body, sender, subject)
  
  3.1: Construct prompt
       prompt = f"""
       Analyze this email for phishing indicators. 
       Provide a risk score from 0.0 (safe) to 1.0 (definitely phishing).
       
       Subject: {subject}
       From: {sender}
       Content: {body[:1000]}...
       
       Consider:
       1. Urgency and fear tactics
       2. Suspicious links or attachments
       3. Poor grammar/spelling
       4. Sender authenticity
       5. Request for sensitive information
       
       Respond with:
       RISK_SCORE: [0.0-1.0]
       REASON: [brief explanation]
       CONFIDENCE: [0.0-1.0]
       """
  
  3.2: Call Gemini API
       ├── import google.generativeai as genai
       ├── genai.configure(api_key=GEMINI_API_KEY)
       ├── llm_model = genai.GenerativeModel('gemini-2.5-flash')
       │
       └── response = llm_model.generate_content(prompt)
           ├── Sends HTTPS POST to:
           │   └── https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent
           ├── Request body:
           │   {
           │     "contents": [{"parts": [{"text": prompt}]}],
           │     "generationConfig": {
           │       "temperature": 0.7,
           │       "maxOutputTokens": 1024
           │     }
           │   }
           └── Gemini processes (2-5 seconds)
  
  3.3: Gemini Response
       {
         "candidates": [{
           "content": {
             "parts": [{
               "text": "RISK_SCORE: 0.75\nREASON: Email contains urgency tactics ('Act now!'), suspicious shortened URL, and requests personal information.\nCONFIDENCE: 0.85"
             }]
           },
           "finishReason": "STOP"
         }]
       }
  
  3.4: Parse response
       text = response.text
       # "RISK_SCORE: 0.75\nREASON: ...\nCONFIDENCE: 0.85"
       
       risk_score = 0.75
       reason = "Email contains urgency tactics..."
       confidence = 0.85
       
       return (0.75, reason, 0.85)

Step 4: Combine All Scores
  utils.py → compute_final_risk()
  
  weights = {
    'content': 0.30,
    'url': 0.20,
    'llm': 0.50,
    'blockchain': 0.00  # Not found
  }
  
  final_risk = (
    0.30 * 0.079 +  # Content ML
    0.20 * 0.650 +  # URL ML
    0.50 * 0.750 +  # LLM
    0.00 * 0.500    # Blockchain (not used)
  )
  final_risk = 0.024 + 0.130 + 0.375 + 0.0 = 0.529
  final_risk = 52.9% risk → SUSPICIOUS
  
  ⏱️  Analysis time: ~5-8 seconds (LLM is slow)
```

---

### **3.6 Auto-Reporting to Blockchain (High Confidence Results)**

```
┌─────────────────────────────────────────────────────────────────────┐
│   PHASE 4: AUTO-REPORT HIGH-CONFIDENCE RESULTS TO BLOCKCHAIN        │
└─────────────────────────────────────────────────────────────────────┘

Step 1: Check Auto-Report Criteria
  backend.py:
  
  confidence = 0.85  # From analysis
  AUTO_REPORT_ENABLED = True
  MIN_CONFIDENCE_THRESHOLD = 0.8
  
  if confidence >= MIN_CONFIDENCE_THRESHOLD and AUTO_REPORT_ENABLED:
    # Automatically store to blockchain
    for domain in domains:
      is_spam = (final_risk > 0.5)
      store_classification_to_blockchain(
        domain=domain,
        is_spam=is_spam,
        reason="Auto-reported by ML/AI analysis"
      )

Step 2: Store to Blockchain
  utils.py → store_classification_to_blockchain()
  
  2.1: Call Node.js script
       classification = 'true' if is_spam else 'false'
       
       result = subprocess.run(
         [
           'node',
           'blockchain/interact.js',
           'classify',
           'example-unknown-site.com',  # Domain
           'true',                       # Is spam
           'Auto-reported by ML/AI analysis'  # Reason
         ],
         capture_output=True,
         text=True,
         timeout=60,  # Increased for blockchain confirmation
         encoding='utf-8'
       )
  
  2.2: Node.js receives command
       interact.js:
       ├── args = ['classify', 'example-unknown-site.com', 'true', 'Auto-reported...']
       ├── domain = args[1]
       ├── isSpam = (args[2] === 'true')
       └── reason = args[3]
  
  2.3: Call classifyDomain with retry
       contract.classifyDomain(domain, isSpam, reason, maxRetries=3)
       
       ┌──────────────────────────────────────────────────┐
       │  Attempt 1: Submit Transaction                   │
       └──────────────────────────────────────────────────┘
       
       ├── Check cooldown:
       │   ├── canSubmit = await contract.canUserSubmit(wallet.address)
       │   └── If cooldown active: wait or retry later
       │
       ├── Encode function call:
       │   ├── functionFragment = contract.interface.getFunction('classifyDomain')
       │   ├── encodedData = contract.interface.encodeFunctionData(
       │   │     'classifyDomain',
       │   │     ['example-unknown-site.com', true, 'Auto-reported...']
       │   │   )
       │   └── data = "0x1234abcd..." (hex encoded)
       │
       ├── Create transaction:
       │   ├── const tx = await contract.classifyDomain(domain, isSpam, reason)
       │   │
       │   │   Behind the scenes:
       │   │   ├── Get current gas price:
       │   │   │   └── gasPrice = await provider.getFeeData()
       │   │   │
       │   │   ├── Get nonce (transaction count):
       │   │   │   └── nonce = await provider.getTransactionCount(wallet.address)
       │   │   │
       │   │   ├── Estimate gas:
       │   │   │   └── gasLimit = await contract.estimateGas.classifyDomain(...)
       │   │   │
       │   │   ├── Build unsigned transaction:
       │   │   │   {
       │   │   │     to: "0x14B9A3Fd9502528a7Bdf7780eE75b387b942b0D3",
       │   │   │     data: encodedData,
       │   │   │     gasLimit: 150000,
       │   │   │     maxFeePerGas: "50 gwei",
       │   │   │     maxPriorityFeePerGas: "2 gwei",
       │   │   │     nonce: 42,
       │   │   │     chainId: 11155111
       │   │   │   }
       │   │   │
       │   │   ├── Sign transaction:
       │   │   │   ├── txHash = keccak256(serialize(unsignedTx))
       │   │   │   ├── signature = sign(txHash, BLOCKCHAIN_PRIVATE_KEY)
       │   │   │   └── signedTx = { ...unsignedTx, ...signature }
       │   │   │
       │   │   └── Broadcast transaction:
       │   │       ├── provider.sendTransaction(signedTx)
       │   │       ├── POST to Infura API:
       │   │       │   {
       │   │       │     "jsonrpc": "2.0",
       │   │       │     "method": "eth_sendRawTransaction",
       │   │       │     "params": ["0x...signedTxData"],
       │   │       │     "id": 1
       │   │       │   }
       │   │       └── Infura forwards to Sepolia network
       │   │
       │   └── tx = { hash: "0xabc123...", ... }
       │
       └── console.log(`⏳ Transaction submitted: ${tx.hash}`)
  
  2.4: Wait for confirmation
       const receipt = await tx.wait()
       
       ├── Ethers.js polls Infura every 2 seconds:
       │   ├── eth_getTransactionReceipt(txHash)
       │   └── Null while pending
       │
       ├── Sepolia miners:
       │   ├── Pick up transaction from mempool
       │   ├── Validate signature
       │   ├── Execute smart contract function:
       │   │   ├── Load contract bytecode
       │   │   ├── Execute classifyDomain():
       │   │   │   {
       │   │   │     require(block.timestamp >= lastSubmissionTime[msg.sender] + submissionCooldown);
       │   │   │     domains[_domain] = DomainInfo({
       │   │   │       isSpam: true,
       │   │   │       timestamp: block.timestamp,
       │   │   │       reporter: msg.sender,
       │   │   │       reason: "Auto-reported..."
       │   │   │     });
       │   │   │     lastSubmissionTime[msg.sender] = block.timestamp;
       │   │   │     emit DomainClassified(_domain, true, msg.sender, block.timestamp);
       │   │   │   }
       │   │   └── State changes written to blockchain
       │   ├── Include transaction in block
       │   └── Block propagated to network
       │
       └── receipt = {
             blockNumber: 9411250,
             blockHash: "0xdef456...",
             transactionHash: "0xabc123...",
             gasUsed: 125000,
             status: 1  // Success
           }
  
  2.5: Return success
       console.log(`✅ Transaction confirmed in block: ${receipt.blockNumber}`)
       
       return {
         success: true,
         txHash: tx.hash,
         blockNumber: receipt.blockNumber
       }
  
  2.6: Python receives result
       utils.py:
       ├── stdout = "✅ Transaction confirmed in block: 9411250"
       ├── if result.returncode == 0:
       │   └── logger.info(f"Successfully stored {domain} as {classification}")
       └── return (True, f"Domain {domain} stored as {classification}")
```

---

### **3.7 Response to Frontend**

```
┌─────────────────────────────────────────────────────────────────────┐
│         PHASE 5: SEND ANALYSIS RESULT TO BROWSER EXTENSION          │
└─────────────────────────────────────────────────────────────────────┘

Step 1: Backend Formats Response
  backend.py:
  
  # Determine label
  if final_risk < 0.3:
    label = "safe"
  elif final_risk < 0.7:
    label = "suspicious"
  else:
    label = "phishing"
  
  # Build response
  response = {
    "final_risk": 0.125,  # 12.5%
    "label": "safe",
    "llm_reason": "Skipped - using blockchain consensus",
    "llm_actions": ["Skipped - using blockchain consensus"],
    "sender": "support@figma.com",
    "blockchain_weight": 0.7,
    "domain_reputations": {
      "figma.com": {
        "exists": True,
        "reputation_score": 90,
        "consensus": "ham"
      }
    },
    "details": {
      "content_prob": 0.017,
      "url_prob": 0.500,
      "llm_conf": 0.9,
      "urls": ["https://click.figma.com/accept"],
      "domains": ["figma.com", "click.figma.com"]
    }
  }
  
  return jsonify(response), 200

Step 2: Extension Receives Response
  content_script.js:
  
  const result = await response.json()
  // result = { final_risk: 0.125, label: "safe", ... }
  
  showOverlay(result)

Step 3: Display Analysis Panel
  content_script.js → showOverlay(result)
  
  ├── Calculate safe percentage:
  │   └── safePercentage = (1 - result.final_risk) * 100 = 87.5%
  │
  ├── Create panel HTML:
  │   const panel = document.createElement('div')
  │   panel.id = 'phish-analyzer-panel'
  │   panel.innerHTML = `
  │     <div class="panel-header">
  │       🛡️ Email Phish Analyzer
  │       <button class="close-btn">×</button>
  │     </div>
  │     
  │     <div class="risk-card" style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%)">
  │       <h3>Risk Assessment:</h3>
  │       <h2 style="color: #155724">Safe (88%)</h2>
  │     </div>
  │     
  │     <div class="blockchain-section">
  │       <h4>🔗 Blockchain Reputation:</h4>
  │       <p>✅ figma.com: Legitimate (HAM)</p>
  │       <p>Score: 90/100</p>
  │     </div>
  │     
  │     <div class="reasoning">
  │       <h4>💭 Reasoning:</h4>
  │       <p>Skipped - using blockchain consensus</p>
  │     </div>
  │     
  │     <div class="actions">
  │       <h4>✅ Recommended Actions:</h4>
  │       <ol>
  │         <li>Skipped - using blockchain consensus</li>
  │       </ol>
  │     </div>
  │     
  │     <div class="feedback">
  │       <h4>📊 Help improve accuracy:</h4>
  │       <button class="btn-safe">✅ Safe</button>
  │       <button class="btn-phishing">❌ Phishing</button>
  │     </div>
  │   `
  │
  ├── Make panel draggable:
  │   ├── header.addEventListener('mousedown', startDrag)
  │   └── document.addEventListener('mousemove', drag)
  │
  ├── Add close button handler:
  │   └── closeBtn.addEventListener('click', () => panel.remove())
  │
  └── Insert into Gmail:
      └── document.body.appendChild(panel)

⏱️  Total Time Breakdown:
  - Email data extraction: 0.1s
  - Backend analysis: 1.5s
    ├── Domain extraction: 0.1s
    ├── Blockchain query: 1.0s
    ├── ML analysis: 0.3s
    └── Response formatting: 0.1s
  - Rendering panel: 0.1s
  
  TOTAL: ~1.7 seconds (with blockchain hit)
  vs. ~7-10 seconds (without blockchain, full LLM)
```

---

### **3.8 User Feedback Flow**

```
┌─────────────────────────────────────────────────────────────────────┐
│    PHASE 6: USER PROVIDES FEEDBACK (SAFE/PHISHING BUTTONS)          │
└─────────────────────────────────────────────────────────────────────┘

Step 1: User Clicks Feedback Button
  User clicks: "❌ Phishing" button
  
  content_script.js:
  ├── phishingBtn.addEventListener('click', () => {
  │     submitFeedback(analysisResult, 'spam')
  │   })
  │
  └── submitFeedback() triggered

Step 2: Re-Extract Email Data
  content_script.js → submitFeedback()
  
  // Re-extract to ensure fresh data
  const currentEmailData = getGmailMessageData()
  
  ├── sender = "support@figma.com"
  ├── subject = "We've updated..."
  └── urls = ["https://click.figma.com/accept"]

Step 3: Prepare Feedback Payload
  const feedbackPayload = {
    analysis_result: {
      final_risk: 0.125,
      sender: "support@figma.com",
      details: {
        urls: ["https://click.figma.com/accept"],
        domains: ["figma.com", "click.figma.com"]
      }
    },
    user_classification: "spam",  // User says it's phishing
    reason: "User feedback from Gmail extension - Phishing reported"
  }

Step 4: Send to Backend
  fetch('http://127.0.0.1:8080/blockchain/bulk-report', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': apiKey
    },
    body: JSON.stringify(feedbackPayload)
  })

Step 5: Backend Processes Feedback
  backend.py → @app.route("/blockchain/bulk-report")
  
  5.1: Extract domains from feedback
       ├── sender_domain = extract_domain_from_email(sender)
       │   └── "figma.com"
       │
       └── url_domains = extract_domains_from_urls(urls)
           └── ["click.figma.com"]
       
       domains = ["figma.com", "click.figma.com"]
  
  5.2: Submit each domain to blockchain
       For each domain:
       
       is_spam = (classification == 'spam')  # True
       
       success, message = store_classification_to_blockchain(
         domain="figma.com",
         is_spam=True,  # User marked as phishing
         reason="User feedback from Gmail extension - Phishing reported"
       )
       
       ├── Python calls Node.js:
       │   subprocess.run([
       │     'node', 'interact.js',
       │     'classify', 'figma.com', 'true',
       │     'User feedback from Gmail extension - Phishing reported'
       │   ])
       │
       ├── Node.js submits transaction (with retry):
       │   ├── Attempt 1: May fail if cooldown active
       │   ├── Wait 2 seconds
       │   ├── Attempt 2: Success
       │   └── Transaction confirmed in block 9411260
       │
       └── Return success = True
  
  5.3: Wait between domains (0.5s delay)
       time.sleep(0.5)  # Prevent cooldown issues
  
  5.4: Return results
       return jsonify({
         "successful_reports": 2,
         "failed_reports": 0,
         "total_domains": 2,
         "results": [
           {"domain": "figma.com", "success": True},
           {"domain": "click.figma.com", "success": True}
         ]
       })

Step 6: Extension Shows Feedback Result
  content_script.js:
  
  const result = await response.json()
  
  feedbackDiv.innerHTML = `
    <div style="color: #137333">
      ✅ Reported 2/2 domains to blockchain
    </div>
  `
  
  setTimeout(() => {
    feedbackDiv.innerHTML = ''  // Hide after 3 seconds
  }, 3000)

Step 7: Blockchain Updated
  Smart contract state now contains:
  
  domains["figma.com"] = {
    isSpam: true,  // ⚠️ CHANGED from false to true
    timestamp: 1697285000,
    reporter: 0x5C792FdF1a0aeBd8A6EeC4C5C67e814f1fbE85A4,
    reason: "User feedback from Gmail extension - Phishing reported"
  }
  
  domains["click.figma.com"] = {
    isSpam: true,
    timestamp: 1697285001,
    reporter: 0x5C792FdF1a0aeBd8A6EeC4C5C67e814f1fbE85A4,
    reason: "User feedback from Gmail extension - Phishing reported"
  }

Step 8: Next Analysis Will Use Updated Data
  When ANY user analyzes email from figma.com again:
  
  ├── Blockchain query: figma.com
  ├── Result: SPAM (based on user feedback)
  ├── blockchain_score = 1.0 (100% spam)
  ├── blockchain_weight = 0.7 (70% weight)
  └── final_risk = 0.7 * 1.0 + ... = HIGH RISK
  
  Email will now be marked as PHISHING! 🎯
```

---

### **3.9 Complete System State Diagram**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SYSTEM STATE TRANSITIONS                          │
└─────────────────────────────────────────────────────────────────────┘

State 1: Initial Deployment
  ├── Smart contract deployed to Sepolia
  ├── CONTRACT_ADDRESS saved to .env
  ├── No domains in blockchain yet
  └── domains mapping = {}

State 2: First Email Analysis (figma.com)
  ├── Blockchain query: UNKNOWN
  ├── Run full ML + LLM analysis
  ├── Result: SAFE (12.5% risk)
  ├── Auto-report to blockchain (confidence 85% > 80%)
  └── domains["figma.com"] = { isSpam: false, ... }

State 3: Second Email Analysis (figma.com)
  ├── Blockchain query: HAM (found!)
  ├── Skip LLM analysis
  ├── Use blockchain score directly
  ├── Result: SAFE (10% risk)
  └── ⏱️  2 seconds (vs 8 seconds without blockchain)

State 4: User Provides Feedback (marks as phishing)
  ├── User clicks "❌ Phishing"
  ├── Submit to blockchain
  ├── domains["figma.com"] = { isSpam: true, ... } (updated)
  └── Blockchain state changed

State 5: Third Email Analysis (figma.com)
  ├── Blockchain query: SPAM (updated!)
  ├── Skip LLM analysis
  ├── Use blockchain score (spam = 100% risk)
  ├── Result: PHISHING (70% risk)
  └── Email marked as dangerous

State 6: Accumulating Data
  After 1000 user reports:
  ├── domains["google.com"] = { isSpam: false, reports: 500 }
  ├── domains["paypal-secure.tk"] = { isSpam: true, reports: 300 }
  ├── domains["amazon.com"] = { isSpam: false, reports: 450 }
  └── Rich reputation database built over time
```

---

## 📊 Complete Data Flow Summary

### **Key Takeaways:**

1. **JavaScript is Essential for Blockchain**
   - Ethers.js is industry standard
   - Mature, well-documented, battle-tested
   - Web3.py (Python) is less capable
   - Subprocess architecture keeps concerns separated

2. **Private Key = Your Identity**
   - Signs all blockchain transactions
   - Proves you own the Ethereum account
   - MUST be kept secret (never commit to Git)
   - Used by Node.js, never exposed to Flask API

3. **Contract Address = Smart Contract Location**
   - Where your code lives on blockchain
   - Permanent, immutable address
   - All interactions target this address
   - Deployed once, used forever

4. **Blockchain-First = Performance**
   - 85% faster when domain in blockchain (1-2s vs 8s)
   - Skips expensive LLM calls
   - Community-driven reputation database
   - Scales with user feedback

5. **User Feedback = Continuous Learning**
   - Users correct AI mistakes
   - Blockchain stores corrections permanently
   - Future analyses benefit from past corrections
   - Decentralized truth consensus

---

## 🎯 Final Architecture Visualization

```
┌───────────────────────────────────────────────────────────────────────┐
│                         EMAIL ANALYSIS SYSTEM                          │
└───────────────────────────────────────────────────────────────────────┘
                                    │
                ┌───────────────────┼───────────────────┐
                │                   │                   │
                ▼                   ▼                   ▼
      ┌──────────────────┐  ┌──────────────┐  ┌──────────────────┐
      │ Browser Extension│  │ Flask Backend│  │ Blockchain Layer │
      │   (JavaScript)   │  │   (Python)   │  │   (Node.js)      │
      └──────────────────┘  └──────────────┘  └──────────────────┘
      │                     │                  │
      │ - Extract email     │ - ML models      │ - Ethers.js
      │ - Display results   │ - LLM API        │ - Smart contract
      │ - User feedback     │ - Orchestration  │ - TX signing
      │                     │                  │
      └──────────┬──────────┴────────┬─────────┴──────────┐
                 │                   │                    │
                 ▼                   ▼                    ▼
         Gmail Interface      Analysis Engine    Ethereum Blockchain
         (DOM injection)      (compute_final     (Sepolia Testnet)
                              _risk())           (CONTRACT_ADDRESS)
```
---
```

# Implementation Flow - Sender Email Storage

## Old Flow (Domain-Based) ❌

```
Email from: spammer@gmail.com
Link: https://forms.gle/scam123

┌─────────────────────────────────────┐
│  Extract Domains                    │
│  - gmail.com (from sender)          │
│  - forms.gle (from link)            │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Store in Blockchain                │
│  ✓ gmail.com → SPAM                 │
│  ✓ forms.gle → SPAM                 │
└─────────────────────────────────────┘

Later...

Email from: verified@company.com  
Link: https://forms.gle/survey456

┌─────────────────────────────────────┐
│  Query Blockchain                   │
│  ? forms.gle → Found: SPAM ⚠️       │
└─────────────────────────────────────┘
              ↓
        FALSE POSITIVE!
    (Legitimate email flagged)
```

## New Flow (Email-Based) ✅

```
Email from: spammer@gmail.com
Link: https://forms.gle/scam123

┌─────────────────────────────────────┐
│  Extract Sender Email               │
│  - spammer@gmail.com                │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Store in Blockchain                │
│  ✓ spammer@gmail.com → SPAM         │
└─────────────────────────────────────┘

Later...

Email from: verified@company.com  
Link: https://forms.gle/survey456

┌─────────────────────────────────────┐
│  Query Blockchain                   │
│  ? verified@company.com             │
│  → Not Found (New sender)           │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Run Fresh LLM Analysis             │
│  ✓ Analyzed independently           │
└─────────────────────────────────────┘
              ↓
        NO FALSE POSITIVE!
    (Legitimate email analyzed correctly)
```

## User Experience Flow

### First Email from Spammer

```
┌──────────────────────────┐
│ User receives email      │
│ From: spammer@gmail.com  │
└──────────────────────────┘
            ↓
┌──────────────────────────┐
│ Click "Analyze" button   │
└──────────────────────────┘
            ↓
┌──────────────────────────┐
│ Backend Processing:      │
│ 1. Check blockchain      │
│    ✗ Not found          │
│ 2. Run ML analysis       │
│ 3. Run LLM analysis      │
│ 4. Final Risk: 0.92      │
└──────────────────────────┘
            ↓
┌──────────────────────────┐
│ Show Result:             │
│ "Phishing (92%)"         │
│ No blockchain warning    │
└──────────────────────────┘
            ↓
┌──────────────────────────┐
│ Auto-Report (High conf)  │
│ Store: spammer@gmail.com │
│        → SPAM            │
└──────────────────────────┘
```

### Second Email from Same Spammer

```
┌──────────────────────────┐
│ User receives email      │
│ From: spammer@gmail.com  │
│ (Same spammer!)          │
└──────────────────────────┘
            ↓
┌──────────────────────────┐
│ Click "Analyze" button   │
└──────────────────────────┘
            ↓
┌──────────────────────────┐
│ Backend Processing:      │
│ 1. Check blockchain      │
│    ✓ FOUND: SPAM         │
│ 2. Skip LLM (use cache)  │
│ 3. Final Risk: 1.0       │
└──────────────────────────┘
            ↓
┌──────────────────────────────────────┐
│ Show Result with Warning:            │
│ ┌──────────────────────────────────┐ │
│ │ ⚠️ Based on Previous Incidents   │ │
│ │ This sender was previously       │ │
│ │ marked as SPAM                   │ │
│ └──────────────────────────────────┘ │
│                                      │
│ "Phishing (100%)"                    │
│                                      │
│ [🔄 Run Fresh LLM Analysis]          │
└──────────────────────────────────────┘
            ↓
    ┌──────────┴──────────┐
    ↓                     ↓
Accept Result      Click "Run Fresh LLM"
    ↓                     ↓
 Done!         ┌──────────────────────┐
               │ Backend runs fresh   │
               │ LLM analysis         │
               │ (force_llm=true)     │
               └──────────────────────┘
                        ↓
               ┌──────────────────────┐
               │ Show new result      │
               │ User can submit      │
               │ feedback if needed   │
               └──────────────────────┘
```

### Legitimate Email with Common Domain

```
┌──────────────────────────┐
│ User receives email      │
│ From: hr@company.com     │
│ Link: forms.gle/survey   │
└──────────────────────────┘
            ↓
┌──────────────────────────┐
│ Click "Analyze" button   │
└──────────────────────────┘
            ↓
┌──────────────────────────┐
│ Backend Processing:      │
│ 1. Check blockchain      │
│    Email: hr@company.com │
│    ✗ Not found          │
│ 2. Run ML analysis       │
│ 3. Run LLM analysis      │
│ 4. Final Risk: 0.15      │
└──────────────────────────┘
            ↓
┌──────────────────────────┐
│ Show Result:             │
│ "Safe (85%)"             │
│ ✓ No false positive!     │
└──────────────────────────┘
```

## Code Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Chrome Extension                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ content_script.js                                    │   │
│  │ - Extract email data from Gmail                     │   │
│  │ - Send to background.js                             │   │
│  └─────────────────────────────────────────────────────┘   │
│                           ↓                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ background.js                                        │   │
│  │ - Add force_llm flag if user clicked button         │   │
│  │ - POST to /analyze endpoint                         │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    Backend (app.py)                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ /analyze endpoint                                    │   │
│  │ 1. Extract sender email                             │   │
│  │ 2. Call compute_final_risk(force_llm=...)          │   │
│  │ 3. Auto-report sender if confident                  │   │
│  │ 4. Return result with blockchain flags              │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    Backend (utils.py)                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ compute_final_risk()                                 │   │
│  │ 1. Clean sender email                               │   │
│  │ 2. Query blockchain for SENDER EMAIL               │   │
│  │ 3. If found && !force_llm:                          │   │
│  │    - Use blockchain classification                  │   │
│  │    - Skip LLM (fast!)                               │   │
│  │ 4. If !found || force_llm:                          │   │
│  │    - Run ML analysis                                │   │
│  │    - Run LLM analysis                               │   │
│  │ 5. Calculate weighted risk score                    │   │
│  │ 6. Return with from_previous_incident flag          │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              Blockchain (interact.js)                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ getDomainClassification(senderEmail)                 │   │
│  │ - Query smart contract                              │   │
│  │ - Return: exists, isSpam, reason                    │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ classifyDomain(senderEmail, isSpam, reason)         │   │
│  │ - Store in smart contract                           │   │
│  │ - Emit DomainClassified event                       │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│          Smart Contract (DomainReputation.sol)               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ mapping(string => DomainRecord) public domains;      │   │
│  │ // Now stores: senderEmail => Classification        │   │
│  │                                                      │   │
│  │ Examples:                                            │   │
│  │ "spammer@gmail.com" => SPAM                         │   │
│  │ "verified@company.com" => HAM                       │   │
│  │ "hr@company.com" => HAM                             │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Key Decision Points

### Should we use blockchain data?

```
if (blockchain_found && !force_llm):
    ✓ Use blockchain classification
    ✓ Skip LLM (save time & cost)
    ✓ Show "Previous Incidents" warning
    ✓ Offer "Run Fresh LLM" button
else:
    ✓ Run fresh LLM analysis
    ✓ Show normal result
```

### How to weight the risk score?

```
Blockchain found + NOT forcing LLM:
    - Content ML: 10%
    - URL ML: 10%
    - LLM: 10% (matches blockchain)
    - Blockchain: 70% (HIGH TRUST)

Blockchain found + forcing LLM:
    - Content ML: 20%
    - URL ML: 20%
    - LLM: 40% (fresh analysis)
    - Blockchain: 20% (some history)

No blockchain data:
    - Content ML: 30%
    - URL ML: 20%
    - LLM: 50% (primary)
    - Blockchain: 0%
```

---

**This implementation ensures no false positives while maintaining the benefits of blockchain-based reputation tracking!** 🎉

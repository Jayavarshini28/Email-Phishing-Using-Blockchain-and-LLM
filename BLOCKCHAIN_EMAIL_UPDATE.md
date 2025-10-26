# Blockchain Storage Update: Domain → Sender Email

## Overview
Updated the system to store **sender email addresses** instead of **domains** in the blockchain. This prevents false positives when legitimate senders use common domains (e.g., forms.gle).

## Problem Solved
**Before:** A spammer sends from `spammer@gmail.com` with a `forms.gle` link → System stores `forms.gle` as spam → Later, a verified sender sends `forms.gle` link → Incorrectly flagged as spam.

**After:** System stores `spammer@gmail.com` as spam → Verified sender with different email is analyzed independently → No false positive.

## Key Changes

### 1. Smart Contract (`DomainReputation.sol`)
- ✅ Updated comments to clarify it now stores **sender email addresses**
- ✅ Contract name kept as `DomainClassification` for backward compatibility
- ✅ The `domain` parameter now accepts email addresses
- ✅ All functions updated with new documentation

### 2. Backend Core (`utils.py`)
- ✅ `compute_final_risk()` - Now queries blockchain by **sender email** only
- ✅ Added `force_llm` parameter to allow fresh LLM analysis even when blockchain data exists
- ✅ `get_blockchain_domain_reputation()` - Now queries sender email, adds `from_previous_incident` flag
- ✅ `store_classification_to_blockchain()` - Now stores sender email instead of domain
- ✅ Returns sender reputation data instead of domain reputation data

### 3. Backend API (`app.py`)
- ✅ `/analyze` endpoint - Added `force_llm` parameter for fresh analysis
- ✅ `auto_report_domains_to_blockchain()` - Now reports sender email only
- ✅ `/blockchain/bulk-report` - User feedback now reports sender email
- ✅ `/blockchain/bulk-store` - Admin endpoint now stores sender email
- ✅ Response includes `from_previous_incident` flag

### 4. Blockchain Integration (`interact.js`)
- ✅ Updated console logs to reference "sender email" instead of "domain"
- ✅ Classification and query functions work with email addresses

### 5. Chrome Extension (`content_script.js`)
- ✅ **NEW FEATURE:** Shows warning when classification is based on previous incidents
- ✅ **NEW FEATURE:** "Run Fresh LLM Analysis" button appears when blockchain data exists
- ✅ Updated UI to show sender reputation instead of domain reputation
- ✅ Feedback system now reports sender email to blockchain

### 6. Extension Background (`background.js`)
- ✅ Passes `force_llm` parameter to backend
- ✅ Returns blockchain signals and sender reputation data

## New User Experience

### Scenario 1: First Time Analysis
1. User receives email from `unknown@suspicious.com`
2. System runs ML + LLM analysis
3. Classified as spam (confidence 85%)
4. **Sender email** `unknown@suspicious.com` stored in blockchain
5. User sees normal analysis result

### Scenario 2: Sender Has Previous Incidents
1. User receives email from `unknown@suspicious.com` (same spammer)
2. System queries blockchain → **Finds previous incident**
3. Shows warning: "⚠️ Based on Previous Incidents - This sender was previously marked as spam"
4. Skips expensive LLM analysis (uses blockchain data)
5. User can click **"Run Fresh LLM Analysis"** if they think it's incorrect
6. Can still submit feedback to update classification

### Scenario 3: User Overrides Blockchain
1. User sees "Based on Previous Incidents" warning
2. Clicks **"Run Fresh LLM Analysis"** button
3. System runs fresh LLM analysis with `force_llm=true`
4. Shows new analysis result
5. User can submit feedback to update blockchain

### Scenario 4: Verified Sender with Common Domain
1. Verified user sends email from `verified@company.com` with `forms.gle` link
2. Even if `forms.gle` was reported as spam before, **sender email is different**
3. System runs fresh analysis (no false positive)
4. Email analyzed independently

## Technical Implementation

### Blockchain Query Strategy
```python
# OLD: Query all domains from email
domains = extract_domains_from_urls(urls) + [sender_domain]
for domain in domains:
    reputation = get_blockchain_domain_reputation(domain)

# NEW: Query sender email only
sender_email = extract_email_from_sender(sender)
reputation = get_blockchain_domain_reputation(sender_email)
```

### Force LLM Analysis
```python
# User can force fresh LLM analysis
final_risk, details = compute_final_risk(
    body=body, 
    sender=sender, 
    subject=subject,
    force_llm=True  # Bypass blockchain, run fresh LLM
)
```

### UI Warning System
```javascript
// Show warning when blockchain data exists
if (fromPreviousIncident && !forceLlmUsed) {
    // Display: "Based on Previous Incidents"
    // Show: "Run Fresh LLM Analysis" button
}
```

## API Changes

### Request to `/analyze`
```json
{
  "sender": "user@example.com",
  "subject": "Email subject",
  "body": "Email content",
  "force_llm": false  // NEW: Set to true to force fresh LLM analysis
}
```

### Response from `/analyze`
```json
{
  "final_risk": 0.85,
  "llm_reason": "Analysis reason...",
  "from_previous_incident": true,  // NEW: Indicates blockchain data was used
  "force_llm_used": false,         // NEW: Whether fresh LLM was run
  "sender_reputation": {           // NEW: Sender's blockchain reputation
    "exists": true,
    "consensus": "spam",
    "reputation_score": 10,
    "from_previous_incident": true
  },
  "blockchain_signals": {
    "blockchain_available": true,
    "sender_classification": {     // NEW: Sender classification details
      "classification": "spam",
      "confidence": 0.9,
      "reputation_score": 10
    }
  }
}
```

## Migration Notes

### No Database Migration Needed
- Smart contract parameter names kept for backward compatibility
- The `domain` variable now stores email addresses
- Existing blockchain data (if any) will work but represents old domain-based entries

### Redeployment Required
1. **Smart Contract** - Redeploy `DomainReputation.sol` to blockchain
2. **Backend** - Restart Flask application
3. **Extension** - Reload extension in browser

### Breaking Changes
- **NONE** - All changes are backward compatible
- Old API responses still work, new fields are added

## Testing Checklist

- [ ] Smart contract compiles successfully
- [ ] Backend starts without errors
- [ ] Extension loads in Chrome
- [ ] First-time email analysis works
- [ ] Sender email stored in blockchain
- [ ] Second email from same sender shows "Previous Incidents" warning
- [ ] "Run Fresh LLM Analysis" button appears and works
- [ ] User feedback submits sender email to blockchain
- [ ] Different sender with same domain analyzed independently

## Benefits

1. ✅ **No more false positives** from common domains (forms.gle, bit.ly, etc.)
2. ✅ **Sender-specific tracking** - Each email address has its own reputation
3. ✅ **User control** - Can override blockchain with fresh LLM analysis
4. ✅ **Transparency** - Users see when classification is based on previous incidents
5. ✅ **Faster analysis** - Skip LLM when blockchain data exists (unless user forces it)
6. ✅ **Better accuracy** - Legitimate senders on same domains won't be flagged

## Files Modified

### Smart Contract
- `backend/blockchain/contracts/DomainReputation.sol`

### Backend
- `backend/utils.py`
- `backend/app.py`
- `backend/blockchain/interact.js`

### Extension
- `phish-analyzer-extension/content_script.js`
- `phish-analyzer-extension/background.js`

---

**Status:** ✅ **COMPLETE - All changes implemented and ready for testing**

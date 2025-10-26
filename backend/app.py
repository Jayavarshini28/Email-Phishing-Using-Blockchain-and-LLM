from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from utils import compute_final_risk, store_classification_to_blockchain, extract_domain_from_email
# from blockchain_integration import get_blockchain_instance
from blockchain_integration import get_blockchain_instance  
import logging
import re
from urllib.parse import urlparse
import sys

app = Flask(__name__)
CORS(app)  # allow cross-origin calls from extension (restrict in production)

# Fix Flask reloader issue by excluding node_modules from watchdog
if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
    # Only configure on main process, not reloader subprocess
    import pathlib
    exclude_patterns = ['**/node_modules/**', '**/blockchain/node_modules/**', '**/__pycache__/**']
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_KEY = os.environ.get("EXT_API_KEY", "")
print(f"API KEY: {API_KEY}")

# Admin-only blockchain settings
AUTO_REPORT_TO_BLOCKCHAIN = os.environ.get("AUTO_REPORT_CONFIDENT_CLASSIFICATIONS", "true").lower() == "true"
MIN_CONFIDENCE_FOR_BLOCKCHAIN = float(os.environ.get("MIN_CONFIDENCE_FOR_BLOCKCHAIN_REPORT", "0.8"))

def extract_domains_from_content(content):
    """Extract domains from email content"""
    if not content:
        return []
    
    # Find URLs in content
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+|www\.[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, content, re.IGNORECASE)
    
    domains = set()
    for url in urls:
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            parsed = urlparse(url)
            if parsed.netloc:
                domain = parsed.netloc.lower()
                # Remove www. prefix
                if domain.startswith('www.'):
                    domain = domain[4:]
                domains.add(domain)
        except Exception as e:
            logger.warning(f"Could not parse URL {url}: {e}")
            continue
    
    return list(domains)

def auto_report_domains_to_blockchain(domains, final_risk, llm_reason="", sender=""):
    """Automatically report sender email to blockchain if confidence is high enough
    NOTE: 'domains' parameter is now used for sender email for backward compatibility
    """
    if not AUTO_REPORT_TO_BLOCKCHAIN:
        logger.info("Auto-reporting to blockchain is disabled")
        return
    
    # Extract sender email from sender parameter
    sender_email = sender
    if not sender_email:
        logger.info("No sender email provided for auto-reporting")
        return
    
    # Clean sender email
    if '@' in sender_email:
        # Handle format like "Name <email@domain.com>"
        if '<' in sender_email and '>' in sender_email:
            sender_email = sender_email.split('<')[1].split('>')[0].strip()
        sender_email = sender_email.lower()
    else:
        logger.info("Invalid sender email format")
        return
    
    # Determine if this should be reported as spam based on risk score
    is_spam = final_risk >= MIN_CONFIDENCE_FOR_BLOCKCHAIN
    confidence = final_risk if is_spam else (1 - final_risk)
    
    # Only report if we're confident enough
    if confidence < MIN_CONFIDENCE_FOR_BLOCKCHAIN:
        logger.info(f"Confidence {confidence:.2f} below threshold {MIN_CONFIDENCE_FOR_BLOCKCHAIN}, not reporting to blockchain")
        return
    
    # Prepare reason for blockchain
    classification_type = "spam/phishing" if is_spam else "legitimate"
    reason = f"System classification: {classification_type} (confidence: {confidence:.2f})"
    if llm_reason:
        reason += f" - {llm_reason[:200]}"  # Limit reason length
    if sender:
        reason += f" - From: {sender}"
    
    # Report sender email
    try:
        logger.info(f"Auto-reporting sender email '{sender_email}' as {classification_type} to blockchain")
        success, message = store_classification_to_blockchain(
            domain=sender_email,  # Using domain parameter for sender email
            is_spam=is_spam,
            reason=reason,
            final_risk_score=final_risk
        )
        
        if success:
            logger.info(f"✅ Successfully reported {sender_email} to blockchain")
        else:
            logger.warning(f"❌ Failed to report {sender_email} to blockchain: {message}")
            
    except Exception as e:
        logger.error(f"Error reporting sender email {sender_email} to blockchain: {e}")

@app.route('/')
def home():
    """Health check endpoint"""
    blockchain = get_blockchain_instance()   
    blockchain_status = blockchain.get_connection_status()
    
    return jsonify({
        "status": "Phishing analyzer is running",
        "blockchain_connected": blockchain_status.get("connected", False),
        "auto_reporting": AUTO_REPORT_TO_BLOCKCHAIN,
        "min_confidence": MIN_CONFIDENCE_FOR_BLOCKCHAIN
    })

@app.route("/analyze", methods=["POST"])
def analyze():
    """Main email analysis endpoint with automatic blockchain reporting"""
    # Simple API key check (improve in prod)
    if API_KEY:
        key = request.headers.get("x-api-key", "")
        print(f"Request API KEY: {key}")
        if key != API_KEY:
            return jsonify({"error": "invalid api key"}), 403

    data = request.get_json() or {}
    sender = data.get("sender", "")
    subject = data.get("subject", "")
    body = data.get("body", "")
    urls = data.get("urls", [])
    force_llm = data.get("force_llm", False)  # New parameter to force LLM analysis
    
    logger.info(f"Analyzing email from {sender} with subject: {subject[:50]}... (force_llm={force_llm})")
    
    # Call your compute_final_risk which returns (final_risk, details)
    final_risk, details = compute_final_risk(body, sender=sender, subject=subject, force_llm=force_llm)
    
    # Ensure actions exist
    actions = details.get("llm_actions") or details.get("actions") or ["No actions required"]
    llm_reason = details.get("llm_reason", "")
    
    # Auto-report sender email to blockchain if enabled and confidence is high
    # Only auto-report if NOT force_llm (i.e., this is initial analysis)
    if sender and not force_llm:
        logger.info(f"Sender email: {sender}")
        try:
            auto_report_domains_to_blockchain(
                domains=[],  # Not used anymore, kept for compatibility
                final_risk=final_risk,
                llm_reason=llm_reason,
                sender=sender
            )
        except Exception as e:
            logger.error(f"Error in auto-reporting to blockchain: {e}")
    
    # Respond with sanitized JSON including blockchain data
    resp = {
        "final_risk": final_risk,
        "details": details,
        "llm_actions": actions,
        "llm_reason": llm_reason,
        "blockchain_signals": details.get("blockchain_signals", {}),
        "sender_classification": details.get("blockchain_signals", {}).get("sender_classification", {}),
        "blockchain_weight": details.get("blockchain_weight", 0.0),
        "blockchain_available": details.get("blockchain_signals", {}).get("blockchain_available", False),
        "sender_reputation": details.get("sender_reputation", {}),
        "from_previous_incident": details.get("blockchain_signals", {}).get("from_previous_incident", False),
        "force_llm_used": force_llm
    }
    
    logger.info(f"Analysis complete: risk={final_risk:.3f}, from_previous_incident={resp['from_previous_incident']}")
    return jsonify(resp)

@app.route("/blockchain/status", methods=["GET"])
def blockchain_status():
    """Get blockchain connection status"""
    blockchain = get_blockchain_instance()
    status = blockchain.get_connection_status()
    
    # Add admin-specific information
    status.update({
        "auto_reporting_enabled": AUTO_REPORT_TO_BLOCKCHAIN,
        "min_confidence_threshold": MIN_CONFIDENCE_FOR_BLOCKCHAIN,
        "mode": "admin_only"
    })
    
    return jsonify(status)

@app.route("/blockchain/reputation/<domain>", methods=["GET"])
def get_domain_classification(domain):
    """Get classification for a specific domain"""
    if API_KEY:
        key = request.headers.get("x-api-key", "")
        if key != API_KEY:
            return jsonify({"error": "invalid api key"}), 403
    
    blockchain = get_blockchain_instance()
    classification = blockchain.get_domain_classification(domain)
    return jsonify(classification)

@app.route("/blockchain/store", methods=["POST"])
def store_domain():
    """Store a domain classification to blockchain (admin endpoint)"""
    if API_KEY:
        key = request.headers.get("x-api-key", "")
        if key != API_KEY:
            return jsonify({"error": "invalid api key"}), 403
    
    data = request.get_json() or {}
    domain = data.get("domain", "")
    is_spam = data.get("is_spam", False)
    reason = data.get("reason", "Manual admin classification")
    final_risk_score = data.get("final_risk_score")
    
    if not domain:
        return jsonify({"error": "Domain is required"}), 400
    
    logger.info(f"Manual admin classification: {domain} -> {'spam' if is_spam else 'ham'}")
    
    success, message = store_classification_to_blockchain(domain, is_spam, reason, final_risk_score)
    
    return jsonify({
        "success": success,
        "message": message,
        "domain": domain,
        "classification": "spam" if is_spam else "ham",
        "source": "manual_admin"
    })

@app.route("/blockchain/bulk-store", methods=["POST"])
def bulk_store_domains():
    """Store sender email from analysis result (admin endpoint)"""
    if API_KEY:
        key = request.headers.get("x-api-key", "")
        if key != API_KEY:
            return jsonify({"error": "invalid api key"}), 403
    
    data = request.get_json() or {}
    analysis_result = data.get("analysis_result", {})
    user_classification = data.get("user_classification", "ham")  # "spam" or "ham"
    reason = data.get("reason", "Bulk admin classification from email analysis")
    
    final_risk = analysis_result.get("final_risk", 0.5)
    
    # Extract sender email
    sender = analysis_result.get("sender", "")
    if not sender:
        return jsonify({"error": "No sender email found in analysis result"}), 400
    
    # Clean sender email
    sender_email = sender
    if '@' in sender:
        if '<' in sender and '>' in sender:
            sender_email = sender.split('<')[1].split('>')[0].strip()
        sender_email = sender_email.lower()
    
    logger.info(f"Bulk storing sender email {sender_email} as {user_classification}")
    
    is_spam = user_classification == "spam"
    
    success, message = store_classification_to_blockchain(sender_email, is_spam, reason, final_risk)
    
    return jsonify({
        "results": [{
            "sender_email": sender_email,
            "success": success,
            "message": message
        }],
        "classification": user_classification,
        "successful_stores": 1 if success else 0,
        "source": "bulk_admin"
    })

@app.route("/blockchain/bulk-report", methods=["POST"])
def bulk_report_domains():
    """
    User feedback endpoint: Report sender email to blockchain based on user classification
    """
    if API_KEY:
        key = request.headers.get("x-api-key", "")
        if key != API_KEY:
            return jsonify({"error": "invalid api key"}), 403
    
    data = request.get_json() or {}
    analysis_result = data.get("analysis_result", {})
    user_classification = data.get("user_classification", "ham")  # "spam" or "ham"
    reason = data.get("reason", "User feedback from browser extension")
    
    # Debug: Log the received data structure
    logger.info(f"📥 Received feedback request:")
    logger.info(f"   Classification: {user_classification}")
    logger.info(f"   Analysis result keys: {list(analysis_result.keys()) if isinstance(analysis_result, dict) else 'Not a dict'}")
    
    # Extract sender email from analysis result
    sender = (
        analysis_result.get("sender") or 
        (analysis_result.get("details", {}).get("sender") if isinstance(analysis_result, dict) else None)
    )
    
    logger.info(f"   Sender found: {sender}")
    
    if not sender or "@" not in sender:
        logger.warning("⚠️ No valid sender email found in user feedback request")
        logger.warning(f"   Full data structure: {data}")
        return jsonify({
            "error": "No sender email found to report",
            "hint": "Make sure the email analysis includes sender email address",
            "successful_reports": 0
        }), 400
    
    # Clean sender email
    sender_email = sender
    if '<' in sender and '>' in sender:
        # Handle format like: "Name <email@domain.com>"
        sender_email = sender.split("<")[1].split(">")[0]
    
    sender_email = sender_email.strip().lower()
    
    logger.info(f"📊 User feedback: Reporting sender email '{sender_email}' as {user_classification}")
    
    # Report sender email to blockchain
    is_spam = user_classification == "spam"
    final_risk = analysis_result.get("final_risk", 0.9 if is_spam else 0.1)
    
    success, message = store_classification_to_blockchain(
        domain=sender_email,
        is_spam=is_spam,
        reason=reason,
        final_risk_score=final_risk
    )
    
    if success:
        logger.info(f"✅ Reported {sender_email} as {user_classification}")
    else:
        logger.warning(f"❌ Failed to report {sender_email}: {message}")
    
    return jsonify({
        "results": [{
            "sender_email": sender_email,
            "success": success,
            "message": message
        }],
        "classification": user_classification,
        "successful_reports": 1 if success else 0,
        "sender_reported": sender_email if success else None,
        "source": "user_feedback"
    })

@app.route("/admin/blockchain/report", methods=["POST"])
def admin_force_report():
    """Force report domains to blockchain (admin-only endpoint)"""
    if API_KEY:
        key = request.headers.get("x-api-key", "")
        if key != API_KEY:
            return jsonify({"error": "invalid api key"}), 403
    
    data = request.get_json() or {}
    domains = data.get("domains", [])
    is_spam = data.get("is_spam", False)
    reason = data.get("reason", "Admin force report")
    final_risk = data.get("final_risk", 0.9 if is_spam else 0.1)
    
    if not domains:
        return jsonify({"error": "Domains list is required"}), 400
    
    logger.info(f"Admin force reporting {len(domains)} domains as {'spam' if is_spam else 'ham'}")
    
    results = []
    for domain in domains:
        success, message = store_classification_to_blockchain(domain, is_spam, reason, final_risk)
        results.append({
            "domain": domain,
            "success": success,
            "message": message
        })
    
    return jsonify({
        "results": results,
        "classification": "spam" if is_spam else "ham",
        "total_domains": len(domains),
        "successful_reports": sum(1 for r in results if r["success"]),
        "source": "admin_force"
    })

@app.route("/admin/stats", methods=["GET"])
def admin_stats():
    """Get admin statistics"""
    if API_KEY:
        key = request.headers.get("x-api-key", "")
        if key != API_KEY:
            return jsonify({"error": "invalid api key"}), 403
    
    # This would require additional tracking in your system
    # For now, return basic configuration info
    return jsonify({
        "auto_reporting_enabled": AUTO_REPORT_TO_BLOCKCHAIN,
        "min_confidence_threshold": MIN_CONFIDENCE_FOR_BLOCKCHAIN,
        "mode": "admin_only_system",
        "blockchain_connected": get_blockchain_instance().get_connection_status().get("connected", False)
    })

if __name__ == "__main__":
    # Initialize blockchain connection on startup
    try:
        blockchain = get_blockchain_instance()
        status = blockchain.get_connection_status()
        if status.get("connected"):
            logger.info(f"✅ Connected to blockchain: {status.get('provider_url')}")
            if status.get("contract_address"):
                logger.info(f"✅ Contract loaded: {status.get('contract_address')}")
        else:
            logger.warning("❌ Blockchain connection failed - running in offline mode")
    except Exception as e:
        logger.error(f"❌ Blockchain initialization error: {e}")
    
    logger.info(f"🚀 Starting Email Phishing Detection Backend")
    logger.info(f"📊 Auto-reporting: {AUTO_REPORT_TO_BLOCKCHAIN}")
    logger.info(f"🎯 Min confidence: {MIN_CONFIDENCE_FOR_BLOCKCHAIN}")
    
    # Run with reloader that excludes node_modules to prevent OSError
    extra_files = []
    extra_dirs = []
    
    # Use stat reloader instead of watchdog to avoid socket errors
    app.run(
        host="0.0.0.0",
        port=8080,
        debug=True,
        use_reloader=True,
        reloader_type='stat',  # Use stat reloader instead of watchdog
        extra_files=extra_files,
        exclude_patterns=['**/node_modules/**', '**/blockchain/node_modules/**']
    )
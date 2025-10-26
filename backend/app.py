from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from utils import compute_final_risk, store_classification_to_blockchain, get_domains_from_analysis_result
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
    """Automatically report domains to blockchain if confidence is high enough"""
    if not AUTO_REPORT_TO_BLOCKCHAIN:
        logger.info("Auto-reporting to blockchain is disabled")
        return
    
    if not domains:
        logger.info("No domains to report")
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
    
    # Report each domain
    for domain in domains:
        try:
            logger.info(f"Auto-reporting domain '{domain}' as {classification_type} to blockchain")
            success, message = store_classification_to_blockchain(
                domain=domain,
                is_spam=is_spam,
                reason=reason,
                final_risk_score=final_risk
            )
            
            if success:
                logger.info(f"✅ Successfully reported {domain} to blockchain")
            else:
                logger.warning(f"❌ Failed to report {domain} to blockchain: {message}")
                
        except Exception as e:
            logger.error(f"Error reporting domain {domain} to blockchain: {e}")

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
    
    logger.info(f"Analyzing email from {sender} with subject: {subject[:50]}...")
    
    # Call your compute_final_risk which returns (final_risk, details)
    final_risk, details = compute_final_risk(body, sender=sender, subject=subject)
    
    # Ensure actions exist
    actions = details.get("llm_actions") or details.get("actions") or ["No actions required"]
    llm_reason = details.get("llm_reason", "")
    
    # Extract domains from email content for auto-reporting
    email_content = f"{subject} {body} {' '.join(urls)}"
    domains = extract_domains_from_content(email_content)
    
    # Auto-report domains to blockchain if enabled and confidence is high
    if domains:
        logger.info(f"Found {len(domains)} domains: {domains}")
        try:
            auto_report_domains_to_blockchain(
                domains=domains,
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
        "domain_classifications": details.get("domain_classifications", {}),
        "blockchain_weight": details.get("blockchain_weight", 0.0),  # Add blockchain_weight to response
        "blockchain_available": details.get("blockchain_signals", {}).get("blockchain_available", False),
        "domain_reputations": details.get("domain_reputations", {}),  # Add domain reputations for UI
        "auto_reported_domains": domains if AUTO_REPORT_TO_BLOCKCHAIN else [],
        "domains_found": len(domains)
    }
    
    logger.info(f"Analysis complete: risk={final_risk:.3f}, domains={len(domains)}")
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
    """Store multiple domains from analysis result (admin endpoint)"""
    if API_KEY:
        key = request.headers.get("x-api-key", "")
        if key != API_KEY:
            return jsonify({"error": "invalid api key"}), 403
    
    data = request.get_json() or {}
    analysis_result = data.get("analysis_result", {})
    user_classification = data.get("user_classification", "ham")  # "spam" or "ham"
    reason = data.get("reason", "Bulk admin classification from email analysis")
    
    final_risk = analysis_result.get("final_risk", 0.5)
    domains = get_domains_from_analysis_result(analysis_result)
    
    if not domains:
        return jsonify({"error": "No domains found in analysis result"}), 400
    
    logger.info(f"Bulk storing {len(domains)} domains as {user_classification}")
    
    results = []
    is_spam = user_classification == "spam"
    
    for domain in domains:
        success, message = store_classification_to_blockchain(domain, is_spam, reason, final_risk)
        results.append({
            "domain": domain,
            "success": success,
            "message": message
        })
    
    return jsonify({
        "results": results,
        "classification": user_classification,
        "total_domains": len(domains),
        "successful_stores": sum(1 for r in results if r["success"]),
        "source": "bulk_admin"
    })

@app.route("/blockchain/bulk-report", methods=["POST"])
def bulk_report_domains():
    """
    User feedback endpoint: Report domains to blockchain based on user classification
    Extracts sender domain and URL domains from email analysis
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
    
    # Extract domains from analysis result
    domains = []
    
    # 1. Extract sender domain from email (check multiple possible locations)
    sender = (
        analysis_result.get("sender") or 
        (analysis_result.get("details", {}).get("sender") if isinstance(analysis_result, dict) else None)
    )
    
    logger.info(f"   Sender found: {sender}")
    
    if sender and "@" in sender:
        # Extract domain from email address (handle <email> format too)
        email_match = sender
        if "<" in sender and ">" in sender:
            # Handle format like: "Name <email@domain.com>"
            email_match = sender.split("<")[1].split(">")[0]
        
        sender_domain = email_match.split("@")[-1].strip().lower()
        # Clean up any trailing characters
        sender_domain = sender_domain.rstrip('>').strip()
        
        if sender_domain:
            domains.append(sender_domain)
            logger.info(f"📧 Extracted sender domain: {sender_domain}")
    
    # 2. Extract domains from the analysis details
    details = analysis_result.get("details", {}) if isinstance(analysis_result, dict) else {}
    
    # Try to get domains from various locations in details
    if isinstance(details, dict):
        # Direct domains field
        if "domains" in details and details["domains"]:
            url_domains = details.get("domains", [])
            domains.extend(url_domains)
            logger.info(f"🔗 Found {len(url_domains)} domains in details.domains: {url_domains}")
        
        # URLs field - extract domains from URLs
        if "urls" in details and details["urls"]:
            urls = details.get("urls", [])
            logger.info(f"🌐 Found {len(urls)} URLs, extracting domains...")
            for url in urls:
                try:
                    if not url.startswith(('http://', 'https://')):
                        url = 'http://' + url
                    parsed = urlparse(url)
                    if parsed.netloc:
                        domain = parsed.netloc.lower()
                        if domain.startswith('www.'):
                            domain = domain[4:]
                        if ':' in domain:  # Remove port
                            domain = domain.split(':')[0]
                        if domain:
                            domains.append(domain)
                            logger.info(f"   Extracted from URL: {domain}")
                except Exception as e:
                    logger.warning(f"   Could not parse URL {url}: {e}")
        
        # Blockchain signals
        blockchain_signals = details.get("blockchain_signals", {})
        if isinstance(blockchain_signals, dict):
            domain_classifications = blockchain_signals.get("domain_classifications", {})
            if domain_classifications:
                domains.extend(domain_classifications.keys())
                logger.info(f"⛓️ Found {len(domain_classifications)} domains in blockchain signals")
    
    # Remove duplicates and empty strings
    domains = list(set(filter(None, domains)))
    
    if not domains:
        logger.warning("⚠️ No domains found in user feedback request")
        logger.warning(f"   Full data structure: {data}")
        return jsonify({
            "error": "No domains found to report",
            "hint": "Make sure the email analysis includes sender or URLs",
            "total_domains": 0,
            "successful_reports": 0
        }), 400
    
    logger.info(f"📊 User feedback: Reporting {len(domains)} domain(s) as {user_classification}")
    logger.info(f"📝 Domains to report: {domains}")
    
    # Report each domain to blockchain
    results = []
    is_spam = user_classification == "spam"
    final_risk = analysis_result.get("final_risk", 0.9 if is_spam else 0.1)
    
    import time
    
    for idx, domain in enumerate(domains):
        # Add small delay between submissions to avoid cooldown issues
        if idx > 0:
            time.sleep(0.5)  # 500ms delay between submissions
            
        success, message = store_classification_to_blockchain(
            domain=domain,
            is_spam=is_spam,
            reason=reason,
            final_risk_score=final_risk
        )
        results.append({
            "domain": domain,
            "success": success,
            "message": message
        })
        
        if success:
            logger.info(f"✅ Reported {domain} as {user_classification}")
        else:
            logger.warning(f"❌ Failed to report {domain}: {message}")
    
    successful_reports = sum(1 for r in results if r["success"])
    
    return jsonify({
        "results": results,
        "classification": user_classification,
        "total_domains": len(domains),
        "successful_reports": successful_reports,
        "domains_reported": [r["domain"] for r in results if r["success"]],
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
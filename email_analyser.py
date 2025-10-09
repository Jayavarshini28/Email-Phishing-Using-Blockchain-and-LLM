# Create this NEW file:
# filepath: e:\Projects\Email - Phishing\Email-Phishing-Using-Blockchain-and-LLM\email_analyzer.py

import re
from urllib.parse import urlparse
from blockchain_wrapper import check_domain_reputation, report_domain
import logging

logger = logging.getLogger(__name__)

def extract_domain_from_email(email_data):
    """Extract primary domain from email content"""
    email_content = email_data.get('body', '') + ' ' + email_data.get('subject', '')
    
    # Find URLs in email
    url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
    urls = re.findall(url_pattern, email_content)
    
    # Extract domains
    for url in urls:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if domain:
                return domain
        except:
            continue
    
    # If no URLs, try to extract domain from sender
    sender = email_data.get('sender', '')
    if '@' in sender:
        return sender.split('@')[1].lower()
    
    return None

def analyze_email_with_blockchain(email_data):
    """
    Analyze email with blockchain integration
    This is the NEW function that connects everything!
    """
    # Step 1: Extract domain from email
    domain = extract_domain_from_email(email_data)
    
    if not domain:
        # No domain found, run ML analysis only
        return run_ml_analysis(email_data)
    
    # Step 2: Check blockchain FIRST (using your perfect wrapper!)
    logger.info(f"Checking blockchain for domain: {domain}")
    blockchain_result = check_domain_reputation(domain)
    
    if blockchain_result is not None:
        # Found in blockchain - instant result!
        classification = 'SPAM' if blockchain_result else 'HAM'
        logger.info(f"Blockchain provided instant result: {domain} = {classification}")
        
        return {
            'classification': classification,
            'confidence': 1.0,
            'source': 'blockchain',
            'domain': domain,
            'reason': f'Known domain from blockchain cache'
        }
    
    # Step 3: Not in blockchain - run ML analysis
    logger.info(f"Domain {domain} not in blockchain, running ML analysis")
    ml_result = run_ml_analysis(email_data)
    
    # Step 4: Store high-confidence results (using your perfect wrapper!)
    if ml_result.get('confidence', 0) > 0.8:
        is_spam = ml_result['classification'] == 'SPAM'
        reason = f"ML confidence: {ml_result['confidence']:.2f}"
        
        logger.info(f"Storing high-confidence result: {domain} = {ml_result['classification']}")
        success = report_domain(domain, is_spam, reason)
        
        if success:
            ml_result['stored_to_blockchain'] = True
        else:
            ml_result['stored_to_blockchain'] = False
    
    return ml_result

def run_ml_analysis(email_data):
    """
    Your existing ML analysis function
    Replace this with your actual ML code!
    """
    # TODO: Replace with your actual ML analysis
    # This is just a placeholder
    
    # For now, return a dummy result
    # In reality, this would run your ML models
    return {
        'classification': 'HAM',  # or 'SPAM'
        'confidence': 0.85,
        'source': 'ml',
        'reason': 'ML analysis completed'
    }

# Main function for email processing
def process_email(email_data):
    """
    Main email processing function
    Use this in your email system!
    """
    try:
        result = analyze_email_with_blockchain(email_data)
        logger.info(f"Email processing complete: {result}")
        return result
    except Exception as e:
        logger.error(f"Email processing failed: {e}")
        return {
            'classification': 'UNKNOWN',
            'confidence': 0.0,
            'source': 'error',
            'error': str(e)
        }
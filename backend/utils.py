import os
import subprocess
import logging
import warnings
import pandas as pd
import pickle
import re
import numpy as np
from email import policy
from email.parser import BytesParser
from urllib.parse import urlparse
from typing import Dict, Any, Optional, List, Tuple

# Suppress warnings
from sklearn.exceptions import InconsistentVersionWarning
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

logger = logging.getLogger(__name__)

# Load models and data
try:
    with open('files/X_train_encoded_columns.pkl', 'rb') as f:
        X_train_encoded_columns = pickle.load(f)
    logger.info("✅ Loaded encoded columns")
except Exception as e:
    logger.error(f"❌ Failed to load encoded columns: {e}")
    X_train_encoded_columns = []

# Import URL utilities
try:
    from url_utils import extract_localhost_features, extract_generic_features
    logger.info("✅ Loaded URL utilities")
except ImportError as e:
    logger.warning(f"⚠️ URL utilities not available: {e}")
    def extract_localhost_features(url): return []
    def extract_generic_features(url): return []

# Load URL model
try:
    with open('files/random_forest_url_model.pkl', 'rb') as f:
        url_model = pickle.load(f)
    logger.info("✅ Loaded URL model")
except Exception as e:
    logger.error(f"❌ Failed to load URL model: {e}")
    url_model = None

# Load embedding model and classifier
try:
    from sentence_transformers import SentenceTransformer
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    logger.info("✅ Loaded embedding model")
except Exception as e:
    logger.error(f"❌ Failed to load embedding model: {e}")
    embedding_model = None

try:
    with open('files/email_log_reg_embed_model.pkl', 'rb') as f:
        content_model = pickle.load(f)
    logger.info("✅ Loaded content model")
except Exception as e:
    logger.error(f"❌ Failed to load content model: {e}")
    content_model = None

# LLM setup
from dotenv import load_dotenv
load_dotenv()

GENINI_MODEL_NAME = "gemini-2.5-flash"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        llm_model = genai.GenerativeModel(GENINI_MODEL_NAME)
        logger.info("✅ LLM model configured")
    except Exception as e:
        logger.error(f"❌ Failed to configure LLM: {e}")
        llm_model = None
else:
    logger.warning("⚠️ GEMINI_API_KEY not found")
    llm_model = None

# Constants
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

def parse_email_content(raw_email: str) -> Dict[str, str]:
    """Parse raw email content and extract components"""
    try:
        if isinstance(raw_email, str):
            raw_email = raw_email.encode('utf-8')
        
        msg = BytesParser(policy=policy.default).parsebytes(raw_email)
        
        # Extract text content
        body_text = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body_text += part.get_content()
        else:
            if msg.get_content_type() == "text/plain":
                body_text = msg.get_content()
        
        return {
            "sender": msg.get("From", ""),
            "subject": msg.get("Subject", ""),
            "body": body_text,
            "date": msg.get("Date", ""),
            "to": msg.get("To", ""),
            "reply_to": msg.get("Reply-To", "")
        }
    except Exception as e:
        logger.error(f"Error parsing email: {e}")
        return {
            "sender": "",
            "subject": "",
            "body": raw_email if isinstance(raw_email, str) else str(raw_email),
            "date": "",
            "to": "",
            "reply_to": ""
        }

def extract_urls_from_content(content: str) -> List[str]:
    """Extract URLs from email content"""
    if not content:
        return []
    
    # URL pattern to match http/https URLs
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, content, re.IGNORECASE)
    
    # Also match www. URLs
    www_pattern = r'www\.[^\s<>"{}|\\^`\[\]]+'
    www_urls = re.findall(www_pattern, content, re.IGNORECASE)
    
    # Add http:// prefix to www URLs
    www_urls = ['http://' + url for url in www_urls]
    
    return list(set(urls + www_urls))

def extract_domains_from_urls(urls: List[str]) -> List[str]:
    """Extract domains from list of URLs"""
    domains = []
    for url in urls:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            if domain and domain not in domains:
                domains.append(domain)
        except Exception as e:
            logger.error(f"Error parsing URL {url}: {e}")
    return domains

def analyze_content_with_ml(content: str) -> Tuple[float, float]:
    """Analyze content using ML models"""
    try:
        if not content or not embedding_model or not content_model:
            logger.warning("Content analysis not available")
            return 0.5, 0.5
        
        # Generate embedding
        embedding = embedding_model.encode([content])
        
        # Get prediction
        proba = content_model.predict_proba(embedding)[0]
        confidence = max(proba)
        spam_prob = proba[1] if len(proba) > 1 else proba[0]
        
        return spam_prob, confidence
    except Exception as e:
        logger.error(f"Error in ML content analysis: {e}")
        return 0.5, 0.5

def analyze_urls_with_ml(urls: List[str]) -> float:
    """Analyze URLs using ML model"""
    try:
        if not urls or not url_model:
            return 0.5
        
        url_scores = []
        for url in urls:
            try:
                # Extract features (simplified)
                features = extract_generic_features(url) + extract_localhost_features(url)
                if not features:
                    features = [len(url), url.count('.'), url.count('/'), 0, 0]
                
                # Pad or truncate features to match model expectations
                expected_features = 50  # Adjust based on your model
                if len(features) < expected_features:
                    features.extend([0] * (expected_features - len(features)))
                else:
                    features = features[:expected_features]
                
                # Get prediction
                features_array = np.array(features).reshape(1, -1)
                score = url_model.predict_proba(features_array)[0][1]
                url_scores.append(score)
            except Exception as e:
                logger.error(f"Error analyzing URL {url}: {e}")
                url_scores.append(0.5)
        
        return np.mean(url_scores) if url_scores else 0.5
    except Exception as e:
        logger.error(f"Error in URL analysis: {e}")
        return 0.5

def analyze_with_llm(content: str, sender: str = "", subject: str = "") -> Tuple[float, str, float]:
    """Analyze email using LLM"""
    try:
        if not llm_model:
            return 0.5, "LLM not available", 0.5
        
        prompt = f"""
        Analyze this email for phishing indicators. Provide a risk score from 0.0 (safe) to 1.0 (definitely phishing).

        Subject: {subject}
        From: {sender}
        Content: {content[:1000]}...

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
        
        response = llm_model.generate_content(prompt)
        text = response.text
        
        # Parse response
        risk_score = 0.5
        reason = "Analysis completed"
        confidence = 0.5
        
        for line in text.split('\n'):
            if 'RISK_SCORE:' in line:
                try:
                    risk_score = float(re.findall(r'[0-9\.]+', line)[0])
                    risk_score = max(0.0, min(1.0, risk_score))
                except:
                    pass
            elif 'REASON:' in line:
                reason = line.split('REASON:')[-1].strip()
            elif 'CONFIDENCE:' in line:
                try:
                    confidence = float(re.findall(r'[0-9\.]+', line)[0])
                    confidence = max(0.0, min(1.0, confidence))
                except:
                    pass
        
        return risk_score, reason, confidence
    except Exception as e:
        logger.error(f"Error in LLM analysis: {e}")
        return 0.5, f"LLM analysis failed: {str(e)}", 0.5

def get_blockchain_domain_reputation(domain: str) -> Dict:
    """Get sender email reputation from blockchain (domain parameter name kept for compatibility)"""
    try:
        script_path = os.path.join(os.path.dirname(__file__), 'blockchain', 'interact.js')
        if not os.path.exists(script_path):
            logger.warning(f"Blockchain script not found at: {script_path}")
            return {"exists": False}
        
        # Use UTF-8 encoding to avoid Windows CP1252 Unicode errors
        result = subprocess.run(
            ['node', script_path, 'query', domain],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',  # Ignore Unicode decode errors
            timeout=15,  # Increased from 10 to 15 seconds
            cwd=os.path.dirname(script_path)  # Set working directory to blockchain folder
        )
        
        if result.returncode == 0 and result.stdout:
            # Extract ONLY the last line (which is the classification)
            # This ignores all the debug/emoji output from interact.js
            lines = result.stdout.strip().split('\n')
            classification = lines[-1].strip() if lines else ''
            
            logger.debug(f"Blockchain query output for {domain}: {len(lines)} lines, last='{classification}'")
            
            if classification in ['SPAM', 'HAM']:
                logger.info(f"✅ Found blockchain record for sender {domain}: {classification}")
                return {
                    "exists": True,
                    "reputation_score": 10 if classification == 'SPAM' else 90,
                    "consensus": classification.lower(),
                    "spam_votes": 1 if classification == 'SPAM' else 0,
                    "ham_votes": 1 if classification == 'HAM' else 0,
                    "total_reports": 1,
                    "source": "blockchain",
                    "from_previous_incident": True  # Flag to indicate this is from historical data
                }
            else:
                logger.info(f"No blockchain record for sender {domain} (got '{classification}')")
                return {"exists": False}
        else:
            if result.stderr:
                logger.warning(f"Blockchain query stderr: {result.stderr[:100]}")
            return {"exists": False}
    except subprocess.TimeoutExpired:
        logger.warning(f"⏱️ Blockchain query timeout for {domain}")
        return {"exists": False}
    except Exception as e:
        logger.error(f"Error querying blockchain: {e}")
        return {"exists": False}

def store_classification_to_blockchain(domain: str, is_spam: bool, reason: str, final_risk_score: Optional[float] = None) -> Tuple[bool, str]:
    """Store sender email classification to blockchain (domain parameter name kept for compatibility)"""
    try:
        script_path = os.path.join(os.path.dirname(__file__), 'blockchain', 'interact.js')
        if not os.path.exists(script_path):
            logger.warning(f"Blockchain script not found at: {script_path}")
            return False, "Blockchain script not available"
        
        classification = 'true' if is_spam else 'false'
        
        # Truncate reason to avoid command line length issues
        truncated_reason = reason[:200] if len(reason) > 200 else reason
        
        logger.info(f"Attempting blockchain storage for sender email {domain} (spam={is_spam})")
        
        # Use UTF-8 encoding to avoid Windows CP1252 Unicode errors
        # Increased timeout to 60 seconds for blockchain transactions
        result = subprocess.run(
            ['node', script_path, 'classify', domain, classification, truncated_reason],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',  # Ignore Unicode decode errors
            timeout=60,  # Increased from 30 to 60 seconds
            cwd=os.path.dirname(script_path)  # Set working directory to blockchain folder
        )
        
        if result.returncode == 0:
            logger.info(f"✅ Successfully stored sender email {domain} as {classification}")
            return True, f"Sender email {domain} stored as {classification}"
        else:
            error_msg = result.stderr[:200] if result.stderr else "Unknown error"
            logger.error(f"❌ Failed to store {domain}: {error_msg}")
            return False, f"Storage failed: {error_msg}"
    except subprocess.TimeoutExpired:
        logger.warning(f"⏱️ Blockchain storage timeout for {domain} - transaction may still complete")
        return False, f"Blockchain transaction timeout (may still complete in background)"
    except Exception as e:
        logger.error(f"Error storing to blockchain: {e}")
        return False, f"Error: {e}"

# def report_domain_to_blockchain(domain: str, is_spam: bool, reason: str, final_risk_score: Optional[float] = None) -> Tuple[bool, str]:
#     """Report domain to blockchain - alias for store_classification_to_blockchain"""
#     return store_classification_to_blockchain(domain, is_spam, reason, final_risk_score)

def extract_domains_from_urls(urls: List[str]) -> List[str]:
    """Extract clean domains from list of URLs"""
    domains = []
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
                # Remove port if present
                if ':' in domain:
                    domain = domain.split(':')[0]
                if domain:
                    domains.append(domain)
        except Exception as e:
            logger.warning(f"Could not parse URL {url}: {e}")
            continue
    return domains

def extract_domain_from_email(email_address: str) -> Optional[str]:
    """Extract domain from email address"""
    try:
        if '@' in email_address:
            domain = email_address.split('@')[-1].strip().lower()
            # Remove any trailing > or brackets
            domain = domain.rstrip('>').strip()
            return domain if domain else None
    except Exception as e:
        logger.warning(f"Could not extract domain from email {email_address}: {e}")
    return None

def get_domains_from_analysis_result(analysis_result: Dict) -> List[str]:
    """
    Extract all domains from analysis result including:
    1. Sender email domain
    2. URL domains from email body
    3. Domains from blockchain signals
    """
    domains = []
    try:
        # 1. Extract sender domain from email address
        sender = analysis_result.get("sender", "")
        if sender:
            sender_domain = extract_domain_from_email(sender)
            if sender_domain:
                domains.append(sender_domain)
                logger.debug(f"Extracted sender domain: {sender_domain}")
        
        # 2. Extract from details if available
        details = analysis_result.get("details", {})
        if "domains" in details:
            domains.extend(details.get("domains", []))
        
        # 3. Extract from URLs
        if "urls" in details:
            extracted_domains = extract_domains_from_urls(details.get("urls", []))
            domains.extend(extracted_domains)
        
        # 4. Extract from blockchain_signals
        blockchain_signals = details.get("blockchain_signals", {})
        if blockchain_signals:
            domain_classifications = blockchain_signals.get("domain_classifications", {})
            domains.extend(domain_classifications.keys())
            
    except Exception as e:
        logger.error(f"Error extracting domains from analysis result: {e}")
    
    # Remove duplicates, empty strings, and None values
    unique_domains = list(set(filter(None, domains)))
    logger.info(f"Extracted {len(unique_domains)} unique domain(s): {unique_domains}")
    
    return unique_domains

def compute_final_risk(body: str, sender: str = "", subject: str = "", force_llm: bool = False) -> Tuple[float, Dict[str, Any]]:
    """Compute final risk score using all available methods
    
    Args:
        body: Email body content
        sender: Sender email address
        subject: Email subject
        force_llm: If True, always run LLM analysis even if blockchain data exists
    """
    try:
        logger.info("Computing final risk score...")
        
        # Initialize components
        content_prob = 0.5
        content_conf = 0.5
        url_prob = 0.5
        llm_score = 0.5
        llm_reason = "No analysis performed"
        llm_conf = 0.5
        
        # Extract URLs and domains
        full_content = f"{subject} {body}"
        urls = extract_urls_from_content(full_content)
        logger.info(f"Extracted {len(urls)} URLs from content")
        
        domains = extract_domains_from_urls(urls)
        
        logger.info(f"Total URL domains found: {domains}")
        
        # ===== BLOCKCHAIN FIRST STRATEGY (CHECK SENDER EMAIL) =====
        # Check blockchain for SENDER EMAIL ONLY, not domains
        # If blockchain has classification for sender, show it but allow LLM override
        blockchain_weight = 0.0
        blockchain_spam_signal = False
        blockchain_ham_signal = False
        sender_reputation = {}
        sender_classification = {}
        blockchain_found = False
        from_previous_incident = False
        
        # Clean sender email
        sender_email = sender
        if sender and '@' in sender:
            # Handle format like "Name <email@domain.com>"
            if '<' in sender and '>' in sender:
                sender_email = sender.split('<')[1].split('>')[0].strip()
            sender_email = sender_email.lower()
            
            logger.info(f"🔍 Checking blockchain for sender email: {sender_email}")
            reputation = get_blockchain_domain_reputation(sender_email)
            sender_reputation = reputation
            logger.info(f"Blockchain query for sender '{sender_email}': exists={reputation.get('exists', False)}, consensus={reputation.get('consensus', 'none')}")
            
            if reputation.get("exists", False):
                blockchain_found = True
                from_previous_incident = reputation.get("from_previous_incident", False)
                is_spam = reputation.get("consensus") == "spam"
                
                if is_spam:
                    blockchain_spam_signal = True
                else:
                    blockchain_ham_signal = True
                
                sender_classification = {
                    "classification": "spam" if is_spam else "ham",
                    "confidence": 0.9,
                    "reputation_score": reputation.get("reputation_score", 50),
                    "from_previous_incident": from_previous_incident
                }
        
        # If blockchain found and NOT forcing LLM, use blockchain classification
        if blockchain_found and not force_llm:
            logger.info("✅ Blockchain classification found for sender - using previous incident data")
            blockchain_weight = 0.7  # HIGH weight when blockchain data exists
            llm_reason = f"Based on previous incidents, this sender was marked as {'spam' if blockchain_spam_signal else 'legitimate'}. Click 'Run LLM Analysis' if you think this is incorrect."
            llm_conf = 0.9
            # LLM score matches blockchain (0.0 for HAM, 1.0 for SPAM)
            llm_score = 1.0 if blockchain_spam_signal else 0.0
        else:
            if blockchain_found and force_llm:
                logger.info("⚠️ Blockchain data found but force_llm=True - running fresh LLM analysis...")
            else:
                logger.info("⚠️ No blockchain data for sender - running LLM analysis...")
            # LLM Analysis (if blockchain not found OR force_llm is True)
            llm_score, llm_reason, llm_conf = analyze_with_llm(body, sender, subject)
            logger.info(f"LLM analysis: score={llm_score:.3f}, conf={llm_conf:.3f}")
            
            # If we forced LLM, reduce blockchain weight
            if blockchain_found and force_llm:
                blockchain_weight = 0.2  # Lower weight when user explicitly requests fresh analysis
        
        # ML Content Analysis (lightweight, always run)
        if body:
            content_prob, content_conf = analyze_content_with_ml(body)
            logger.info(f"Content analysis: prob={content_prob:.3f}, conf={content_conf:.3f}")
        
        # ML URL Analysis (lightweight, always run)
        if urls:
            url_prob = analyze_urls_with_ml(urls)
            logger.info(f"URL analysis: prob={url_prob:.3f}")
        
        # Compute weighted final score
        if blockchain_found and not force_llm:
            # When blockchain data exists and not forcing LLM, trust it heavily
            weights = {
                'content': 0.1,
                'url': 0.1,
                'llm': 0.1,  # Minimal weight (llm_score matches blockchain anyway)
                'blockchain': 0.7  # HIGH trust in blockchain consensus
            }
        elif blockchain_found and force_llm:
            # When forcing LLM despite blockchain, balance between fresh analysis and history
            weights = {
                'content': 0.2,
                'url': 0.2,
                'llm': 0.4,  # Trust fresh LLM analysis more
                'blockchain': 0.2  # Some weight to blockchain history
            }
        else:
            # When no blockchain data, rely on ML + LLM
            weights = {
                'content': 0.3,
                'url': 0.2,
                'llm': 0.5,
                'blockchain': 0.0
            }
        
        # Normalize weights
        total_weight = sum(weights.values())
        weights = {k: v/total_weight for k, v in weights.items()}
        
        # Calculate blockchain contribution to risk score
        blockchain_risk = 0.5  # Default neutral if no blockchain data
        if blockchain_spam_signal:
            blockchain_risk = 1.0  # High risk if marked as spam
        elif blockchain_ham_signal:
            blockchain_risk = 0.0  # Low risk if marked as legitimate
        
        # Calculate final score
        final_risk = (
            weights['content'] * content_prob +
            weights['url'] * url_prob +
            weights['llm'] * llm_score +
            weights['blockchain'] * blockchain_risk
        )
        
        logger.info(f"Score breakdown: content={content_prob:.3f}*{weights['content']:.2f}, url={url_prob:.3f}*{weights['url']:.2f}, llm={llm_score:.3f}*{weights['llm']:.2f}, blockchain={blockchain_risk:.3f}*{weights['blockchain']:.2f}")
        
        # Prepare detailed results
        details = {
            "content_prob": float(content_prob),
            "content_conf": float(content_conf),
            "url_prob": float(url_prob),
            "ml_score": float((content_prob + url_prob) / 2),
            "llm_safe_score": float(1.0 - llm_score),
            "llm_conf": float(llm_conf),
            "llm_reason": llm_reason,
            "llm_actions": [llm_reason] if llm_reason else [],
            "blockchain_weight": float(blockchain_weight),
            "sender_reputation": sender_reputation,
            "blockchain_signals": {
                "blockchain_available": blockchain_weight > 0,
                "sender_classification": sender_classification,
                "from_previous_incident": from_previous_incident
            },
            "urls": urls,
            "domains": domains,
            "weights": weights,
            "sender": sender,
            "force_llm_used": force_llm
        }
        
        logger.info(f"Final risk score: {final_risk:.3f}")
        return float(final_risk), details
        
    except Exception as e:
        logger.error(f"Error computing final risk: {e}")
        # Return safe defaults
        return 0.5, {
            "error": str(e),
            "content_prob": 0.5,
            "url_prob": 0.5,
            "ml_score": 0.5,
            "llm_safe_score": 0.5,
            "llm_conf": 0.5,
            "blockchain_weight": 0.0,
            "domain_reputations": {},
            "blockchain_signals": {"blockchain_available": False, "domain_classifications": {}},
            "llm_actions": ["Analysis failed"],
            "llm_reason": f"Error: {str(e)}",
            "urls": [],
            "domains": []
        }
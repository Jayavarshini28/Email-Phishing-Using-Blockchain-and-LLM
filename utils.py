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
    """Get domain reputation from blockchain"""
    try:
        script_path = os.path.join(os.path.dirname(__file__), 'blockchain', 'interact.js')
        if not os.path.exists(script_path):
            logger.warning("Blockchain script not found")
            return {"exists": False}
        
        result = subprocess.run(
            ['node', script_path, 'query', domain],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            classification = result.stdout.strip()
            if classification in ['SPAM', 'HAM']:
                return {
                    "exists": True,
                    "reputation_score": 10 if classification == 'SPAM' else 90,
                    "consensus": classification.lower(),
                    "spam_votes": 1 if classification == 'SPAM' else 0,
                    "ham_votes": 1 if classification == 'HAM' else 0,
                    "total_reports": 1
                }
            else:
                return {"exists": False}
        else:
            logger.error(f"Blockchain query failed: {result.stderr}")
            return {"exists": False}
    except Exception as e:
        logger.error(f"Error querying blockchain: {e}")
        return {"exists": False}

def store_classification_to_blockchain(domain: str, is_spam: bool, reason: str, final_risk_score: Optional[float] = None) -> Tuple[bool, str]:
    """Store classification to blockchain"""
    try:
        script_path = os.path.join(os.path.dirname(__file__), 'blockchain', 'interact.js')
        if not os.path.exists(script_path):
            logger.warning("Blockchain script not found")
            return False, "Blockchain script not available"
        
        classification ='true' if is_spam else 'false'
        
        result = subprocess.run(
            ['node', script_path, 'classify', domain, classification, reason],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0:
            logger.info(f"Successfully stored {domain} as {classification}")
            return True, f"Domain {domain} stored as {classification}"
        else:
            logger.error(f"Failed to store {domain}: {result.stderr}")
            return False, f"Storage failed: {result.stderr}"
    except Exception as e:
        logger.error(f"Error storing to blockchain: {e}")
        return False, f"Error: {e}"

# def report_domain_to_blockchain(domain: str, is_spam: bool, reason: str, final_risk_score: Optional[float] = None) -> Tuple[bool, str]:
#     """Report domain to blockchain - alias for store_classification_to_blockchain"""
#     return store_classification_to_blockchain(domain, is_spam, reason, final_risk_score)

def get_domains_from_analysis_result(analysis_result: Dict) -> List[str]:
    """Extract domains from analysis result"""
    domains = []
    try:
        # Extract from blockchain_signals
        blockchain_signals = analysis_result.get("blockchain_signals", {})
        domain_classifications = blockchain_signals.get("domain_classifications", {})
        domains.extend(domain_classifications.keys())
        
        # Extract from details if available
        details = analysis_result.get("details", {})
        if "domains" in details:
            domains.extend(details["domains"])
        
        # Extract from URLs
        if "urls" in details:
            extracted_domains = extract_domains_from_urls(details["urls"])
            domains.extend(extracted_domains)
            
    except Exception as e:
        logger.error(f"Error extracting domains from analysis result: {e}")
    
    return list(set(domains))  # Remove duplicates

def compute_final_risk(body: str, sender: str = "", subject: str = "") -> Tuple[float, Dict[str, Any]]:
    """Compute final risk score using all available methods"""
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
        domains = extract_domains_from_urls(urls)
        
        # ML Content Analysis
        if body:
            content_prob, content_conf = analyze_content_with_ml(body)
            logger.info(f"Content analysis: prob={content_prob:.3f}, conf={content_conf:.3f}")
        
        # ML URL Analysis
        if urls:
            url_prob = analyze_urls_with_ml(urls)
            logger.info(f"URL analysis: prob={url_prob:.3f}")
        
        # LLM Analysis
        llm_score, llm_reason, llm_conf = analyze_with_llm(body, sender, subject)
        logger.info(f"LLM analysis: score={llm_score:.3f}, conf={llm_conf:.3f}")
        
        # Blockchain Analysis
        blockchain_weight = 0.0
        domain_reputations = {}
        domain_classifications = {}
        
        for domain in domains:
            reputation = get_blockchain_domain_reputation(domain)
            domain_reputations[domain] = reputation
            if reputation.get("exists", False):
                blockchain_weight = 0.3  # Increase weight if we have blockchain data
                is_spam = reputation.get("consensus") == "spam"
                domain_classifications[domain] = {
                    "classification": "spam" if is_spam else "ham",
                    "confidence": 0.9,
                    "reputation_score": reputation.get("reputation_score", 50)
                }
        
        # Compute weighted final score
        weights = {
            'content': 0.3,
            'url': 0.2,
            'llm': 0.5 - blockchain_weight,
            'blockchain': blockchain_weight
        }
        
        # Normalize weights
        total_weight = sum(weights.values())
        weights = {k: v/total_weight for k, v in weights.items()}
        
        # Calculate final score
        final_risk = (
            weights['content'] * content_prob +
            weights['url'] * url_prob +
            weights['llm'] * llm_score +
            weights['blockchain'] * (1.0 if any(rep.get("consensus") == "spam" for rep in domain_reputations.values()) else 0.0)
        )
        
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
            "domain_reputations": domain_reputations,
            "blockchain_signals": {
                "blockchain_available": blockchain_weight > 0,
                "domain_classifications": domain_classifications
            },
            "urls": urls,
            "domains": domains,
            "weights": weights
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
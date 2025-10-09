import re
import numpy as np
import pandas as pd
from email import policy
from email.parser import BytesParser
import pickle
import subprocess
import json
import os

# Suppress warnings
import warnings
from sklearn.exceptions import InconsistentVersionWarning

# Suppress sklearn model pickle warnings
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

# Load encoded column names for training set
with open('files/X_train_encoded_columns.pkl', 'rb') as f:
    X_train_encoded_cols = pickle.load(f)

# Feature extraction functions
from url_utils import extract_localhost_features, extract_generic_features

# Load models that are necessary
with open('files/random_forest_url_model.pkl', 'rb') as f:
    random_forest = pickle.load(f)
# with open('files/nb_email_model.pkl', 'rb') as f:
#     email_naive_bayes = pickle.load(f)

# Load TF IDF Vectorizer
# with open('files/tfidf_vectorizer.pkl', 'rb') as f:
#     tfidf_vectorizer = pickle.load(f)

# Constants
feature_names = ['scheme',
 'netloc',
 'path',
 'query',
 'hostname',
 'port',
 'qty_._url',
 'qty_-_url',
 'qty___url',
 'qty_/_url',
 'qty_?_url',
 'qty_=_url',
 'qty_@_url',
 'qty_&_url',
 'qty_!_url',
 'qty_space_url',
 'qty_~_url',
 'qty_,_url',
 'qty_+_url',
 'qty_*_url',
 'qty_#_url',
 'qty_$_url',
 'qty_%_url',
 'length_url',
 'qty_._domain',
 'qty_-_domain',
 'qty___domain',
 'qty_/_domain',
 'qty_?_domain',
 'qty_=_domain',
 'qty_@_domain',
 'qty_&_domain',
 'qty_!_domain',
 'qty_space_domain',
 'qty_~_domain',
 'qty_,_domain',
 'qty_+_domain',
 'qty_*_domain',
 'qty_#_domain',
 'qty_$_domain',
 'qty_%_domain',
 'qty_vowels_domain',
 'domain_length',
 'domain_in_ip',
 'server_client_domain',
 'qty_._directory',
 'qty_-_directory',
 'qty___directory',
 'qty_/_directory',
 'qty_?_directory',
 'qty_=_directory',
 'qty_@_directory',
 'qty_&_directory',
 'qty_!_directory',
 'qty_space_directory',
 'qty_~_directory',
 'qty_,_directory',
 'qty_+_directory',
 'qty_*_directory',
 'qty_#_directory',
 'qty_$_directory',
 'qty_%_directory',
 'directory_length',
 'qty_._file',
 'qty_-_file',
 'qty___file',
 'qty_/_file',
 'qty_?_file',
 'qty_=_file',
 'qty_@_file',
 'qty_&_file',
 'qty_!_file',
 'qty_space_file',
 'qty_~_file',
 'qty_,_file',
 'qty_+_file',
 'qty_*_file',
 'qty_#_file',
 'qty_$_file',
 'qty_%_file',
 'file_length',
 'qty_._params',
 'qty_-_params',
 'qty___params',
 'qty_/_params',
 'qty_?_params',
 'qty_=_params',
 'qty_@_params',
 'qty_&_params',
 'qty_!_params',
 'qty_space_params',
 'qty_~_params',
 'qty_,_params',
 'qty_+_params',
 'qty_*_params',
 'qty_#_params',
 'qty_$_params',
 'qty_%_params',
 'params_length',
 'tld_present_params',
 'qty_params',
 'email_in_url']
non_numeric_cols = ['scheme', 'netloc', 'path', 'query', 'hostname']


def extract_urls_from_email(email_text):
    """
    Extracts URLs carefully from email content using regex.
    Handles cases with punctuation and angle brackets.
    """
    url_pattern = r'https?://[^\s<>"\'\]]+'
    urls = re.findall(url_pattern, email_text)
    return [url.strip('.,;!?') for url in urls]  # remove trailing punctuation

def classify_url_proba(url):
    """
    Returns phishing probability for a single URL using the trained Random Forest.
    Applies the same preprocessing pipeline as training.
    """
    # Step 1: Extract features
    if 'localhost' in url or '127.0.0.1' in url:
        features = extract_localhost_features(url)
    else:
        features = extract_generic_features(url)

    df_single = pd.DataFrame([features], columns=feature_names)

    # Step 2: One-hot encode categorical columns
    df_encoded = pd.get_dummies(df_single, columns=non_numeric_cols)

    # Step 3: Align with training columns
    aligned = pd.DataFrame(0, index=[0], columns=X_train_encoded_cols)
    for col in df_encoded.columns:
        if col in aligned.columns:
            aligned[col] = df_encoded[col].iloc[0]

    # Step 4: Get probability from Random Forest
    prob = random_forest.predict_proba(aligned)[0][1]
    return prob


# def classify_email_proba(email_text):
#     """
#     Returns spam probability for an email using the trained Naive Bayes model.
#     """
#     email_features = tfidf_vectorizer.transform([email_text])
#     spam_index = list(email_naive_bayes.classes_).index("spam")
#     prob = email_naive_bayes.predict_proba(email_features)[0][spam_index]
#     return prob

# Necessary of Embeddings + Linear Classifier
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
with open('files/email_log_reg_embed_model.pkl', 'rb') as f:
    email_log_reg_embed = pickle.load(f)

def classify_email_proba(email_text):
    # Generate embedding for the single email content
    # The encode method expects an iterable, so pass the string in a list
    email_embedding = embedding_model.encode([email_text])

    # Get predicted probabilities using the Logistic Regression model
    # The output is a numpy array of shape (1, num_labels) with probabilities
    probabilities = email_log_reg_embed.predict_proba(email_embedding)

    # Find the index corresponding to the 'spam' class
    # This assumes the model's classes_ attribute is ordered consistently ('ham', 'spam') or similar
    # You might need to confirm the order or map it explicitly if needed
    try:
        spam_index = list(email_log_reg_embed.classes_).index("spam")
    except ValueError:
        print("Error: 'spam' class not found in the model's classes.")
        # Handle this error, perhaps return a default probability or raise an exception
        return 0.0 # Return 0 probability as a fallback


    # Extract the probability for the 'spam' class
    prob = probabilities[0][spam_index]

    return prob

def parse_rfc5322(raw_email_bytes):
    """
    Parses a raw RFC5322 email into subject, headers, and body text.
    """
    msg = BytesParser(policy=policy.default).parsebytes(raw_email_bytes)

    subject = msg['subject']
    from_addr = msg['from']
    to_addr = msg['to']
    
    # Extract plain text + HTML body
    body_parts = []
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type in ["text/plain", "text/html"]:
                try:
                    body_parts.append(part.get_content())
                except:
                    continue
    else:
        body_parts.append(msg.get_content())

    body_text = "\n".join([str(bp) for bp in body_parts if bp])
    return subject, from_addr, to_addr, body_text

# --- LLM Sanity Check ---
import google.generativeai as genai
import os, json
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load .env file
load_dotenv()

GENINI_MODEL_NAME = "gemini-1.5-flash"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# def llm_safe_score_full(sender, subject, body, urls, base_signals):
#     """
#     Ask Gemini to reason on the actual email contents + metadata.
#     Returns (safe_score, reason).
#     """
#     if not GEMINI_API_KEY:
#         return 0.5, "LLM disabled, returning neutral safe score."

#     # Limit body size for API
#     preview_body = body[:2000] if body else "(empty)"

#     url_domains = []
#     for u in urls:
#         try:
#             d = urlparse(u).hostname
#             if d:
#                 url_domains.append(d)
#         except:
#             continue
#     url_domains = list(set(url_domains))

#     prompt = f"""
# You are a cybersecurity assistant. You will receive ONLY privacy-minimized metadata.
# Estimate how SAFE this email is based on whether the sender and link domains look like well-known, legitimate services.
# Return:
# - safe_score: float between 0 and 1
# - reason: concise explanation (<= 2 lines)

# Email Data:
# From: {sender}
# Subject: {subject}
# URL Domains: {", ".join(url_domains) if url_domains else "none"}
# Base signals: {base_signals}

# Body (truncated):
# {preview_body}

# Rules:
# - Give 0.9–1.0 if it clearly matches a real service/legitimate content.
# - 0.6–0.8 if it looks okay but uncertain.
# - 0.3–0.5 if suspicious wording, unusual domains.
# - 0.0–0.2 if clear phishing attempt.
# Reply strictly in JSON:
# {{"safe_score": <float>, "reason": "<string>"}}
# """

#     model = genai.GenerativeModel(GENINI_MODEL_NAME)
#     resp = model.generate_content(prompt)
#     text = (resp.text or "").strip()
#     # print(text)ko

#     try:
#         # Remove markdown fences if present
#         cleaned = text.strip()
#         if cleaned.startswith("```json"):
#             cleaned = cleaned[len("```json"):].strip()
#         if cleaned.endswith("```"):
#             cleaned = cleaned[:-3].strip()

#         data = json.loads(cleaned)
#         score = float(data.get("safe_score", 0.5))
#         reason = str(data.get("reason", "No reason")).strip()
#         return max(0.0, min(1.0, score)), reason
#     except Exception as e:
#         return 0.5, f"LLM parse error: {e}, returning neutral safe score."

def get_blockchain_classifications(url_domains):
    """Simple blockchain lookup using JavaScript tools"""
    classifications = {}
    blockchain_signals = {
        'blockchain_available': False,
        'domains_checked': 0,
        'domains_found': 0,
        'cache_hits': 0
    }
    
    if not url_domains:
        return classifications, blockchain_signals
    
    # Use JavaScript interact script for blockchain queries
    script_path = os.path.join(os.path.dirname(__file__), 'blockchain', 'interact.js')
    
    for domain in url_domains:
        try:
            result = subprocess.run(
                ['node', script_path, 'query', domain],
                capture_output=True, text=True, timeout=10
            )
            
            if 'SPAM' in result.stdout:
                classifications[domain] = {
                    'exists': True, 'is_spam': True, 'blockchain_available': True
                }
                blockchain_signals['domains_found'] += 1
            elif 'HAM' in result.stdout:
                classifications[domain] = {
                    'exists': True, 'is_spam': False, 'blockchain_available': True
                }
                blockchain_signals['domains_found'] += 1
            else:
                classifications[domain] = {
                    'exists': False, 'is_spam': False, 'blockchain_available': True
                }
            
            blockchain_signals['blockchain_available'] = True
            blockchain_signals['domains_checked'] += 1
            
        except Exception as e:
            print(f"Blockchain query failed for {domain}: {e}")
            classifications[domain] = {
                'exists': False, 'is_spam': False, 'blockchain_available': False
            }
    
    return classifications, blockchain_signals

def store_classification_to_blockchain(domain, is_spam, reason="", final_risk_score=None):
    """Store classification using JavaScript tools"""
    script_path = os.path.join(os.path.dirname(__file__), 'blockchain', 'interact.js')
    
    try:
        enhanced_reason = reason
        if final_risk_score is not None:
            enhanced_reason = f"{reason} (Risk Score: {final_risk_score:.3f})"
        
        result = subprocess.run(
            ['node', script_path, 'classify', domain, str(is_spam).lower(), enhanced_reason],
            capture_output=True, text=True, timeout=30
        )
        
        if 'Transaction confirmed' in result.stdout:
            return True, f"Successfully stored {domain}"
        else:
            return False, "Failed to store classification"
            
    except Exception as e:
        return False, f"Blockchain storage error: {e}"

# --- LLM Sanity Check ---
import google.generativeai as genai
import os, json
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load .env file
load_dotenv()

GENINI_MODEL_NAME = "gemini-1.5-flash"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def llm_safe_score_full(sender, subject, body, urls, base_signals, known_domains=None, blockchain_data=None):
    """
    Ask Gemini to reason on the actual email contents + metadata.
    Returns (safe_score, reason).
    """

    if not GEMINI_API_KEY:
        return 0.5, "LLM disabled, returning neutral safe score."

    preview_body = body[:2000] if body else "(empty)"

    # --- Extract URL domains
    url_domains = []
    for u in urls:
        try:
            d = urlparse(u).hostname
            if d:
                url_domains.append(d.lower())
        except:
            continue
    url_domains = list(set(url_domains))

    # --- Heuristic features (non-hardcoded)
    suspicious_domains = []
    for d in url_domains:
        # digits inside domain
        if re.search(r"\d", d):
            suspicious_domains.append(d)
        # punycode domains
        if d.startswith("xn--"):
            suspicious_domains.append(d)
        # long random-looking subdomain
        parts = d.split(".")
        if len(parts[0]) > 15 and re.search(r"[a-z]{5,}\d{2,}", parts[0]):
            suspicious_domains.append(d)

    # Compare sender vs. URL domains
    sender_domain = sender.split("@")[-1].lower() if "@" in sender else None
    mismatch_flag = sender_domain and any(sd not in sender_domain for sd in url_domains)

    # Known domains reference (optional external file)
    known_match = False
    if known_domains:
        for d in url_domains:
            if any(d.endswith(kd) for kd in known_domains):
                known_match = True

    heuristic_flags = {
        "suspicious_domains": suspicious_domains,
        "sender_domain": sender_domain,
        "mismatch_sender_url": mismatch_flag,
        "known_domain_match": known_match,
    }

    # --- Prompt for LLM
    blockchain_info = ""
    if blockchain_data and blockchain_data.get('blockchain_available'):
        cached_domains = blockchain_data.get('cached_domains', 0)
        unknown_domains = blockchain_data.get('unknown_domains', 0)
        
        blockchain_info = f"""
Blockchain Cache Data:
- Blockchain Available: {blockchain_data.get('blockchain_available', False)}
- Cached Domains: {cached_domains} (found in blockchain cache)
- Unknown Domains: {unknown_domains} (not in cache, analyzed with ML)

Domain Classifications from Cache:"""
        
        # Add individual domain data if available
        domain_details = blockchain_data.get('domain_details', {})
        for domain, cls_data in domain_details.items():
            if cls_data.get('exists'):
                classification = "SPAM" if cls_data.get('is_spam') else "HAM"
                timestamp = cls_data.get('timestamp', 0)
                blockchain_info += f"""
  {domain}: {classification} (cached, stored: {timestamp})"""
            else:
                blockchain_info += f"""
  {domain}: Not in cache (analyzed with ML)"""

    prompt = f"""
You are a cybersecurity assistant. You will receive privacy-minimized metadata + heuristics + blockchain cache data.
Estimate how SAFE this email is. Provide necessary actions that can be taken care by the user if its suspicious or phish.

Email Metadata:
From: {sender}
Subject: {subject}
Sender Domain: {sender_domain}
URL Domains: {", ".join(url_domains) if url_domains else "none"}
Base signals: {base_signals}
Heuristic Flags: {heuristic_flags}
{blockchain_info}

Body (truncated):
{preview_body}

Rules:
- Blockchain cache contains previous community classifications (SPAM/HAM)
- If domains are cached as SPAM, increase suspicion significantly
- If domains are cached as HAM, increase confidence in legitimacy
- Unknown domains (not cached) rely on ML analysis signals
- 0.9–1.0 → clear legitimate service/content (known domains, cached as HAM, no flags)
- 0.6–0.8 → looks fine but some uncertainty
- 0.3–0.5 → suspicious heuristics or mismatch, mixed cache results
- 0.0–0.2 → clear phishing attempt (cached as SPAM, malicious patterns)

Reply strictly in JSON:
{{
  "safe_score": <float>,
  "reason": "<string>",
  "actions": [
    "1. <first recommended step>",
    "2. <second recommended step>",
    "3. <third recommended step>"
  ]
}}
"""

    model = genai.GenerativeModel(GENINI_MODEL_NAME)
    resp = model.generate_content(prompt)
    text = (resp.text or "").strip()

    try:
        cleaned = text
        if cleaned.startswith("```json"):
            cleaned = cleaned[len("```json"):].strip()
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()

        data = json.loads(cleaned)
        score = float(data.get("safe_score", 0.5))
        reason = str(data.get("reason", "No reason")).strip()
        actions = data.get("actions", ["No actions required"])
        return max(0.0, min(1.0, score)), reason, actions
    except Exception as e:
        return 0.5, f"LLM parse error: {e}, returning neutral safe score.", "No actions required"


def compute_final_risk(email_text, sender=None, subject=None, w1=0.6, w2=0.4):
    # --- Extract URL domains first ---
    urls = extract_urls_from_email(email_text)
    url_domains = []
    for u in urls:
        try:
            d = urlparse(u).hostname
            if d:
                url_domains.append(d.lower())
        except:
            continue
    url_domains = list(set(url_domains))

    # --- BLOCKCHAIN CACHE LOOKUP FIRST ---
    domain_classifications, blockchain_signals = get_blockchain_classifications(url_domains)
    
    # Check if any domains have cached classifications
    cached_classifications = {}
    unknown_domains = []
    
    for domain in url_domains:
        cls_data = domain_classifications.get(domain, {})
        if cls_data.get('exists', False):
            # Domain found in blockchain cache
            cached_classifications[domain] = cls_data
        else:
            # Domain not in cache, needs ML analysis
            unknown_domains.append(domain)
    
    # --- ML ANALYSIS ---
    content_prob = classify_email_proba(email_text)  # phishing prob from text
    
    # Only run URL analysis for unknown domains
    if unknown_domains:
        url_probs = []
        for url in urls:
            try:
                domain = urlparse(url).hostname.lower()
                if domain in unknown_domains:
                    url_probs.append(classify_url_proba(url))
            except:
                continue
        url_prob = np.mean(url_probs) if url_probs else 0.0
    else:
        # Use cached classifications for URL risk
        cached_spam_count = sum(1 for cls in cached_classifications.values() if cls.get('is_spam', False))
        total_cached = len(cached_classifications)
        url_prob = (cached_spam_count / total_cached) if total_cached > 0 else 0.0
    
    ml_score = (w1 * content_prob) + (w2 * url_prob)

    base_signals = {
        "content_prob": round(content_prob, 3),
        "url_prob": round(url_prob, 3),
        "blockchain_available": blockchain_signals['blockchain_available'],
        "cached_domains": len(cached_classifications),
        "unknown_domains": len(unknown_domains)
    }

    # --- LLM REASONING with blockchain context ---
    blockchain_data = blockchain_signals.copy()
    blockchain_data['domain_details'] = domain_classifications

    safe_score, reason, actions = llm_safe_score_full(
        sender, subject, email_text, urls, base_signals, 
        blockchain_data=blockchain_data
    )
    llm_risk = 1 - safe_score

    # --- FINAL RISK CALCULATION ---
    # If we have cached classifications, use them to influence the score
    blockchain_risk_factor = 0.5  # Default neutral
    blockchain_weight = 0.0
    
    if cached_classifications:
        # Calculate risk based on cached spam classifications
        spam_domains = sum(1 for cls in cached_classifications.values() if cls.get('is_spam', False))
        total_cached = len(cached_classifications)
        blockchain_risk_factor = spam_domains / total_cached if total_cached > 0 else 0.5
        blockchain_weight = 0.4  # Give significant weight to cached data
    
    # Adaptive LLM weight
    llm_conf = abs(safe_score - 0.5) * 2
    w_llm = 0.5 + (0.5 * llm_conf)
    
    # Normalize weights
    total_w = w1 + w2 + w_llm + blockchain_weight
    final_risk = (
        w1 * content_prob + 
        w2 * url_prob + 
        w_llm * llm_risk + 
        blockchain_weight * blockchain_risk_factor
    ) / total_w

    # --- STORE NEW CLASSIFICATIONS TO BLOCKCHAIN ---
    # Store final classification for unknown domains
    if unknown_domains and blockchain_signals['blockchain_available']:
        classification_threshold = 0.6  # Domains above this are considered spam
        for domain in unknown_domains:
            is_spam = final_risk > classification_threshold
            reason_text = f"ML+LLM analysis result (Risk: {final_risk:.3f})"
            try:
                store_classification_to_blockchain(domain, is_spam, reason_text, final_risk)
            except Exception as e:
                print(f"Failed to store {domain} to blockchain: {e}")

    return final_risk, {
        "content_prob": round(content_prob, 3),
        "url_prob": round(url_prob, 3),
        "ml_score": round(ml_score, 3),
        "llm_safe_score": round(safe_score, 3),
        "llm_reason": reason,
        "llm_actions": actions,
        "llm_conf": round(llm_conf, 3),
        "adaptive_llm_weight": round(w_llm, 2),
        "blockchain_risk_factor": round(blockchain_risk_factor, 3),
        "blockchain_weight": round(blockchain_weight, 2),
        "blockchain_signals": blockchain_signals,
        "domain_classifications": domain_classifications,
        "cached_domains": len(cached_classifications),
        "unknown_domains": len(unknown_domains),
        "final_risk": round(final_risk, 3),
    }
    try:
        store_classification_to_blockchain(domain, is_spam, reason_text, final_risk)
    except Exception as e:
        print(f"Failed to store {domain} to blockchain: {e}")

    return final_risk, {
        "content_prob": round(content_prob, 3),
        "url_prob": round(url_prob, 3),
        "ml_score": round(ml_score, 3),
        "llm_safe_score": round(safe_score, 3),
        "llm_reason": reason,
        "llm_actions": actions,
        "llm_conf": round(llm_conf, 3),
        "adaptive_llm_weight": round(w_llm, 2),
        "blockchain_risk_factor": round(blockchain_risk_factor, 3),
        "blockchain_weight": round(blockchain_weight, 2),
        "blockchain_signals": blockchain_signals,
        "domain_classifications": domain_classifications,
        "cached_domains": len(cached_classifications),
        "unknown_domains": len(unknown_domains),
        "final_risk": round(final_risk, 3),
    }

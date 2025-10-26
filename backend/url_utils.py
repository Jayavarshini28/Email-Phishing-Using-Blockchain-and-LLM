# import pandas as pd
# import tldextract
# import re
# from urllib.parse import urlparse


# # Symbols and vowels
# special_chars = ['.', '-', '_', '/', '?', '=', '@', '&', '!', ' ', '~', ',', '+', '*', '#', '$', '%']
# vowels = "aeiou"

# def count_chars(string, char_list):
#     """Counts occurrences of characters from char_list in a string."""
#     return [string.count(ch) for ch in char_list]

# def extract_features(url):
#     """
#     Extracts common features from a given URL string.

#     Args:
#         url (str): The URL string to extract features from.

#     Returns:
#         tuple: A tuple containing extracted features and parsed URL components.
#     """
#     parsed = urlparse(url)
#     ext = tldextract.extract(url)

#     domain = parsed.hostname or ""
#     path = parsed.path or ""
#     query = parsed.query or ""
#     scheme = parsed.scheme or ""
#     netloc = parsed.netloc or ""
#     hostname = parsed.hostname or ""
#     port = parsed.port or -1

#     full = url
#     feature_list = []

#     # Raw parsed fields
#     feature_list.extend([scheme, netloc, path, query, hostname, port])

#     # URL level
#     feature_list.extend(count_chars(full, special_chars))
#     feature_list.append(len(full))  # length_url

#     # Domain level
#     feature_list.extend(count_chars(domain, special_chars))
#     feature_list.append(sum(domain.count(v) for v in vowels))
#     feature_list.append(len(domain))
#     feature_list.append(1 if re.match(r"^\d+\.\d+\.\d+\.\d+$", domain) else 0)
#     feature_list.append(1 if 'client' in domain or 'server' in domain else 0)

#     # Directory level
#     feature_list.extend(count_chars(path, special_chars))
#     feature_list.append(len(path))

#     # File level
#     file_name = path.split('/')[-1]
#     feature_list.extend(count_chars(file_name, special_chars))
#     feature_list.append(len(file_name))

#     # Params level
#     feature_list.extend(count_chars(query, special_chars))
#     feature_list.append(len(query))
#     feature_list.append(1 if any(tld in query for tld in ['.com', '.org', '.net']) else 0)
#     feature_list.append(len(query.split('&')) if query else 0)
#     feature_list.append(1 if 'mailto:' in url or 'email=' in url else 0)

#     return feature_list, parsed, ext

# def extract_localhost_features(url):
#     """
#     Extracts features specifically for localhost or 127.0.0.1 URLs.

#     Args:
#         url (str): The localhost URL string.

#     Returns:
#         list: A list of extracted features for localhost URLs.
#     """
#     features, parsed, ext = extract_features(url)
#     # Add any specific localhost features here if needed in the future
#     return features

# def extract_generic_features(url):
#     """
#     Extracts features for generic URLs (not localhost or 127.0.0.1).

#     Args:
#         url (str): The generic URL string.

#     Returns:
#         list: A list of extracted features for generic URLs.
#     """
#     features, parsed, ext = extract_features(url)
#     # Add any specific generic features here if needed in the future
#     return features

# def extract_domain_from_url(url):
#     """Extract clean domain from URL for blockchain lookup"""
#     try:
#         parsed = urlparse(url if url.startswith(('http://', 'https://')) else f'http://{url}')
#         domain = parsed.hostname or url
        
#         # Extract root domain
#         ext = tldextract.extract(domain)
#         if ext.domain and ext.suffix:
#             return f"{ext.domain}.{ext.suffix}"
#         return domain.lower()
#     except:
#         return url.lower()
    
# def check_domain_reputation(domain: str):
#     """
#     Quick blockchain lookup for a single domain
#     Returns: True (spam), False (ham), None (unknown/error)
#     """
#     script_path = os.path.join(os.path.dirname(__file__), 'blockchain', 'interact.js')
    
#     try:
#         result = subprocess.run(
#             ['node', script_path, 'query', domain],
#             capture_output=True, text=True, timeout=10
#         )
        
#         if 'SPAM' in result.stdout:
#             return True
#         elif 'HAM' in result.stdout:
#             return False
#         else:
#             return None
            
#     except Exception as e:
#         logger.debug(f"Blockchain query failed for {domain}: {e}")
#         return None


# def check_url_reputation(url):
#     """
#     Check URL reputation using blockchain
#     Returns: 'spam', 'ham', 'unknown'
#     """
#     domain = extract_domain_from_url(url)
#     reputation = check_domain_reputation(domain)
    
#     if reputation is True:
#         return 'spam'
#     elif reputation is False:
#         return 'ham'
#     else:
#         return 'unknown'


def extract_localhost_features(url):
    """Extract features for localhost URLs"""
    try:
        parsed = urlparse(url)
        features = []
        # Add basic localhost detection
        features.append(1 if 'localhost' in parsed.netloc else 0)
        features.append(1 if '127.0.0.1' in parsed.netloc else 0)
        features.append(len(parsed.path.split('/')))
        return features
    except:
        return [0, 0, 0]

def extract_generic_features(url):
    """Extract generic URL features"""
    try:
        parsed = urlparse(url)
        features = []
        features.append(len(url))
        features.append(len(parsed.netloc))
        features.append(len(parsed.path))
        features.append(url.count('.'))
        features.append(url.count('-'))
        return features
    except:
        return [0, 0, 0, 0, 0]

def extract_domain_from_url(url):
    """Extract domain from URL"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain.lower()
    except:
        return ""

def check_domain_reputation(domain: str):
    """Check domain reputation via blockchain"""
    try:
        script_path = os.path.join(os.path.dirname(__file__), 'blockchain', 'interact.js')
        if not os.path.exists(script_path):
            return None
            
        result = subprocess.run(
            ['node', script_path, 'query', domain],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            # Parse result - adjust based on your interact.js output
            return True  # or False based on actual result
        return None
    except Exception as e:
        logger.error(f"Error checking domain reputation: {e}")
        return None

def check_url_reputation(url):
    """Check URL reputation"""
    domain = extract_domain_from_url(url)
    if domain:
        return check_domain_reputation(domain)
    return None
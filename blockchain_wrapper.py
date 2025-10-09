"""
Simple Python wrapper for blockchain operations
Calls JavaScript blockchain tools via subprocess
"""
import subprocess
import json
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BlockchainWrapper:
    def __init__(self):
        self.interact_script = os.path.join(os.path.dirname(__file__), 'blockchain', 'interact.js')
        self.enabled = os.getenv('ENABLE_BLOCKCHAIN', 'true').lower() == 'true'
        
    def is_domain_spam(self, domain: str) -> Optional[bool]:
        """
        Quick check if domain is known spam
        Returns: True (spam), False (ham), None (unknown/error)
        """
        if not self.enabled:
            return None
            
        try:
            result = subprocess.run(
                ['node', self.interact_script, 'query', domain],
                capture_output=True, text=True, timeout=30
            )
            
            if 'Classification: SPAM' in result.stdout:
                logger.info(f"Blockchain: {domain} is known SPAM")
                return True
            elif 'Classification: HAM' in result.stdout:
                logger.info(f"Blockchain: {domain} is known HAM")
                return False
            else:
                logger.debug(f"Blockchain: {domain} not found")
                return None
                
        except Exception as e:
            logger.warning(f"Blockchain query failed for {domain}: {e}")
            return None
    
    def report_classification(self, domain: str, is_spam: bool, reason: str = "") -> bool:
        """
        Report domain classification to blockchain
        """
        if not self.enabled:
            return False
            
        try:
            result = subprocess.run(
                ['node', self.interact_script, 'classify', domain, 
                 str(is_spam).lower(), reason],
                capture_output=True, text=True, timeout=60
            )
            
            success = 'Transaction confirmed' in result.stdout
            if success:
                status = "SPAM" if is_spam else "HAM"
                logger.info(f"Blockchain: Successfully reported {domain} as {status}")
            else:
                logger.error(f"Blockchain: Failed to report {domain}")
                
            return success
            
        except Exception as e:
            logger.error(f"Blockchain report failed for {domain}: {e}")
            return False

# Global instance
blockchain = BlockchainWrapper()

def check_domain_reputation(domain: str) -> Optional[bool]:
    """Quick function to check if domain is spam"""
    return blockchain.is_domain_spam(domain)

def report_domain(domain: str, is_spam: bool, reason: str = "") -> bool:
    """Quick function to report domain classification"""
    return blockchain.report_classification(domain, is_spam, reason)

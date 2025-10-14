import os
import subprocess
import logging

logger = logging.getLogger(__name__)

class BlockchainInstance:
    def __init__(self):
        self.connected = False
        self.contract_address = None
        self.provider_url = None
        self.network_id = None
        self.account_address = None
        
    def get_connection_status(self):
        """Get blockchain connection status"""
        return {
            "connected": self.connected,
            "contract_address": self.contract_address,
            "provider_url": self.provider_url,
            "network_id": self.network_id or os.getenv('BLOCKCHAIN_NETWORK_ID', '11155111'),
            "account_address": self.account_address
        }
    
    def get_domain_classification(self, domain):
        """Get classification for a specific domain"""
        try:
            script_path = os.path.join(os.path.dirname(__file__), 'blockchain', 'interact.js')
            result = subprocess.run(
                ['node', script_path, 'query', domain],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                # Parse the result - adjust based on your interact.js output format
                return {"domain": domain, "classification": "ham", "confidence": 0.5}
            else:
                return {"domain": domain, "classification": "unknown", "confidence": 0.0}
        except Exception as e:
            logger.error(f"Error getting domain classification: {e}")
            return {"domain": domain, "classification": "unknown", "confidence": 0.0}
    
    def get_domain_reputation(self, domain):
        """Get detailed reputation for a domain"""
        try:
            script_path = os.path.join(os.path.dirname(__file__), 'blockchain', 'interact.js')
            result = subprocess.run(
                ['node', script_path, 'reputation', domain],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                return {
                    "exists": True,
                    "reputation_score": 50,
                    "consensus": "unknown",
                    "spam_votes": 0,
                    "ham_votes": 0,
                    "total_reports": 0
                }
            else:
                return {"exists": False}
        except Exception as e:
            logger.error(f"Error getting domain reputation: {e}")
            return {"exists": False}

# Global instance
_blockchain_instance = None

def get_blockchain_instance():
    """Get or create blockchain instance"""
    global _blockchain_instance
    if _blockchain_instance is None:
        _blockchain_instance = BlockchainInstance()
        try:
            script_path = os.path.join(os.path.dirname(__file__), 'blockchain', 'interact.js')
            if os.path.exists(script_path):
                _blockchain_instance.connected = True
                _blockchain_instance.provider_url = os.getenv('BLOCKCHAIN_PROVIDER_URL', 'http://localhost:8545')
                _blockchain_instance.contract_address = os.getenv('CONTRACT_ADDRESS', '0x41C7c90A5cbCaaC9f1879006bC70231F6d667827')
                _blockchain_instance.network_id = os.getenv('BLOCKCHAIN_NETWORK_ID', '11155111')
                _blockchain_instance.account_address = os.getenv('BLOCKCHAIN_ACCOUNT_ADDRESS')
            else:
                logger.warning("Blockchain script not found, running in offline mode")
                _blockchain_instance.connected = False
        except Exception as e:
            logger.warning(f"Blockchain initialization failed: {e}")
            _blockchain_instance.connected = False
    return _blockchain_instance
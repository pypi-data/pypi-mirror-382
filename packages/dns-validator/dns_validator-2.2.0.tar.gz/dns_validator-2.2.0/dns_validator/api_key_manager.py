"""
API Key Manager for DNS Validator - Secure credential storage

Author: Matisse Urquhart
Contact: me@maturqu.com
License: GNU AGPL v3.0
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from cryptography.fernet import Fernet
import getpass
import base64

class APIKeyManager:
    """Secure API key management for DNS Validator"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.dns-validator'
        self.config_file = self.config_dir / 'config.json'
        self.key_file = self.config_dir / 'key.key'
        self.credentials_file = self.config_dir / 'credentials.enc'
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(exist_ok=True)
        
        # Initialize encryption
        self._init_encryption()
    
    def _init_encryption(self):
        """Initialize encryption key"""
        if not self.key_file.exists():
            # Generate a new key
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            # Set restrictive permissions (Unix-like systems)
            if hasattr(os, 'chmod'):
                os.chmod(self.key_file, 0o600)
        
        with open(self.key_file, 'rb') as f:
            key = f.read()
        
        self.cipher = Fernet(key)
    
    def _load_credentials(self) -> Dict:
        """Load encrypted credentials"""
        if not self.credentials_file.exists():
            return {}
        
        try:
            with open(self.credentials_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception:
            return {}
    
    def _save_credentials(self, credentials: Dict):
        """Save credentials with encryption"""
        try:
            json_data = json.dumps(credentials, indent=2)
            encrypted_data = self.cipher.encrypt(json_data.encode())
            
            with open(self.credentials_file, 'wb') as f:
                f.write(encrypted_data)
            
            # Set restrictive permissions
            if hasattr(os, 'chmod'):
                os.chmod(self.credentials_file, 0o600)
        except Exception as e:
            raise Exception(f"Failed to save credentials: {e}")
    
    def add_credentials(self, provider: str, name: str, credentials: Dict):
        """Add new credentials for a provider"""
        all_creds = self._load_credentials()
        
        if provider not in all_creds:
            all_creds[provider] = {}
        
        all_creds[provider][name] = credentials
        self._save_credentials(all_creds)
    
    def get_credentials(self, provider: str, name: str = None) -> Dict:
        """Get credentials for a provider"""
        all_creds = self._load_credentials()
        
        if provider not in all_creds:
            return {}
        
        if name is None:
            # Return the first (default) credentials
            provider_creds = all_creds[provider]
            if provider_creds:
                return list(provider_creds.values())[0]
            return {}
        
        return all_creds[provider].get(name, {})
    
    def list_credentials(self, provider: str = None) -> Dict:
        """List all credentials, optionally filtered by provider"""
        all_creds = self._load_credentials()
        
        if provider:
            return {provider: all_creds.get(provider, {})}
        
        return all_creds
    
    def delete_credentials(self, provider: str, name: str):
        """Delete specific credentials"""
        all_creds = self._load_credentials()
        
        if provider in all_creds and name in all_creds[provider]:
            del all_creds[provider][name]
            
            # Remove provider if no credentials left
            if not all_creds[provider]:
                del all_creds[provider]
            
            self._save_credentials(all_creds)
            return True
        
        return False
    
    def update_credentials(self, provider: str, name: str, credentials: Dict):
        """Update existing credentials"""
        all_creds = self._load_credentials()
        
        if provider in all_creds and name in all_creds[provider]:
            all_creds[provider][name].update(credentials)
            self._save_credentials(all_creds)
            return True
        
        return False
    
    def get_provider_names(self, provider: str) -> List[str]:
        """Get all credential names for a provider"""
        all_creds = self._load_credentials()
        return list(all_creds.get(provider, {}).keys())
    
    def export_config(self, file_path: str, include_secrets: bool = False):
        """Export configuration to a file"""
        all_creds = self._load_credentials()
        
        if not include_secrets:
            # Mask sensitive information
            masked_creds = {}
            for provider, creds in all_creds.items():
                masked_creds[provider] = {}
                for name, cred_data in creds.items():
                    masked_creds[provider][name] = {}
                    for key, value in cred_data.items():
                        if any(sensitive in key.lower() for sensitive in ['token', 'key', 'secret', 'password']):
                            masked_creds[provider][name][key] = '***MASKED***'
                        else:
                            masked_creds[provider][name][key] = value
            all_creds = masked_creds
        
        with open(file_path, 'w') as f:
            json.dump(all_creds, f, indent=2)
    
    def clear_all_credentials(self):
        """Clear all stored credentials"""
        if self.credentials_file.exists():
            os.remove(self.credentials_file)
        if self.key_file.exists():
            os.remove(self.key_file)
        self._init_encryption()
"""
Configuration management for Jobtty.io
Handles user settings, API keys, and authentication tokens
"""

import os
import json
import keyring
from keyring import errors as keyring_errors
from pathlib import Path
from typing import Dict, Any, Optional

class JobttyConfig:
    """Manages Jobtty configuration and secure storage"""
    
    def __init__(self):
        self.app_name = "jobtty"
        custom_config_dir = os.getenv("JOBTTY_CONFIG_DIR")
        self.config_dir = Path(custom_config_dir) if custom_config_dir else Path.home() / ".jobtty"
        self.config_file = self.config_dir / "config.json"
        self.tokens_file = self.config_dir / "tokens.json"
        self.ensure_config_dir()
        self.load_config()
        self._load_fallback_tokens()
        self._ensure_profile_defaults()
    
    def ensure_config_dir(self):
        """Create config directory if it doesn't exist"""
        try:
            self.config_dir.mkdir(exist_ok=True)
        except PermissionError:
            fallback_dir = Path.cwd() / ".jobtty"
            fallback_dir.mkdir(exist_ok=True)
            self.config_dir = fallback_dir
            self.config_file = self.config_dir / "config.json"
            self.tokens_file = self.config_dir / "tokens.json"
    
    def load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = self.get_default_config()
            self.save_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "location": "",
            "currency": "GBP",
            "remote_only": False,
            "salary_min": 0,
            "preferred_sources": ["jobtty"],
            "display_mode": "table",  # table, list, minimal
            "auto_save_searches": True,
            "notifications": True,
            "theme": "cyber",  # cyber, classic, minimal
            
            # Geographic preferences
            "preferred_countries": [],  # ["Poland", "Germany", "Netherlands"]
            "preferred_cities": [],     # ["Rzeszów", "Kraków", "Warsaw"]
            
            # Job search preferences
            "preference_relocate": False,           # Willing to relocate
            "preference_visa_status": "Not set",   # EU-citizen, US-citizen, Visa-required, Work-permit
            "preference_timezone": "",
            "preference_languages": [],
            
            # Smart filtering
            "use_location_filtering": True,  # Apply preferred countries/cities to search
            "include_remote": True,          # Always include remote positions
            "show_relocation_jobs": False,

            # Activity tracking defaults
            "saved_jobs": [],
            "search_history": [],
            "applied_history": []
        }
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def _load_fallback_tokens(self):
        """Load fallback tokens from file"""
        if self.tokens_file.exists():
            try:
                with open(self.tokens_file, 'r') as f:
                    self._fallback_tokens = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._fallback_tokens = {}
        else:
            self._fallback_tokens = {}

    def _save_fallback_tokens(self):
        """Persist fallback tokens to disk"""
        try:
            with open(self.tokens_file, 'w') as f:
                json.dump(self._fallback_tokens, f, indent=2)
        except OSError:
            # Ignore persistence errors in fallback mode.
            pass

    def _ensure_profile_defaults(self):
        """Ensure optional profile collections exist without preset values"""
        defaults = self.get_default_config()
        keys_to_check = [
            "preferred_countries",
            "preferred_cities",
            "saved_jobs",
            "search_history",
            "applied_history"
        ]

        changed = False
        for key in keys_to_check:
            if key not in self.config:
                self.config[key] = defaults.get(key, [] if 'history' in key else [])
                changed = True

        if changed:
            try:
                self.save_config()
            except PermissionError:
                # In restricted environments (e.g., tests), gracefully skip persistence
                pass

    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value
        self.save_config()
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all configuration settings"""
        return self.config.copy()
    
    # Authentication methods
    def set_auth_token(self, service: str, token: str):
        """Securely store authentication token"""
        try:
            keyring.set_password(self.app_name, f"{service}_token", token)
            if service in self._fallback_tokens:
                self._fallback_tokens.pop(service)
                self._save_fallback_tokens()
        except keyring_errors.KeyringError:
            self._fallback_tokens[service] = token
            self._save_fallback_tokens()

    def get_auth_token(self, service: str) -> Optional[str]:
        """Get authentication token from secure storage"""
        try:
            token = keyring.get_password(self.app_name, f"{service}_token")
            if token:
                return token
        except keyring_errors.KeyringError:
            pass

        return self._fallback_tokens.get(service)

    def remove_auth_token(self, service: str):
        """Remove authentication token"""
        try:
            keyring.delete_password(self.app_name, f"{service}_token")
        except (keyring_errors.PasswordDeleteError, keyring_errors.KeyringError):
            pass

        if service in self._fallback_tokens:
            self._fallback_tokens.pop(service)
            self._save_fallback_tokens()
    
    def set_user_info(self, user_data: Dict[str, Any]):
        """Store user information"""
        user_file = self.config_dir / "user.json"
        with open(user_file, 'w') as f:
            json.dump(user_data, f, indent=2)
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get stored user information"""
        user_file = self.config_dir / "user.json"
        if user_file.exists():
            with open(user_file, 'r') as f:
                return json.load(f)
        return {}
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated to JobTTY"""
        return self.get_auth_token('jobtty') is not None
    
    def logout(self):
        """Clear all authentication data"""
        self.remove_auth_token('jobtty')
        
        # Remove user info
        user_file = self.config_dir / "user.json"
        if user_file.exists():
            user_file.unlink()
    
    # API Configuration
    def get_api_endpoints(self) -> Dict[str, str]:
        """Get API endpoints - JobTTY is the single source of truth"""
        # Allow override for development/testing
        api_base = os.getenv("JOBTTY_API_BASE", "https://jobtty-io.fly.dev/api/v1")
        return {
            "jobtty": api_base
        }
    
    def get_stripe_config(self) -> Dict[str, str]:
        """Get Stripe configuration"""
        return {
            "publishable_key": os.getenv("STRIPE_PUBLISHABLE_KEY", "pk_test_..."),
            "webhook_secret": os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_..."),
            "success_url": "https://jobtty.io/payment/success",
            "cancel_url": "https://jobtty.io/payment/cancel"
        }

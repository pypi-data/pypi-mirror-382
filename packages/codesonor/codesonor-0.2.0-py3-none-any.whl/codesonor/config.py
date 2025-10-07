"""Configuration management for CodeSonor."""

import os
import json
from pathlib import Path
from typing import Optional


class Config:
    """Manages CodeSonor configuration and API keys."""
    
    def __init__(self):
        """Initialize configuration manager."""
        self.config_dir = Path.home() / '.codesonor'
        self.config_file = self.config_dir / 'config.json'
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Create config directory if it doesn't exist."""
        self.config_dir.mkdir(exist_ok=True)
    
    def save_config(self, github_token: Optional[str] = None, gemini_key: Optional[str] = None):
        """
        Save API keys to config file.
        
        Args:
            github_token: GitHub Personal Access Token
            gemini_key: Google Gemini API Key
        """
        config = self.load_config()
        
        if github_token is not None:
            config['github_token'] = github_token
        
        if gemini_key is not None:
            config['gemini_key'] = gemini_key
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_config(self) -> dict:
        """
        Load configuration from file.
        
        Returns:
            Dictionary containing configuration
        """
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    
    def get_github_token(self) -> Optional[str]:
        """
        Get GitHub token from config or environment.
        
        Priority: Environment variable > Config file
        
        Returns:
            GitHub token or None
        """
        # Check environment first
        token = os.getenv('GITHUB_TOKEN')
        if token:
            return token
        
        # Check config file
        config = self.load_config()
        return config.get('github_token')
    
    def get_gemini_key(self) -> Optional[str]:
        """
        Get Gemini API key from config or environment.
        
        Priority: Environment variable > Config file
        
        Returns:
            Gemini API key or None
        """
        # Check environment first
        key = os.getenv('GEMINI_API_KEY')
        if key:
            return key
        
        # Check config file
        config = self.load_config()
        return config.get('gemini_key')
    
    def clear_config(self):
        """Clear all stored configuration."""
        if self.config_file.exists():
            self.config_file.unlink()
    
    def get_config_status(self) -> dict:
        """
        Get current configuration status.
        
        Returns:
            Dictionary with status of each API key
        """
        github_env = bool(os.getenv('GITHUB_TOKEN'))
        gemini_env = bool(os.getenv('GEMINI_API_KEY'))
        
        config = self.load_config()
        github_config = bool(config.get('github_token'))
        gemini_config = bool(config.get('gemini_key'))
        
        return {
            'github_token': {
                'set': github_env or github_config,
                'source': 'environment' if github_env else ('config' if github_config else None)
            },
            'gemini_key': {
                'set': gemini_env or gemini_config,
                'source': 'environment' if gemini_env else ('config' if gemini_config else None)
            },
            'config_file': str(self.config_file)
        }

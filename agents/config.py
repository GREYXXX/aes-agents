import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional

class Config:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        # Load environment variables from .env file
        load_dotenv()
        
        # API Keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.brave_api_key = os.getenv("BRAVE_API_KEY")
        
        # Provider Settings
        self.default_llm_provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
        self.default_search_provider = os.getenv("DEFAULT_SEARCH_PROVIDER", "brave")
        self.default_order_provider = os.getenv("DEFAULT_ORDER_PROVIDER", "playwright")
        
        # LLM Model Settings
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        self.anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
        self.google_model = os.getenv("GOOGLE_MODEL", "gemini-pro")
        
        # Browser Settings
        self.browser_headless = os.getenv("BROWSER_HEADLESS", "true").lower() == "true"
        
    def get_provider_config(self, provider_type: str) -> Dict[str, Any]:
        """Get configuration for a specific provider type."""
        configs = {
            "llm": {
                "openai": {
                    "api_key": self.openai_api_key,
                    "model": self.openai_model
                },
                "anthropic": {
                    "api_key": self.anthropic_api_key,
                    "model": self.anthropic_model
                },
                "google": {
                    "api_key": self.google_api_key,
                    "model": self.google_model
                }
            },
            "search": {
                "brave": {
                    "api_key": self.brave_api_key
                },
                "google": {
                    "api_key": self.google_api_key
                }
            },
            "order": {
                "playwright": {
                    "headless": self.browser_headless
                }
            }
        }
        
        provider_type = provider_type.lower()
        if provider_type not in configs:
            raise ValueError(f"Unknown provider type: {provider_type}")
            
        return configs[provider_type]
    
    def validate_config(self) -> bool:
        """Validate that all required API keys are present."""
        required_keys = {
            "openai": self.openai_api_key,
            "anthropic": self.anthropic_api_key,
            "google": self.google_api_key,
            "brave": self.brave_api_key
        }
        
        missing_keys = [provider for provider, key in required_keys.items() if not key]
        if missing_keys:
            print(f"Warning: Missing API keys for providers: {', '.join(missing_keys)}")
            return False
        return True 
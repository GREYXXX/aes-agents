from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class BaseLLMProvider(ABC):
    """Base class for LLM providers."""
    
    @abstractmethod
    def generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a completion using the LLM."""
        pass

    @abstractmethod
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embeddings for the given text."""
        pass

class BaseSearchProvider(ABC):
    """Base class for search providers."""
    
    @abstractmethod
    def search(
        self,
        query: str,
        count: int = 10,
        result_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for results using the given query."""
        pass 
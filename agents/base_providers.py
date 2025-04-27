from abc import ABC, abstractmethod
from typing import Dict, Any, List

class LLMProvider(ABC):
    @abstractmethod
    def generate_completion(self, prompt: str, system_prompt: str = None, response_format: Dict = None) -> Any:
        """Generate completion from the LLM provider."""
        pass

class SearchProvider(ABC):
    @abstractmethod
    def search(self, query: str, count: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """Search using the search provider."""
        pass

class OrderExecutionProvider(ABC):
    @abstractmethod
    def execute_order(self, product_info: Dict[str, Any], quantity: int) -> Dict[str, Any]:
        """Execute the order using the provider."""
        pass 
from typing import Dict, Any, List
from .base_providers import OrderExecutionProvider

class OrderExecutionAgent:
    def __init__(self, provider: OrderExecutionProvider):
        self.provider = provider
        
    def execute(self, recommendations: List[Dict[str, Any]], quantity: int) -> Dict[str, Any]:
        """Execute the order using the selected provider."""
        selected_product = recommendations[0]  # Use the top recommendation
        return self.provider.execute_order(selected_product, quantity) 
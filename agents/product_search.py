from typing import Dict, Any, List
from .base_providers import SearchProvider

class ProductSearchAgent:
    def __init__(self, search_provider: SearchProvider):
        self.search_provider = search_provider
        
    def search(self, extracted_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for products using the extracted information."""
        search_query = self._construct_search_query(extracted_info)
        return self.search_provider.search(search_query)
    
    def _construct_search_query(self, info: Dict[str, Any]) -> str:
        """Construct a search query from the extracted information."""
        query_parts = [
            info.get('product_type', ''),
            f"quantity {info.get('quantity', '')}",
            f"budget {info.get('budget', '')}"
        ]
        
        if info.get('special_requirements'):
            query_parts.extend(info['special_requirements'])
            
        return " ".join(filter(None, query_parts))
    
    def _process_search_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process and format the search results."""
        processed_results = []
        
        for result in results.get('web', {}).get('results', [])[:5]:
            processed_result = {
                'title': result.get('title', ''),
                'description': result.get('description', ''),
                'url': result.get('url', ''),
                'price': self._extract_price(result.get('description', '')),
                'source': result.get('source', '')
            }
            processed_results.append(processed_result)
        
        return processed_results
    
    def _extract_price(self, text: str) -> str:
        """Extract price information from text if available."""
        # This is a simple implementation. In a real system, you might want to use
        # more sophisticated price extraction methods.
        import re
        price_pattern = r'\$[\d,]+(?:\.\d{2})?'
        match = re.search(price_pattern, text)
        return match.group(0) if match else "Price not specified" 
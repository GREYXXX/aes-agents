from brave import Brave
import os
from ..base_providers import SearchProvider
from typing import Dict, Any, List

class BraveSearchProvider(SearchProvider):
    def __init__(self):
        self.client = Brave(api_key=os.getenv("BRAVE_API_KEY"))
        
    def search(self, query: str, count: int = 5, **kwargs) -> List[Dict[str, Any]]:
        try:
            results = self.client.search(
                q=query,
                count=count,
                search_lang="en",
                safesearch="moderate",
                **kwargs
            )
            
            # Check if we got a valid response
            if not results or not hasattr(results, 'web') or not results.web:
                print("No search results found")
                return []
                
            return self._process_results(results)
        except Exception as e:
            print(f"Error in search: {str(e)}")
            return []
    
    def _process_results(self, results: Any) -> List[Dict[str, Any]]:
        processed_results = []
        try:
            # Access the web results directly from the response object
            web_results = results.web.results if hasattr(results.web, 'results') else []
            
            for result in web_results:
                processed_result = {
                    'title': getattr(result, 'title', ''),
                    'description': getattr(result, 'description', ''),
                    'url': getattr(result, 'url', ''),
                    'price': self._extract_price(getattr(result, 'description', '')),
                    'source': getattr(result, 'source', '')
                }
                processed_results.append(processed_result)
        except Exception as e:
            print(f"Error processing results: {str(e)}")
            
        return processed_results
    
    def _extract_price(self, text: str) -> str:
        import re
        price_pattern = r'\$[\d,]+(?:\.\d{2})?'
        match = re.search(price_pattern, text)
        return match.group(0) if match else "Price not specified" 
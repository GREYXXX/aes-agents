from brave import Brave
import os
from ..base_providers import SearchProvider
from typing import Dict, Any, List, Optional
import json
import requests
import time
from urllib.parse import quote_plus

class BraveSearchProvider(SearchProvider):
    def __init__(self):
        """Initialize the Brave search provider."""
        self.api_key = os.getenv("BRAVE_API_KEY")
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.rate_limit_delay = 1  # Delay between requests in seconds
        self.max_retries = 3  # Maximum number of retries for rate-limited requests
        self.last_request_time = 0

    def search(
        self,
        query: str,
        count: int = 10,
        result_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search using Brave Search API with rate limit handling."""
        if not self.api_key:
            raise ValueError("Brave API key not found in environment variables")

        # Ensure we respect rate limits
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last_request)

        # Prepare query parameters
        params = {
            "q": query,
            "search_lang": "en",
            "count": count,
            "offset": 0,
            "safesearch": "moderate",
            "text_decorations": True,
            "spellcheck": True,
            "extra_snippets": False,
            "result_filter": "web"  # Focus on web results
        }

        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }

        # Try the request with retries
        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    self.base_url,
                    params=params,
                    headers=headers
                )
                self.last_request_time = time.time()

                if response.status_code == 200:
                    data = response.json()
                    web_results = data.get("web", {}).get("results", [])
                    if not web_results:
                        print(f"No results found for query: {query}")
                        return []
                    return self._process_results(web_results)
                elif response.status_code == 429:  # Rate limit
                    if attempt < self.max_retries - 1:
                        # Exponential backoff
                        delay = (2 ** attempt) * self.rate_limit_delay
                        print(f"Rate limited. Retrying in {delay} seconds...")
                        time.sleep(delay)
                        continue
                    else:
                        print("Max retries reached for rate limit")
                        return []
                else:
                    print(f"Search failed with status code: {response.status_code}")
                    print(f"Response: {response.text}")
                    return []

            except Exception as e:
                print(f"Error during search: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.rate_limit_delay)
                    continue
                return []

        return []

    def _process_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and filter search results."""
        processed_results = []
        for result in results:
            try:
                # Skip results without title or URL
                if not result.get("title") or not result.get("url"):
                    continue

                # Extract price from description if available
                description = result.get("description", "")
                price = self._extract_price(description)

                processed_result = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "description": description,
                    "source": self._extract_domain(result.get("url", "")),
                    "price": price
                }
                processed_results.append(processed_result)
            except Exception as e:
                print(f"Error processing result: {str(e)}")
                continue

        return processed_results

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return url
    
    def _extract_price(self, text: str) -> str:
        import re
        price_pattern = r'\$[\d,]+(?:\.\d{2})?'
        match = re.search(price_pattern, text)
        price = match.group(0) if match else "Price not specified"
        return price 
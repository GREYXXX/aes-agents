from typing import Dict, Any, List
from .providers.base_providers import BaseSearchProvider, BaseLLMProvider
import json
import re
from dataclasses import dataclass

@dataclass
class ProductInfo:
    name: str
    price: str
    url: str
    source: str
    description: str
    relevance_score: float

class ProductSearchAgent:
    def __init__(self, search_provider: BaseSearchProvider, llm_provider: BaseLLMProvider):
        """Initialize the product search agent."""
        self.search_provider = search_provider
        self.llm_provider = llm_provider

    def search(self, extracted_info: Dict[str, Any]) -> List[ProductInfo]:
        """Search for products using the extracted information."""
        # Generate optimized search queries
        queries = self._generate_search_queries(extracted_info)
        print(f"\nGenerated Search Queries: {queries}")

        # Perform searches and collect results
        all_results = []
        for query in queries:
            results = self.search_provider.search(query, count=10)
            all_results.extend(results)

        # Process and filter results
        processed_products = self._process_results(all_results, extracted_info)
        
        # Sort by relevance and return top 5
        sorted_products = sorted(processed_products, key=lambda x: x.relevance_score, reverse=True)
        return sorted_products[:5]

    def _generate_search_queries(self, info: Dict[str, Any]) -> List[str]:
        """Generate optimized search queries based on the requirements."""
        product_type = info.get('product_type', '').lower()
        budget = info.get('budget', '')
        location = info.get('location', '')
        special_requirements = info.get('special_requirements', [])

        prompt = f"""
        Based on the following procurement requirements, generate optimized search queries to find products on Australian e-commerce websites.
        Focus on finding actual products for sale, not reviews or information pages.
        
        Product Type: {product_type}
        Budget: {budget}
        Location: {location}
        Special Requirements: {special_requirements}
        
        Return a JSON object with the following structure:
        {{
            "queries": [
                "query 1",
                "query 2",
                ...
            ]
        }}
        
        Important guidelines:
        1. Include specific product names and models when possible
        2. Focus on Australian marketplaces (eBay, Amazon, Gumtree)
        3. Include price range in queries when budget is specified
        4. Use site: operator to target specific marketplaces
        5. Avoid generic terms that might return reviews or information pages
        6. Include brand names for better specificity
        7. Use Australian spelling and terminology
        8. Generate queries for each major marketplace
        """
        
        system_prompt = """You are a product search optimization expert specializing in Australian e-commerce.
        Your goal is to generate effective search queries that will find specific products for purchase on 
        Australian marketplaces. Focus on queries that will return actual product listings, not reviews 
        or information pages."""
        
        response_format = {"type": "json_object"}
        
        try:
            response = self.llm_provider.generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                response_format=response_format
            )
            result = json.loads(response)
            queries = result.get("queries", [])
            
            # Add general marketplace queries
            general_marketplaces = ["ebay.com.au", "amazon.com.au", "gumtree.com.au"]
            for marketplace in general_marketplaces:
                base_query = f"{product_type} site:{marketplace}"
                queries.append(base_query)
                if budget:
                    queries.append(f"{base_query} under {budget}")
                for req in special_requirements:
                    queries.append(f"{base_query} {req}")
            
            return queries
        except Exception:
            # Fallback to basic query with general marketplaces
            return [f"{product_type} site:ebay.com.au OR site:amazon.com.au OR site:gumtree.com.au"]

    def _process_results(self, results: List[Dict[str, Any]], requirements: Dict[str, Any]) -> List[ProductInfo]:
        """Process and filter search results."""
        processed_products = []
        seen_urls = set()

        for result in results:
            try:
                # Skip if we've already seen this URL
                url = result.get('url', '')
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)

                # Extract and validate product information
                name = result.get('title', '')
                description = result.get('description', '')
                source = result.get('source', '')
                
                # Skip if it's not a product page
                if not self._is_product_page(name, description, source):
                    continue

                # Extract price
                price = self._extract_price(description + ' ' + name)
                
                # Calculate relevance score
                relevance_score = self._calculate_relevance(
                    name, description, price, requirements
                )

                # Skip if relevance is too low
                if relevance_score < 0.3:
                    continue

                # Create product info
                product = ProductInfo(
                    name=name,
                    price=price,
                    url=url,
                    source=source,
                    description=description,
                    relevance_score=relevance_score
                )

                processed_products.append(product)

            except Exception:
                continue

        return processed_products

    def _extract_price(self, text: str) -> str:
        """Extract price information from text."""
        # Common price patterns
        patterns = [
            r'AUD\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # AUD format
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # $ format
            r'Price:\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # Price: format
            r'Cost:\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # Cost: format
            r'From\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # From format
            r'Starting at\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'  # Starting at format
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = match.group(1)
                return f"${amount}"
                
        return "Price not specified"

    def _is_product_page(self, title: str, description: str, source: str) -> bool:
        """Determine if the page is likely a product page."""
        # Skip common non-product pages
        non_product_indicators = [
            'forum', 'blog', 'review', 'comparison', 'guide', 'how to',
            'support', 'help', 'contact', 'about', 'news', 'article',
            'specification', 'manual', 'download', 'warranty'
        ]
        
        # Check for product indicators
        product_indicators = [
            'buy', 'purchase', 'add to cart', 'add to bag', 'in stock',
            'available', 'price', '$', 'AUD', 'delivery', 'shipping'
        ]
        
        text = f"{title} {description} {source}".lower()
        
        # Must not contain non-product indicators
        if any(indicator in text for indicator in non_product_indicators):
            return False
            
        # Should contain at least one product indicator
        return any(indicator in text for indicator in product_indicators)

    def _calculate_relevance(self, name: str, description: str, price: str, requirements: Dict[str, Any]) -> float:
        """Calculate how well the product matches the requirements."""
        score = 0.0
        
        # Check product type match
        product_type = requirements.get('product_type', '').lower()
        if product_type in name.lower() or product_type in description.lower():
            score += 0.3
            
        # Check price match if budget is specified
        budget = requirements.get('budget', '')
        if budget and price != "Price not specified":
            try:
                # Extract numeric values
                product_price = float(re.sub(r'[^\d.]', '', price))
                budget_value = float(re.sub(r'[^\d.]', '', budget))
                if product_price <= budget_value:
                    score += 0.3
            except:
                pass
                
        # Check special requirements
        special_reqs = requirements.get('special_requirements', [])
        for req in special_reqs:
            if req.lower() in name.lower() or req.lower() in description.lower():
                score += 0.2
                
        # Check location
        location = requirements.get('location', '').lower()
        if location and location in description.lower():
            score += 0.2
            
        return min(score, 1.0)  # Cap at 1.0 
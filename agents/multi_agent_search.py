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
    key_specs: Dict[str, str]
    delivery_time: str
    recommendation_reason: str

class SearchQueryGeneratorAgent:
    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm_provider = llm_provider

    def generate_queries(self, info: Dict[str, Any]) -> List[str]:
        """Generate precise search queries based on requirements."""
        product_type = info.get('product_type', '').lower()
        budget = info.get('budget', '')
        location = info.get('location', '')
        special_requirements = info.get('special_requirements', [])

        # Generate search queries using LLM
        try:
            prompt = f"""
            Generate 5 precise search queries for finding products on Australian e-commerce websites.
            
            Requirements:
            - Product Type: {product_type}
            - Budget: {budget}
            - Location: {location}
            - Special Requirements: {special_requirements}
            
            Guidelines:
            1. Include specific product names, models, and brands
            2. Use site: operator to target specific marketplaces
            3. Include price range when budget is specified
            4. Add location-specific terms
            5. Include special requirement keywords
            6. Use Australian spelling and terminology
            7. Focus on finding actual product listings
            8. Always use accurate and official domains (e.g., `site:jbhifi.com.au`, `site:harveynorman.com.au`, etc.)  
            9. Tailor the e-commerce domains to match what is commonly used for the given product type
            
            Return a JSON object with the following structure:
            {{
                "queries": [
                    "query 1",
                    "query 2",
                    ...
                ]
            }}
            """
            
            system_prompt = """You are an expert in generating precise e-commerce search queries.
            Your goal is to create queries that will find specific products for purchase."""
            
            response = self.llm_provider.generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response)
            llm_queries = result.get("queries", [])

            # Ensure we have at least one query
            if not llm_queries:
                all_queries = [f"{product_type} site:ebay.com.au OR site:amazon.com.au OR site:gumtree.com.au"]
            return llm_queries  
        except Exception as e:
            print(f"Error generating queries with LLM: {str(e)}")
            return base_queries if base_queries else [f"{product_type} site:ebay.com.au OR site:amazon.com.au OR site:gumtree.com.au"]

class WebSearchAgent:
    def __init__(self, search_provider: BaseSearchProvider):
        self.search_provider = search_provider

    def search(self, queries: List[str]) -> List[Dict[str, Any]]:
        """Perform web search using Brave Search API."""
        all_results = []
        for query in queries:
            results = self.search_provider.search(query, count=5)
            all_results.extend(results)
        return all_results

class InformationExtractionAgent:
    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm_provider = llm_provider

    def extract_info(self, search_results: List[Dict[str, Any]], use_llm: bool = False) -> List[Dict[str, Any]]:
        """Extract product information from search results using either rule-based or LLM-based method."""
        extracted_products = []
        
        for result in search_results:
            try:
                # Extract information using either method
                if use_llm:
                    product_info = self._extract_with_llm(result)
                else:
                    product_info = self._extract_with_rules(result)
                
                if product_info and product_info.get('name') and product_info.get('url'):
                    extracted_products.append(product_info)
            except Exception:
                continue
                
        return extracted_products

    def _extract_with_rules(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract product information using rule-based methods."""
        title = result.get('title', '')
        url = result.get('url', '')
        description = result.get('description', '')
        source = result.get('source', '')

        # Extract price using patterns
        price = self._extract_price_with_patterns(description + ' ' + title)
        
        # Extract key specifications using patterns
        key_specs = self._extract_specs_with_patterns(description)
        
        # Extract delivery time using patterns
        delivery_time = self._extract_delivery_time_with_patterns(description)

        return {
            'name': title,
            'price': price,
            'url': url,
            'source': source,
            'description': description,
            'key_specs': key_specs,
            'delivery_time': delivery_time
        }

    def _extract_price_with_patterns(self, text: str) -> str:
        """Extract price information using regex patterns."""
        patterns = [
            r'AUD\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'Price:\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'Cost:\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'From\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'Starting at\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = match.group(1)
                return f"${amount}"
                
        return "Price not specified"

    def _extract_specs_with_patterns(self, description: str) -> Dict[str, str]:
        """Extract key specifications using regex patterns."""
        specs = {}
        
        # Common specification patterns
        patterns = {
            'brand': r'Brand:\s*([^\n]+)',
            'model': r'Model:\s*([^\n]+)',
            'color': r'Color:\s*([^\n]+)',
            'size': r'Size:\s*([^\n]+)',
            'weight': r'Weight:\s*([^\n]+)',
            'dimensions': r'Dimensions:\s*([^\n]+)',
            'warranty': r'Warranty:\s*([^\n]+)',
            'condition': r'Condition:\s*([^\n]+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                specs[key] = match.group(1).strip()
        
        return specs

    def _extract_delivery_time_with_patterns(self, description: str) -> str:
        """Extract delivery time information using regex patterns."""
        patterns = [
            r'delivery in (\d+-\d+ days?)',
            r'ships in (\d+-\d+ days?)',
            r'arrives in (\d+-\d+ days?)',
            r'express delivery',
            r'next day delivery',
            r'free shipping',
            r'standard delivery',
            r'priority delivery'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description.lower())
            if match:
                return match.group(0)
                
        return "Delivery time not specified"

    def _extract_with_llm(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract product information using LLM."""
        title = result.get('title', '')
        url = result.get('url', '')
        description = result.get('description', '')
        source = result.get('source', '')

        prompt = f"""
        Extract product information from the following search result.
        
        Title: {title}
        URL: {url}
        Description: {description}
        Source: {source}
        
        Extract the following information:
        1. Product name (if this is a product listing)
        2. Price in AUD (if available)
        3. Key specifications (if available)
        4. Delivery time/options (if available)
        
        Return a JSON object with the following structure:
        {{
            "name": "product name",
            "price": "price in AUD format (e.g., $999.99)",
            "url": "product URL",
            "source": "source website",
            "description": "product description",
            "key_specs": {{
                "spec1": "value1",
                "spec2": "value2"
            }},
            "delivery_time": "delivery time information"
        }}
        
        If any information is not available, use appropriate default values:
        - "Price not specified" for missing price
        - Empty object {{}} for missing specifications
        - "Delivery time not specified" for missing delivery time
        """
        
        system_prompt = """You are an expert in extracting product information from e-commerce listings.
        Your goal is to accurately identify and extract product details, prices, specifications, and delivery information.
        Only return information that is clearly present in the input text."""
        
        try:
            response = self.llm_provider.generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                response_format={"type": "json_object"}
            )
            return json.loads(response)
        except Exception:
            return {
                'name': title,
                'price': "Price not specified",
                'url': url,
                'source': source,
                'description': description,
                'key_specs': {},
                'delivery_time': "Delivery time not specified"
            }

class ProductFilteringAndRankingAgent:
    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm_provider = llm_provider

    def filter_and_rank(self, products: List[Dict[str, Any]], requirements: Dict[str, Any], use_llm: bool = False) -> List[Dict[str, Any]]:
        """Filter and rank products based on requirements."""
        if not products:
            return []

        if use_llm:
            return self._filter_and_rank_with_llm(products, requirements)
        else:
            return self._filter_and_rank_with_rules(products, requirements)

    def _filter_and_rank_with_llm(self, products: List[Dict[str, Any]], requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter and rank products using LLM-based approach with reduced context."""
        try:
            # Prepare a simplified prompt for each product
            prompt_template = """
            Evaluate this product based on the requirements and return only a relevance score (0.0 to 1.0).
            
            Requirements:
            - Product Type: {product_type}
            - Budget: {budget}
            - Location: {location}
            - Special Requirements: {special_reqs}
            
            Product:
            - Name: {name}
            - Price: {price}
            - URL: {url}
            - Description: {description}
            
            Evaluation Criteria:
            1. Must be a specific product page (not category/list)
            2. Must match product type and brand
            3. Price should be within ±20% of budget
            4. Location availability
            5. Special requirements match
            
            Return ONLY a number between 0.0 and 1.0 representing the relevance score.
            """
            
            system_prompt = """You are an expert product evaluator. Return only a relevance score between 0.0 and 1.0."""
            
            # Process products in batches to manage context length
            batch_size = 5
            scored_products = []
            
            for i in range(0, len(products), batch_size):
                batch = products[i:i + batch_size]
                
                for product in batch:
                    try:
                        prompt = prompt_template.format(
                            product_type=requirements.get('product_type', ''),
                            budget=requirements.get('budget', ''),
                            location=requirements.get('location', ''),
                            special_reqs=requirements.get('special_requirements', []),
                            name=product.get('name', ''),
                            price=product.get('price', ''),
                            url=product.get('url', ''),
                            description=product.get('description', '')
                        )
                        
                        response = self.llm_provider.generate_completion(
                            prompt=prompt,
                            system_prompt=system_prompt
                        )
                        
                        # Extract score from response
                        try:
                            score = float(response.strip())
                            if 0 <= score <= 1:
                                product['relevance_score'] = score
                                scored_products.append(product)
                        except ValueError:
                            print(f"Invalid score format: {response}")
                            continue
                            
                    except Exception as e:
                        print(f"Error processing product: {str(e)}")
                        continue
            
            # Filter and sort products
            filtered_products = [
                p for p in scored_products 
                if p.get('relevance_score', 0) >= 0.01
            ]
            
            return sorted(filtered_products, key=lambda x: x.get('relevance_score', 0), reverse=True)
            
        except Exception as e:
            print(f"Error in LLM-based filtering and ranking: {str(e)}")
            # Fallback to rule-based filtering if LLM fails
            return self._filter_and_rank_with_rules(products, requirements)

    def _filter_and_rank_with_rules(self, products: List[Dict[str, Any]], requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter and rank products using rule-based approach matching LLM criteria."""
        filtered_products = []
        
        for product in products:
            try:
                # Initialize evaluation metrics
                evaluation = {
                    "is_specific_product": False,
                    "product_relevance": False,
                    "price_match": False,
                    "additional_factors": {
                        "location_match": False,
                        "requirements_match": False,
                        "overall_quality": "low"
                    }
                }
                
                # 1. Check if it's a specific product page
                url = product.get('url', '').lower()
                name = product.get('name', '').lower()
                description = product.get('description', '').lower()
                
                # Product page indicators
                product_indicators = [
                    'product', 'item', 'sku', 'id', 'p-', 'prod-', 'model-', 'variant-',
                    'model', 'variant', 'version', 'edition', 'series', 'generation'
                ]
                
                # Category page indicators
                category_indicators = [
                    'category', 'collection', 'list', 'search', 'results', 'shop', 'store', 'browse',
                    'all-', 'products-', 'items-', 'laptops', 'computers', 'phones', 'tablets'
                ]
                
                # Check for product identifiers
                has_product_id = any(indicator in url or indicator in name for indicator in product_indicators)
                has_model_number = bool(re.search(r'[A-Z0-9]{4,}', name))
                has_specific_details = len(name.split()) >= 4 and any(char.isdigit() for char in name)
                
                # Check for category indicators
                is_category_page = any(indicator in url or indicator in name or indicator in description 
                                     for indicator in category_indicators)
                
                evaluation["is_specific_product"] = not is_category_page and (has_product_id or has_model_number or has_specific_details)
                
                # 2. Check product relevance
                product_type = requirements.get('product_type', '').lower()
                brand = requirements.get('brand', '').lower()
                
                type_match = product_type in name or product_type in description
                brand_match = not brand or brand in name or brand in description
                
                evaluation["product_relevance"] = type_match and brand_match
                
                # 3. Check price match
                budget = requirements.get('budget', '')
                if budget and product['price'] != "Price not specified":
                    try:
                        product_price = float(re.sub(r'[^\d.]', '', product['price']))
                        budget_value = float(re.sub(r'[^\d.]', '', budget))
                        # Allow ±20% variation
                        evaluation["price_match"] = abs(product_price - budget_value) / budget_value <= 0.2
                    except:
                        pass
                
                # 4. Check additional factors
                location = requirements.get('location', '').lower()
                special_reqs = requirements.get('special_requirements', [])
                
                evaluation["additional_factors"]["location_match"] = not location or location in description
                evaluation["additional_factors"]["requirements_match"] = all(
                    req.lower() in name or req.lower() in description 
                    for req in special_reqs
                )
                
                # Calculate overall quality
                quality_score = sum([
                    0.3 if evaluation["is_specific_product"] else 0,
                    0.3 if evaluation["product_relevance"] else 0,
                    0.2 if evaluation["price_match"] else 0,
                    0.1 if evaluation["additional_factors"]["location_match"] else 0,
                    0.1 if evaluation["additional_factors"]["requirements_match"] else 0
                ])
                
                evaluation["additional_factors"]["overall_quality"] = (
                    "high" if quality_score >= 0.7 else
                    "medium" if quality_score >= 0.4 else
                    "low"
                )
                
                # Calculate final relevance score
                relevance_score = quality_score
                
                # Update product with evaluation results
                product.update({
                    "relevance_score": relevance_score,
                    "ranking_reason": self._generate_ranking_reason(evaluation),
                    "is_specific_product": evaluation["is_specific_product"],
                    "product_relevance": evaluation["product_relevance"],
                    "price_match": evaluation["price_match"],
                    "additional_factors": evaluation["additional_factors"]
                })
                
                # Only include products that meet minimum criteria
                if (evaluation["is_specific_product"] and 
                    evaluation["product_relevance"] and 
                    relevance_score >= 0.3):
                    filtered_products.append(product)
                    
            except Exception as e:
                print(f"Error evaluating product: {str(e)}")
                continue
                
        return sorted(filtered_products, key=lambda x: x.get("relevance_score", 0), reverse=True)

    def _generate_ranking_reason(self, evaluation: Dict[str, Any]) -> str:
        """Generate a human-readable reason for the ranking."""
        reasons = []
        
        if evaluation["is_specific_product"]:
            reasons.append("specific product page")
        if evaluation["product_relevance"]:
            reasons.append("matches product requirements")
        if evaluation["price_match"]:
            reasons.append("price within budget range")
        if evaluation["additional_factors"]["location_match"]:
            reasons.append("available in specified location")
        if evaluation["additional_factors"]["requirements_match"]:
            reasons.append("meets special requirements")
            
        quality = evaluation["additional_factors"]["overall_quality"]
        reasons.append(f"overall quality: {quality}")
        
        return ", ".join(reasons)

class RecommendationFormattingAgent:
    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm_provider = llm_provider

    def format_recommendations(self, products: List[Dict[str, Any]], requirements: Dict[str, Any]) -> List[ProductInfo]:
        """Format products into structured recommendations."""
        formatted_products = []
        
        for product in products:
            try:
                # Generate recommendation reason
                reason = self._generate_recommendation_reason(product, requirements)
                
                # Create ProductInfo object
                formatted_product = ProductInfo(
                    name=product['name'],
                    price=product['price'],
                    url=product['url'],
                    source=product['source'],
                    description=product['description'],
                    relevance_score=product['relevance_score'],
                    key_specs=product['key_specs'],
                    delivery_time=product['delivery_time'],
                    recommendation_reason=reason
                )
                
                formatted_products.append(formatted_product)
            except Exception:
                continue
                
        return formatted_products

    def _generate_recommendation_reason(self, product: Dict[str, Any], requirements: Dict[str, Any]) -> str:
        """Generate a reason for recommending the product."""
        prompt = f"""
        Generate a concise reason for recommending this product based on the requirements.
        
        Product:
        {json.dumps(product, indent=2)}
        
        Requirements:
        {json.dumps(requirements, indent=2)}
        
        Focus on:
        1. How well it matches the requirements
        2. Key specifications that meet the needs
        3. Price and value proposition
        4. Delivery options
        """
        
        try:
            return self.llm_provider.generate_completion(
                prompt=prompt,
                system_prompt="You are an expert in product recommendations."
            )
        except Exception:
            return "Recommended based on relevance to requirements"

class MultiAgentProductSearch:
    def __init__(self, search_provider: BaseSearchProvider, llm_provider: BaseLLMProvider):
        """Initialize the multi-agent product search system."""
        self.query_generator = SearchQueryGeneratorAgent(llm_provider)
        self.web_searcher = WebSearchAgent(search_provider)
        self.info_extractor = InformationExtractionAgent(llm_provider)
        self.filter_ranker = ProductFilteringAndRankingAgent(llm_provider)
        self.llm_provider = llm_provider

    def search(self, extracted_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for products using the extracted information."""
        # Step 1: Generate search queries
        queries = self.query_generator.generate_queries(extracted_info)
        print(f"\nGenerated Search Queries: {queries}")

        # Step 2: Perform web search
        search_results = self.web_searcher.search(queries)

        # Step 3: Extract product information
        extracted_products = self.info_extractor.extract_info(search_results)

        # Step 4: Filter and rank products
        ranked_products = self.filter_ranker.filter_and_rank(extracted_products, extracted_info, use_llm=True)

        # Step 5: Estimate missing prices
        products_with_prices = self._estimate_missing_prices(ranked_products, extracted_info)

        # Return top 5 most relevant products
        return products_with_prices[:5]

    def _estimate_missing_prices(self, products: List[Dict[str, Any]], requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Estimate prices for products with missing price information."""
        for product in products:
            if product['price'] == "Price not specified":
                try:
                    prompt = f"""
                    Estimate the price for this product based on its specifications and market knowledge.
                    
                    Product:
                    - Name: {product['name']}
                    - Description: {product['description']}
                    - Key Specs: {json.dumps(product.get('key_specs', {}), indent=2)}
                    
                    Requirements:
                    - Product Type: {requirements.get('product_type', '')}
                    - Budget: {requirements.get('budget', '')}
                    - Location: {requirements.get('location', '')}
                    
                    Return ONLY the estimated price in AUD format (e.g., "$999.99").
                    """
                    
                    system_prompt = """You are an expert in product pricing. Estimate the market price based on product specifications and current market rates."""
                    
                    response = self.llm_provider.generate_completion(
                        prompt=prompt,
                        system_prompt=system_prompt
                    )
                    
                    # Extract price from response
                    price_match = re.search(r'\$?\d{1,3}(?:,\d{3})*(?:\.\d{2})?', response)
                    if price_match:
                        estimated_price = price_match.group(0)
                        if not estimated_price.startswith('$'):
                            estimated_price = f"${estimated_price}"
                        product['price'] = estimated_price
                        product['is_estimated_price'] = True
                    else:
                        product['price'] = "Price not available"
                        
                except Exception as e:
                    print(f"Error estimating price: {str(e)}")
                    product['price'] = "Price not available"
                    
        return products 
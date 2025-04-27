from typing import Dict, Any, List
from .base_providers import LLMProvider
from .product_search import ProductInfo
import json

class EvaluationAgent:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        
    def evaluate(self, search_results: List[ProductInfo], extracted_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate and rank the search results based on the procurement requirements."""
        # Convert ProductInfo objects to dictionaries for LLM processing
        results_dict = [
            {
                "title": product.name,
                "url": product.url,
                "price": product.price,
                "description": product.description,
                "source": product.source
            }
            for product in search_results
        ]
        
        prompt = f"""
        Evaluate the following products based on the procurement requirements and rank them from best to worst.
        Consider factors such as price, relevance to requirements, and source reliability.
        
        Procurement Requirements:
        {json.dumps(extracted_info, indent=2)}
        
        Search Results:
        {json.dumps(results_dict, indent=2)}
        
        Return the ranked results in JSON format with these fields:
        {{
            "ranked_results": [
                {{
                    "title": string,
                    "url": string,
                    "price": string,
                    "score": number,
                    "reasoning": string
                }}
            ]
        }}
        """
        
        system_prompt = "You are a procurement evaluation assistant."
        response_format = {"type": "json_object"}
        
        try:
            response = self.llm_provider.generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                response_format=response_format
            )
            
            # Parse the JSON response into a dictionary
            parsed_response = json.loads(response)
            return parsed_response["ranked_results"]
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error in evaluation: {str(e)}")
            # If parsing fails or key is missing, return the original results as dictionaries
            return results_dict 
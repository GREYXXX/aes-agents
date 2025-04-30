from typing import Dict, Any, List
from .base_providers import LLMProvider
import json

class EvaluationAgent:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        
    def evaluate(self, search_results: List[Dict[str, Any]], extracted_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate and rank the search results based on the procurement requirements."""
        # Convert dictionaries to format for LLM processing
        results_dict = [
            {
                "title": product.get('name', ''),
                "url": product.get('url', ''),
                "price": product.get('price', ''),
                "description": product.get('description', ''),
                "source": product.get('source', '')
            }
            for product in search_results
        ]
        
        prompt = f"""
        Evaluate the following products based on the procurement requirements and provide a concise summary for each.
        Focus on key features, price, and availability.
        
        Procurement Requirements:
        {json.dumps(extracted_info, indent=2)}
        
        Search Results:
        {json.dumps(results_dict, indent=2)}
        
        Return the results in JSON format with these fields:
        {{
            "recommendations": [
                {{
                    "title": string,
                    "url": string,
                    "price": string,
                    "summary": string,
                    "source": string
                }}
            ]
        }}
        """
        
        system_prompt = "You are a product recommendation assistant. Provide clear, concise summaries of each product."
        response_format = {"type": "json_object"}
        
        try:
            response = self.llm_provider.generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                response_format=response_format
            )
            
            # Parse the JSON response into a dictionary
            parsed_response = json.loads(response)
            return parsed_response["recommendations"]
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error in evaluation: {str(e)}")
            # If parsing fails or key is missing, return the original results as dictionaries
            return results_dict 
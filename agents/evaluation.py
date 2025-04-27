from typing import Dict, Any, List
from .base_providers import LLMProvider
import json

class EvaluationAgent:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        
    def evaluate(self, search_results: List[Dict[str, Any]], extracted_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate and rank the search results based on the procurement requirements."""
        prompt = f"""
        Evaluate the following products based on the procurement requirements and rank them from best to worst.
        Consider factors such as price, relevance to requirements, and source reliability.
        
        Procurement Requirements:
        {extracted_info}
        
        Search Results:
        {search_results}
        
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
        
        response = self.llm_provider.generate_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            response_format=response_format
        )
        
        # Parse the JSON response into a dictionary
        try:
            parsed_response = json.loads(response)
            return parsed_response["ranked_results"]
        except (json.JSONDecodeError, KeyError):
            # If parsing fails or key is missing, return an empty list
            return [] 
from typing import Dict, Any
from .base_providers import LLMProvider
import json

class InputUnderstandingAgent:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        
    def process(self, text: str) -> Dict[str, Any]:
        """Process the input text and extract procurement information."""
        prompt = f"""
        Extract the following information from the procurement request:
        - Product type/description
        - Quantity needed
        - Budget range
        - Special requirements
        - Urgency level
        - Preferred suppliers (if mentioned)
        
        Text: {text}
        
        Return the information in JSON format with these fields:
        {{
            "product_type": string,
            "quantity": number,
            "budget": string,
            "special_requirements": string[],
            "urgency": string,
            "preferred_suppliers": string[]
        }}
        """
        
        system_prompt = "You are a procurement information extraction assistant."
        response_format = {"type": "json_object"}
        
        response = self.llm_provider.generate_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            response_format=response_format
        )
        
        # Parse the JSON response into a dictionary
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # If parsing fails, return a default dictionary
            return {
                "product_type": "",
                "quantity": 0,
                "budget": "",
                "special_requirements": [],
                "urgency": "",
                "preferred_suppliers": []
            } 
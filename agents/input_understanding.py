from typing import Dict, Any
from .providers.base_providers import BaseLLMProvider
import json

class InputUnderstandingAgent:
    def __init__(self, llm_provider: BaseLLMProvider):
        """Initialize the input understanding agent."""
        self.llm_provider = llm_provider

    def extract_info(self, text: str) -> Dict[str, Any]:
        """Extract structured information from the input text."""
        prompt = f"""
        Extract the following information from the procurement request:
        - Product type
        - Quantity
        - Budget
        - Location
        - Special requirements
        - Urgency
        
        Input text:
        {text}
        
        Return a JSON object with the following structure:
        {{
            "product_type": string,
            "quantity": number,
            "budget": string,
            "location": string,
            "special_requirements": string[],
            "urgency": string
        }}
        """
        
        system_prompt = """You are a procurement specialist. Your task is to extract key information 
        from procurement requests. Focus on identifying the product type, quantity, budget, location, 
        special requirements, and urgency. Return the information in a structured JSON format."""
        
        response_format = {"type": "json_object"}
        
        try:
            response = self.llm_provider.generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                response_format=response_format
            )
            extracted_info = json.loads(response)
            return extracted_info
        except Exception as e:
            print(f"Error extracting information: {str(e)}")
            # Return a default structure if extraction fails
            return {
                "product_type": "",
                "quantity": 1,
                "budget": "",
                "location": "",
                "special_requirements": [],
                "urgency": ""
            } 
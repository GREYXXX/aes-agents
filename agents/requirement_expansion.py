from typing import Dict, Any, List
from .providers.base_providers import BaseLLMProvider
import json

class RequirementExpansionAgent:
    def __init__(self, llm_provider: BaseLLMProvider):
        """Initialize the requirement expansion agent."""
        self.llm_provider = llm_provider

    def expand_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Expand vague requirements into detailed specifications covering all possible relevant products."""
        print("\n=== Starting Requirement Expansion ===")
        print(f"Original Requirements: {json.dumps(requirements, indent=2, ensure_ascii=False)}")

        # Generate expanded requirements
        expanded_info = self._generate_expanded_requirements(requirements)
        print(f"\nExpanded Requirements: {json.dumps(expanded_info, indent=2, ensure_ascii=False)}")
        print("\n=== Requirement Expansion Complete ===")
        
        return expanded_info

    def _generate_expanded_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate expanded requirements using LLM."""
        prompt = f"""
        Based on the following procurement requirements, generate expanded requirements.
        
        Original Requirements:
        {json.dumps(requirements, ensure_ascii=False, indent=2)}
        
        Guidelines for expansion:
        1. Keep the original product type but suggest similar alternatives if relevant
        2. Include different brands and options available in the market
        3. Consider different quantities and packaging options
        4. Include both premium and budget options within the specified budget
        5. Maintain the original location and delivery requirements
        6. Consider both online and local purchase options
        
        Return a JSON object with the following structure:
        {{
            "product_type": "original product type with alternatives",
            "options": [
                "option 1",
                "option 2",
                "option 3"
            ],
            "budget": "original budget information",
            "location": "original location information",
            "special_requirements": [
                "original requirements",
                "additional considerations"
            ],
            "urgency": "original urgency level"
        }}
        """
        
        system_prompt = """You are a procurement assistant. Your task is to help users find the products they need, 
        whether it's office supplies, electronics, or daily necessities. Keep the suggestions practical and 
        relevant to the user's needs."""
        
        response_format = {"type": "json_object"}
        
        try:
            response = self.llm_provider.generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                response_format=response_format
            )
            expanded_info = json.loads(response)
            return expanded_info
        except Exception as e:
            print(f"Error in requirement expansion: {str(e)}")
            # Return original requirements if expansion fails
            return requirements 
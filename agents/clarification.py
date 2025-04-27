from typing import Dict, Any, List
from .base_providers import LLMProvider

class ClarificationAgent:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        
    def needs_clarification(self, extracted_info: Dict[str, Any]) -> bool:
        """Determine if the extracted information needs clarification."""
        required_fields = ['product_type', 'quantity', 'budget']
        return any(field not in extracted_info or not extracted_info[field] for field in required_fields)
    
    def generate_questions(self, extracted_info: Dict[str, Any]) -> List[str]:
        """Generate clarification questions based on missing or ambiguous information."""
        prompt = f"""
        Based on the following extracted procurement information, generate specific questions to clarify any missing or ambiguous details:
        
        {extracted_info}
        
        Return a list of questions in JSON format:
        {{
            "questions": string[]
        }}
        """
        
        system_prompt = "You are a procurement clarification assistant."
        response_format = {"type": "json_object"}
        
        response = self.llm_provider.generate_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            response_format=response_format
        )
        
        return response["questions"]
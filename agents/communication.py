from typing import Dict, Any, List
from .base_providers import LLMProvider

class CommunicationAgent:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        
    def generate_approval_request(self, recommendations: List[Dict[str, Any]], extracted_info: Dict[str, Any]) -> str:
        """Generate an approval request email based on the recommendations and procurement details."""
        prompt = f"""
        Generate a professional approval request email for the following procurement request.
        
        Procurement Details:
        {extracted_info}
        
        Recommended Products:
        {recommendations}
        
        The email should include:
        1. Clear subject line
        2. Brief explanation of the request
        3. Key details of the recommended product
        4. Justification for the selection
        5. Request for approval with a clear call to action
        """
        
        system_prompt = "You are a professional procurement communication assistant."
        
        return self.llm_provider.generate_completion(
            prompt=prompt,
            system_prompt=system_prompt
        )
    
    def generate_confirmation(self, recommendations: List[Dict[str, Any]], extracted_info: Dict[str, Any]) -> str:
        """Generate a confirmation email for the procurement request."""
        prompt = f"""
        Generate a professional confirmation email for the following procurement request.
        
        Procurement Details:
        {extracted_info}
        
        Selected Product:
        {recommendations[0]}  # Using the top recommendation
        
        The email should include:
        1. Clear subject line
        2. Confirmation of the order
        3. Key details of the selected product
        4. Next steps and expected delivery timeline
        5. Contact information for any questions
        """
        
        system_prompt = "You are a professional procurement communication assistant."
        
        return self.llm_provider.generate_completion(
            prompt=prompt,
            system_prompt=system_prompt
        ) 
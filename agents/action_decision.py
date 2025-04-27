from typing import Dict, Any, List
from .base_providers import LLMProvider
import json

class ActionDecisionAgent:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        self.company_rules = """
        Company Procurement Rules:
        1. Orders under $1000 can be processed directly
        2. Orders between $1000 and $5000 require department manager approval
        3. Orders above $5000 require executive approval
        4. Urgent orders (within 24 hours) require immediate manager approval regardless of amount
        5. Special requirements must be reviewed by the procurement team
        """
        
    def decide(self, recommendations: List[Dict[str, Any]], extracted_info: Dict[str, Any]) -> Dict[str, Any]:
        """Determine the next action based on company rules and procurement details."""
        prompt = f"""
        Based on the company rules and procurement details, determine the appropriate action.
        
        Company Rules:
        {self.company_rules}
        
        Procurement Details:
        {extracted_info}
        
        Recommended Products:
        {recommendations}
        
        Return the decision in JSON format:
        {{
            "action": string,  // "direct_order" or "request_approval"
            "approval_level": string,  // "department_manager", "executive", or "none"
            "reason": string
        }}
        """
        
        system_prompt = "You are a procurement decision assistant."
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
                "action": "request_approval",
                "approval_level": "department_manager",
                "reason": "Unable to process decision"
            } 
from typing import Dict, Any, List
from .providers.base_providers import BaseLLMProvider
import json

class ActionDecisionAgent:
    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm_provider = llm_provider
        self.company_rules = """
        Company Procurement Rules:
        1. Orders under $1000 can be processed directly
        2. Orders between $1000 and $5000 require department manager approval
        3. Orders above $5000 require executive approval
        4. Urgent orders (within 24 hours) require immediate manager approval regardless of amount
        5. Special requirements must be reviewed by the procurement team
        6. All computer and laptop orders require IT department approval
        """
        
    def decide(self, evaluation: List[Dict[str, Any]], extracted_info: Dict[str, Any]) -> Dict[str, Any]:
        """Determine the next action based on evaluation results and procurement details."""
        # Extract total cost from evaluation
        total_cost = 0
        if evaluation and 'price' in evaluation[0]:
            try:
                price_str = evaluation[0]['price'].replace('$', '').replace(',', '')
                quantity = int(extracted_info.get('quantity', 1))
                total_cost = float(price_str) * quantity
            except:
                total_cost = 0

        # Check if approval is needed based on company rules
        needs_approval = False
        approval_level = "none"
        reason = ""

        # Check for computer/laptop orders
        product_type = extracted_info.get('product_type', '').lower()
        if 'computer' in product_type or 'laptop' in product_type:
            needs_approval = True
            approval_level = "it_department"
            reason = "Computer/laptop orders require IT department approval"

        # Check budget rules if not already requiring approval
        elif total_cost >= 5000:
            needs_approval = True
            approval_level = "executive"
            reason = "Order amount exceeds $5000, requiring executive approval"
        elif total_cost >= 1000:
            needs_approval = True
            approval_level = "department_manager"
            reason = "Order amount between $1000 and $5000, requiring department manager approval"

        # Check urgency
        if extracted_info.get('urgency', '').lower() in ['urgent', 'asap', 'immediate']:
            needs_approval = True
            approval_level = "department_manager"
            reason = "Urgent order requires immediate manager approval"

        # Check special requirements
        if extracted_info.get('special_requirements'):
            needs_approval = True
            approval_level = "procurement_team"
            reason = "Special requirements need procurement team review"

        return {
            "action": "request_approval" if needs_approval else "direct_order",
            "approval_level": approval_level,
            "reason": reason,
            "total_cost": total_cost
        } 
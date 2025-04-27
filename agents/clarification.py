from typing import Dict, Any, List, Tuple
from .providers.base_providers import BaseLLMProvider
import json

class ClarificationAgent:
    def __init__(self, llm_provider: BaseLLMProvider):
        """Initialize the clarification agent."""
        self.llm_provider = llm_provider
        
    def needs_clarification(self, extracted_info: Dict[str, Any]) -> bool:
        """Determine if the extracted information needs clarification."""
        # Check required fields
        required_fields = {
            'product_type': 'What product are you looking to purchase?',
            'quantity': 'How many units do you need?',
            'budget': 'What is your budget for this purchase?',
            'location': 'Where do you need the product delivered?'
        }
        
        # Check if any required field is missing or empty
        for field, _ in required_fields.items():
            if field not in extracted_info or not extracted_info[field]:
                return True
                
        # Check if special requirements are properly formatted
        if 'special_requirements' not in extracted_info:
            return True
            
        return False
    
    def generate_questions(self, extracted_info: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Generate clarification questions based on missing or ambiguous information.
        Returns a list of tuples (field_name, question_text)."""
        prompt = f"""
        Based on the following extracted procurement information, generate specific questions to clarify any missing or ambiguous details.
        Focus on essential information needed for product search.
        
        Current Information:
        {json.dumps(extracted_info, indent=2, ensure_ascii=False)}
        
        Return a JSON object with the following structure:
        {{
            "questions": [
                {{
                    "field": "field_name",
                    "question": "specific question text",
                    "type": "input_type"  // "number", "text", "select", or "multiselect"
                }}
            ]
        }}
        
        Guidelines:
        1. For product type, ask for specific details if too vague
        2. For quantity, always use number input
        3. For budget, include currency format guidance
        4. For location, be specific about delivery address
        5. For special requirements, ask about specific features or constraints
        6. Use appropriate input types for each question
        """
        
        system_prompt = """You are a procurement clarification assistant. Your task is to generate 
        specific, clear questions to gather all necessary information for product search. Focus on 
        essential details that will help find the most relevant products."""
        
        response_format = {"type": "json_object"}
        
        try:
            response = self.llm_provider.generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                response_format=response_format
            )
            result = json.loads(response)
            questions = []
            for q in result.get("questions", []):
                questions.append((q["field"], q["question"], q["type"]))
            return questions
        except Exception as e:
            print(f"Error generating questions: {str(e)}")
            # Return default questions if generation fails
            return [
                ("product_type", "What product are you looking to purchase?", "text"),
                ("quantity", "How many units do you need?", "number"),
                ("budget", "What is your budget for this purchase? (e.g., 1000 AUD)", "text"),
                ("location", "Where do you need the product delivered?", "text")
            ]
    
    def validate_answers(self, answers: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate the provided answers and return (is_valid, error_messages)."""
        errors = []
        
        # Validate quantity
        if "quantity" in answers:
            try:
                quantity = int(answers["quantity"])
                if quantity <= 0:
                    errors.append("Quantity must be greater than 0")
            except ValueError:
                errors.append("Quantity must be a valid number")
        
        # Validate budget
        if "budget" in answers:
            budget = answers["budget"]
            if not budget:
                errors.append("Budget is required")
            elif not any(char.isdigit() for char in budget):
                errors.append("Budget must include a numeric value")
        
        # Validate product type
        if "product_type" in answers and not answers["product_type"]:
            errors.append("Product type is required")
        
        # Validate location
        if "location" in answers and not answers["location"]:
            errors.append("Delivery location is required")
        
        return len(errors) == 0, errors
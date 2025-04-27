from openai import OpenAI
import os
from ..base_providers import LLMProvider
from typing import Dict, Any

class OpenAIProvider(LLMProvider):
    def __init__(self, model: str = "gpt-4-turbo-preview"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        
    def generate_completion(self, prompt: str, system_prompt: str = None, response_format: Dict = None) -> Any:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format=response_format
        )
        
        return response.choices[0].message.content 
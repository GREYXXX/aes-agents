from typing import Dict, Any, Optional
from .base_providers import BaseLLMProvider
import os
import json
from openai import OpenAI

class LLMProvider(BaseLLMProvider):
    def __init__(self):
        """Initialize the LLM provider with OpenAI API."""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

    def generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a completion using the LLM."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format=response_format or {"type": "text"},
                temperature=0.7,
                max_tokens=2000
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"Error generating completion: {str(e)}")
            raise

    def generate_embedding(self, text: str) -> list[float]:
        """Generate embeddings for the given text."""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {str(e)}")
            raise 
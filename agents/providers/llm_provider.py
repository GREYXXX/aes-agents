from typing import Dict, Any, Optional, List
from .base_providers import BaseLLMProvider
import os
import json
from openai import OpenAI
import anthropic

class LLMProvider(BaseLLMProvider):
    def __init__(self):
        """Initialize the LLM provider based on environment variables."""
        self.provider_type = os.getenv("LLM_PROVIDER", "openai").lower()
        
        if self.provider_type == "openai":
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        elif self.provider_type == "claude":
            self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            self.model = os.getenv("CLAUDE_MODEL", "claude-3-opus-20240229")
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider_type}")

    def generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a completion using the selected LLM provider."""
        try:
            if self.provider_type == "openai":
                return self._generate_openai_completion(prompt, system_prompt, response_format)
            else:
                return self._generate_claude_completion(prompt, system_prompt, response_format)
        except Exception as e:
            print(f"Error generating completion: {str(e)}")
            raise

    def _generate_openai_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate completion using OpenAI."""
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

    def _generate_claude_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate completion using Claude."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        if response_format and response_format.get("type") == "json_object":
            messages.append({
                "role": "assistant",
                "content": "I will respond in valid JSON format."
            })

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            messages=messages,
            temperature=0.7
        )
        
        completion = response.content[0].text
        
        if response_format and response_format.get("type") == "json_object":
            try:
                json.loads(completion)
            except json.JSONDecodeError:
                completion = self._fix_json_response(completion)
        
        return completion

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embeddings for the given text."""
        try:
            if self.provider_type == "openai":
                return self._generate_openai_embedding(text)
            else:
                return self._generate_claude_embedding(text)
        except Exception as e:
            print(f"Error generating embedding: {str(e)}")
            raise

    def _generate_openai_embedding(self, text: str) -> List[float]:
        """Generate embeddings using OpenAI."""
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding

    def _generate_claude_embedding(self, text: str) -> List[float]:
        """Generate embeddings using Claude."""
        prompt = f"""
        Generate a semantic representation for the following text.
        Return it as a JSON array of 1536 numbers between -1 and 1.
        
        Text: {text}
        """
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        return json.loads(response.content[0].text)

    def _fix_json_response(self, text: str) -> str:
        """Attempt to fix invalid JSON responses."""
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = text[start:end]
                json.loads(json_str)
                return json_str
            raise ValueError("No valid JSON found")
        except:
            return '{"error": "Could not generate valid JSON response"}' 
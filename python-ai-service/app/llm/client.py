import os
from typing import Optional
from openai import OpenAI


class LLMClient:
    """
    Unified LLM client supporting multiple providers (OpenAI, Claude, Gemini)
    """
    
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "openai").lower()
        self.model = os.getenv("LLM_MODEL", "gpt-4")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "2000"))
        
        # Initialize client based on provider
        if self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set in environment")
            self.client = OpenAI(api_key=api_key)
        elif self.provider == "gemini":
            try:
                import google.generativeai as genai
                api_key = os.getenv("GOOGLE_API_KEY")
                if not api_key:
                    raise ValueError("GOOGLE_API_KEY not set in environment")
                genai.configure(api_key=api_key)
                # Default to gemini-pro if not specified
                if self.model in ["gpt-4", "gpt-3.5-turbo"]:
                    self.model = "gemini-pro"
                self.client = genai
            except ImportError:
                raise ValueError(
                    "google-generativeai package not installed. "
                    "Run: pip install google-generativeai"
                )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate text completion from the LLM
        
        Args:
            prompt: User prompt
            system_prompt: Optional system instructions
            temperature: Override default temperature
            
        Returns:
            Generated text response
        """
        temp = temperature if temperature is not None else self.temperature
        
        if self.provider == "openai":
            return await self._generate_openai(prompt, system_prompt, temp)
        elif self.provider == "gemini":
            return await self._generate_gemini(prompt, system_prompt, temp)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    async def _generate_openai(
        self, 
        prompt: str, 
        system_prompt: Optional[str],
        temperature: float
    ) -> str:
        """Generate using OpenAI API"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    async def _generate_gemini(
        self, 
        prompt: str, 
        system_prompt: Optional[str],
        temperature: float
    ) -> str:
        """Generate using Google Gemini API"""
        # Combine system and user prompts for Gemini
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        try:
            model = self.client.GenerativeModel(self.model)
            
            # Configure generation
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": self.max_tokens,
            }
            
            # Generate response
            response = model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            return response.text.strip()
            
        except Exception as e:
            raise Exception(f"Google Gemini API error: {str(e)}")

    def is_available(self) -> bool:
        """Check if LLM client is properly configured"""
        try:
            if self.provider == "openai":
                return bool(os.getenv("OPENAI_API_KEY"))
            elif self.provider == "gemini":
                return bool(os.getenv("GOOGLE_API_KEY"))
            return False
        except Exception:
            return False

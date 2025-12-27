"""
LLM Gateway
============
Handles all communication with the LLM API via Portkey.
"""

import logging
import time
from collections import deque
from dataclasses import dataclass
from typing import Dict, Optional

logger = logging.getLogger("rag.llm_gateway")


@dataclass
class LLMResponse:
    """Structured response from the LLM."""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    latency_ms: float = 0.0
    success: bool = True
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "content": self.content,
            "model": self.model,
            "usage": self.usage,
            "latency_ms": self.latency_ms,
            "success": self.success,
            "error": self.error
        }


class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, max_calls: int = 10, period_seconds: int = 60):
        self.max_calls = max_calls
        self.period = period_seconds
        self.calls: deque = deque()
    
    def wait_if_needed(self):
        """Block if rate limit would be exceeded."""
        now = time.time()
        while self.calls and self.calls[0] < now - self.period:
            self.calls.popleft()
        if len(self.calls) >= self.max_calls:
            sleep_time = self.calls[0] + self.period - now
            if sleep_time > 0:
                time.sleep(sleep_time)
        self.calls.append(time.time())


class LLMGateway:
    """Gateway for LLM API calls via Portkey with retry and rate limiting."""
    
    def __init__(
        self, 
        api_key: Optional[str],
        model: str,
        max_tokens: int = 512
    ):
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.client = None
        self.rate_limiter = RateLimiter(max_calls=10, period_seconds=60)
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Portkey client."""
        if not self.api_key:
            logger.warning("No API key configured. LLM calls will fail.")
            return
        
        try:
            from portkey_ai import Portkey
            self.client = Portkey(api_key=self.api_key)
            logger.info("✓ Portkey client initialized")
        except ImportError:
            logger.error("portkey_ai not installed. Run: pip install portkey-ai")
        except Exception as e:
            logger.error(f"Failed to initialize Portkey client: {e}")
    
    def generate(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        max_tokens: Optional[int] = None,
        temperature: float = 0.7, 
        max_retries: int = 3
    ) -> LLMResponse:
        """Generate a response from the LLM."""
        if self.client is None:
            return LLMResponse(
                content="", 
                model=self.model, 
                success=False,
                error="LLM client not initialized. Check API key."
            )
        
        max_tokens = max_tokens or self.max_tokens
        
        for attempt in range(max_retries):
            try:
                self.rate_limiter.wait_if_needed()
                start_time = time.time()
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                
                latency_ms = (time.time() - start_time) * 1000
                
                if not response.choices:
                    raise ValueError("No choices in response")
                
                content = response.choices[0].message.content or ""
                usage = None
                if hasattr(response, 'usage') and response.usage:
                    usage = {
                        "prompt_tokens": getattr(response.usage, 'prompt_tokens', 0),
                        "completion_tokens": getattr(response.usage, 'completion_tokens', 0),
                        "total_tokens": getattr(response.usage, 'total_tokens', 0),
                    }
                
                logger.info(f"LLM response: {latency_ms:.0f}ms ({len(content)} chars)")
                
                return LLMResponse(
                    content=content, 
                    model=self.model,
                    usage=usage, 
                    latency_ms=latency_ms, 
                    success=True
                )
                
            except Exception as e:
                logger.warning(f"LLM call failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                # Final attempt failed - return error
                return LLMResponse(
                    content="", 
                    model=self.model, 
                    success=False,
                    error=f"LLM call failed after {max_retries} attempts: {e}"
                )
        
        # This should only be reached if max_retries is 0
        return LLMResponse(
            content="", 
            model=self.model, 
            success=False,
            error="No retry attempts configured"
        )


# System prompts for different use cases
SYSTEM_PROMPTS = {
    "default": """You are a helpful research assistant for studying documents.
You help users understand and analyze the content of their uploaded documents.

When answering:
1. Use ONLY the provided CONTEXT to answer
2. Cite specific documents and quote relevant passages
3. If context is insufficient, clearly state what's missing
4. Be precise and avoid speculation
5. If the documents don't contain relevant information, say so""",

    "summary": """Summarize the key information from the provided context.
Focus on main themes, important details, and relevant patterns.
Cite specific documents when possible.""",
    
    "analysis": """Provide a detailed analysis of the information in the context.
Look for patterns, connections, and significant insights.
Support your analysis with specific references to the documents.""",
}


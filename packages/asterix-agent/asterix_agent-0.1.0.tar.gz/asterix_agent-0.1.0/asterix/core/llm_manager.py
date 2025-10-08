"""
MemGPT LLM Provider Manager

Provides intelligent routing and management for LLM providers with:
- Health-aware routing between Groq and OpenAI
- Automatic fallback and retry logic
- Configuration-driven provider switching
- Comprehensive error handling and monitoring
- Usage tracking and performance metrics
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timezone

import openai
import httpx
from groq import Groq

from ..utils.config import get_config
from ..utils.health import health_monitor
from ..utils.tokens import count_tokens

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Response from LLM provider"""
    content: str
    model: str
    provider: str
    usage: Dict[str, int]
    processing_time: float
    finish_reason: str
    raw_response: Optional[Dict] = None


@dataclass
class LLMMessage:
    """Message for LLM conversation"""
    role: str
    content: str


class LLMError(Exception):
    """Raised when LLM operations fail"""
    pass


class LLMProviderManager:
    """
    Intelligent manager for LLM providers with health-aware routing.
    
    Features:
    - Automatic provider selection based on health status
    - Intelligent fallback between Groq and OpenAI
    - Configuration-driven model selection and parameters
    - Comprehensive error handling and retry logic
    - Usage tracking and performance monitoring
    """
    
    def __init__(self):
        """Initialize the LLM provider manager."""
        self.config = get_config()
        
        # Provider configurations
        self._groq_config = self.config.get_llm_config("groq")
        self._openai_config = self.config.get_llm_config("openai")
        
        # Provider clients
        self._groq_client: Optional[Groq] = None
        self._openai_client: Optional[openai.OpenAI] = None
        
        # Provider selection
        self._primary_provider = self.config.get_yaml_config(
            "agent_config.yaml", 
            "agent.llm.primary_provider", 
            "groq"
        )
        self._fallback_provider = self.config.get_yaml_config(
            "agent_config.yaml", 
            "agent.llm.fallback_provider", 
            "openai"
        )
        
        # Health tracking
        self._provider_health = {}
        self._last_health_check = 0
        self._health_check_interval = 45  # seconds
        self._provider_failures = {"groq": 0, "openai": 0}
        self._max_failures = 3
        
        # Performance tracking
        self._operation_count = {"groq": 0, "openai": 0}
        self._total_processing_time = {"groq": 0.0, "openai": 0.0}
        self._total_tokens = {"groq": 0, "openai": 0}
        self._error_count = {"groq": 0, "openai": 0}
    
    async def _ensure_clients_initialized(self):
        """Ensure LLM provider clients are initialized."""
        # Initialize Groq client
        if self._groq_client is None and self._groq_config.api_key:
            self._groq_client = Groq(api_key=self._groq_config.api_key)
        
        # Initialize OpenAI client
        if self._openai_client is None and self._openai_config.api_key:
            self._openai_client = openai.OpenAI(api_key=self._openai_config.api_key)
    
    async def _check_provider_health(self) -> Dict[str, bool]:
        """
        Check health of LLM providers.
        
        Returns:
            Dictionary mapping provider names to health status
        """
        current_time = time.time()
        if (current_time - self._last_health_check) < self._health_check_interval:
            return self._provider_health
        
        health_status = {}
        
        # Check Groq health
        groq_health = await health_monitor.check_groq_health()
        health_status["groq"] = groq_health.status == "healthy"
        
        # Check OpenAI health
        openai_health = await health_monitor.check_openai_health("llm")
        health_status["openai"] = openai_health.status == "healthy"
        
        self._provider_health = health_status
        self._last_health_check = current_time
        
        return health_status
    
    async def _select_provider(self, force_provider: Optional[str] = None) -> str:
        """
        Select the best available provider based on health and failure rates.
        
        Args:
            force_provider: Force use of specific provider
            
        Returns:
            Name of the selected provider
        """
        if force_provider:
            return force_provider
        
        health_status = await self._check_provider_health()
        
        # Check if primary provider is healthy and hasn't failed too much
        if (health_status.get(self._primary_provider, False) and 
            self._provider_failures[self._primary_provider] < self._max_failures):
            return self._primary_provider
        
        # Fall back to fallback provider
        if (health_status.get(self._fallback_provider, False) and 
            self._provider_failures[self._fallback_provider] < self._max_failures):
            logger.warning(f"Primary provider {self._primary_provider} unavailable, using fallback {self._fallback_provider}")
            return self._fallback_provider
        
        # If both have issues, reset failure counts and try primary
        if (self._provider_failures[self._primary_provider] >= self._max_failures and
            self._provider_failures[self._fallback_provider] >= self._max_failures):
            logger.warning("Both providers have failed multiple times, resetting failure counts")
            self._provider_failures = {"groq": 0, "openai": 0}
        
        # Default to primary provider
        return self._primary_provider
    
    async def _call_groq(self, messages: List[LLMMessage], 
                        temperature: Optional[float] = None,
                        max_tokens: Optional[int] = None) -> LLMResponse:
        """
        Call Groq API for completion.
        
        Args:
            messages: List of conversation messages
            temperature: Temperature override
            max_tokens: Max tokens override
            
        Returns:
            LLM response object
        """
        if not self._groq_client:
            raise LLMError("Groq client not initialized")
        
        start_time = time.time()
        
        try:
            # Prepare messages
            groq_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            # Make API call
            response = self._groq_client.chat.completions.create(
                model=self._groq_config.model,
                messages=groq_messages,
                temperature=temperature or self._groq_config.temperature,
                max_tokens=max_tokens or self._groq_config.max_tokens,
                stream=False
            )
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Extract response data
            content = response.choices[0].message.content or ""
            finish_reason = response.choices[0].finish_reason or "unknown"
            
            # Build usage stats
            usage = {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0
            }
            
            # Update metrics
            self._operation_count["groq"] += 1
            self._total_processing_time["groq"] += processing_time
            self._total_tokens["groq"] += usage["total_tokens"]
            
            # Reset failure count on success
            self._provider_failures["groq"] = 0
            
            result = LLMResponse(
                content=content,
                model=self._groq_config.model,
                provider="groq",
                usage=usage,
                processing_time=processing_time,
                finish_reason=finish_reason,
                raw_response=response.model_dump() if hasattr(response, 'model_dump') else None
            )
            
            logger.info(f"Groq completion: {usage['total_tokens']} tokens in {processing_time:.3f}s")
            return result
            
        except Exception as e:
            self._error_count["groq"] += 1
            self._provider_failures["groq"] += 1
            logger.error(f"Groq API error: {e}")
            raise LLMError(f"Groq error: {e}")
    
    async def _call_openai(self, messages: List[LLMMessage],
                          temperature: Optional[float] = None,
                          max_tokens: Optional[int] = None) -> LLMResponse:
        """
        Call OpenAI API for completion.
        
        Args:
            messages: List of conversation messages
            temperature: Temperature override
            max_tokens: Max tokens override
            
        Returns:
            LLM response object
        """
        if not self._openai_client:
            raise LLMError("OpenAI client not initialized")
        
        start_time = time.time()
        
        try:
            # Prepare messages
            openai_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            # Make API call
            response = self._openai_client.chat.completions.create(
                model=self._openai_config.model,
                messages=openai_messages,
                temperature=temperature or self._openai_config.temperature,
                max_tokens=max_tokens or self._openai_config.max_tokens,
                stream=False
            )
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Extract response data
            content = response.choices[0].message.content or ""
            finish_reason = response.choices[0].finish_reason or "unknown"
            
            # Build usage stats
            usage = {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0
            }
            
            # Update metrics
            self._operation_count["openai"] += 1
            self._total_processing_time["openai"] += processing_time
            self._total_tokens["openai"] += usage["total_tokens"]
            
            # Reset failure count on success
            self._provider_failures["openai"] = 0
            
            result = LLMResponse(
                content=content,
                model=self._openai_config.model,
                provider="openai",
                usage=usage,
                processing_time=processing_time,
                finish_reason=finish_reason,
                raw_response=response.model_dump() if hasattr(response, 'model_dump') else None
            )
            
            logger.info(f"OpenAI completion: {usage['total_tokens']} tokens in {processing_time:.3f}s")
            return result
            
        except openai.RateLimitError as e:
            self._error_count["openai"] += 1
            self._provider_failures["openai"] += 1
            logger.error(f"OpenAI rate limit: {e}")
            raise LLMError(f"OpenAI rate limit: {e}")
        except openai.AuthenticationError as e:
            self._error_count["openai"] += 1
            self._provider_failures["openai"] += 1
            logger.error(f"OpenAI authentication failed: {e}")
            raise LLMError(f"OpenAI authentication failed: {e}")
        except Exception as e:
            self._error_count["openai"] += 1
            self._provider_failures["openai"] += 1
            logger.error(f"OpenAI API error: {e}")
            raise LLMError(f"OpenAI error: {e}")
    
    async def complete(self, messages: Union[str, List[LLMMessage]],
                      provider: Optional[str] = None,
                      temperature: Optional[float] = None,
                      max_tokens: Optional[int] = None,
                      retry_on_failure: bool = True) -> LLMResponse:
        """
        Generate completion using the best available provider.
        
        Args:
            messages: Single message string or list of conversation messages
            provider: Force specific provider (optional)
            temperature: Temperature override
            max_tokens: Max tokens override
            retry_on_failure: Whether to retry with fallback provider on failure
            
        Returns:
            LLM response object
            
        Raises:
            LLMError: If completion fails
        """
        # Normalize input
        if isinstance(messages, str):
            messages = [LLMMessage(role="user", content=messages)]
        
        if not messages:
            raise LLMError("No messages provided for completion")
        
        # Ensure clients are initialized
        await self._ensure_clients_initialized()
        
        # Select provider
        selected_provider = await self._select_provider(provider)
        
        try:
            # Call the appropriate provider
            if selected_provider == "groq":
                return await self._call_groq(messages, temperature, max_tokens)
            elif selected_provider == "openai":
                return await self._call_openai(messages, temperature, max_tokens)
            else:
                raise LLMError(f"Unknown provider: {selected_provider}")
                
        except LLMError as e:
            # If retry is enabled and we haven't tried the fallback yet
            if (retry_on_failure and 
                not provider and  # Don't retry if specific provider was requested
                selected_provider != self._fallback_provider):
                
                logger.warning(f"Provider {selected_provider} failed, trying fallback {self._fallback_provider}")
                return await self.complete(
                    messages, 
                    provider=self._fallback_provider,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    retry_on_failure=False  # Prevent infinite recursion
                )
            else:
                raise
    
    async def summarize_text(self, text: str, 
                           max_tokens: int = 220,
                           provider: Optional[str] = None) -> LLMResponse:
        """
        Summarize text using the configured summarization prompt.
        
        Args:
            text: Text to summarize
            max_tokens: Maximum tokens for summary
            provider: Force specific provider
            
        Returns:
            LLM response with summary
        """
        # Get summarization prompt from config
        summary_prompt = self.config.get_yaml_config(
            "memory_config.yaml",
            "summarization.prompts.default",
            "Summarize the following text in {max_tokens} tokens or less:\n\n{content}"
        )
        
        # Format prompt
        formatted_prompt = summary_prompt.format(
            max_tokens=max_tokens,
            content=text,
            original_tokens=count_tokens(text).tokens
        )
        
        messages = [LLMMessage(role="user", content=formatted_prompt)]
        
        return await self.complete(
            messages,
            provider=provider,
            temperature=0.1,  # Low temperature for consistent summaries
            max_tokens=max_tokens + 50  # Small buffer for formatting
        )
    
    async def extract_keywords(self, text: str,
                             max_keywords: int = 10,
                             provider: Optional[str] = None) -> List[str]:
        """
        Extract keywords from text.
        
        Args:
            text: Text to extract keywords from
            max_keywords: Maximum number of keywords
            provider: Force specific provider
            
        Returns:
            List of extracted keywords
        """
        prompt = f"""Extract the {max_keywords} most important keywords from the following text.
Return only the keywords separated by commas, no other text.

Text: {text}

Keywords:"""
        
        messages = [LLMMessage(role="user", content=prompt)]
        
        response = await self.complete(
            messages,
            provider=provider,
            temperature=0.1,
            max_tokens=100
        )
        
        # Parse keywords
        keywords = [
            keyword.strip() 
            for keyword in response.content.split(",")
            if keyword.strip()
        ]
        
        return keywords[:max_keywords]
    
    def get_provider_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        Get configuration for all providers.
        
        Returns:
            Dictionary with provider configurations
        """
        return {
            "groq": {
                "model": self._groq_config.model,
                "temperature": self._groq_config.temperature,
                "max_tokens": self._groq_config.max_tokens,
                "timeout": self._groq_config.timeout,
                "api_key_configured": bool(self._groq_config.api_key)
            },
            "openai": {
                "model": self._openai_config.model,
                "temperature": self._openai_config.temperature,
                "max_tokens": self._openai_config.max_tokens,
                "timeout": self._openai_config.timeout,
                "api_key_configured": bool(self._openai_config.api_key)
            }
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for all providers.
        
        Returns:
            Dictionary with performance information
        """
        metrics = {
            "primary_provider": self._primary_provider,
            "fallback_provider": self._fallback_provider,
            "provider_health": self._provider_health,
            "provider_failures": self._provider_failures,
            "providers": {}
        }
        
        for provider in ["groq", "openai"]:
            operation_count = self._operation_count[provider]
            avg_processing_time = (
                self._total_processing_time[provider] / operation_count
                if operation_count > 0 else 0
            )
            
            metrics["providers"][provider] = {
                "operation_count": operation_count,
                "error_count": self._error_count[provider],
                "total_tokens": self._total_tokens[provider],
                "total_processing_time_ms": round(self._total_processing_time[provider] * 1000, 2),
                "average_processing_time_ms": round(avg_processing_time * 1000, 2),
                "failure_count": self._provider_failures[provider],
                "success_rate": round(
                    (operation_count - self._error_count[provider]) / operation_count * 100, 2
                ) if operation_count > 0 else 0
            }
        
        return metrics
    
    async def test_provider(self, provider: str) -> Dict[str, Any]:
        """
        Test a specific LLM provider.
        
        Args:
            provider: Provider name to test
            
        Returns:
            Test result with performance metrics
        """
        test_message = "Hello! Please respond with exactly: 'Test successful'"
        
        try:
            start_time = time.time()
            response = await self.complete([LLMMessage(role="user", content=test_message)], provider=provider)
            total_time = time.time() - start_time
            
            return {
                "provider": provider,
                "status": "healthy",
                "response_time_ms": round(total_time * 1000, 2),
                "model": response.model,
                "usage": response.usage,
                "response_content": response.content[:100] + "..." if len(response.content) > 100 else response.content
            }
            
        except Exception as e:
            return {
                "provider": provider,
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": None,
                "model": None,
                "usage": None,
                "response_content": None
            }


# Global LLM manager instance
llm_manager = LLMProviderManager()
"""
llm/factory.py

Selects the LLM provider based on the LLM_PROVIDER env variable.
Default: gemini

Usage:
    from llm.factory import get_llm_client
    client = get_llm_client()

To switch providers, set in .env:
    LLM_PROVIDER=openai   → uses OpenAIClient (requires OPENAI_API_KEY)
    LLM_PROVIDER=gemini   → uses GeminiClient (requires GEMINI_API_KEY)
"""

import os
import logging

from llm.client import LLMClient

logger = logging.getLogger(__name__)

SUPPORTED_PROVIDERS = ("gemini", "openai")


def get_llm_client() -> LLMClient:
    provider = os.getenv("LLM_PROVIDER", "gemini").lower().strip()
    logger.info(f"LLM provider selected: {provider}")

    if provider == "openai":
        from llm.openai_client import OpenAIClient
        return OpenAIClient()

    if provider == "gemini":
        from llm.gemini_client import GeminiClient
        return GeminiClient()

    raise ValueError(
        f"Unknown LLM_PROVIDER '{provider}'. "
        f"Choose one of: {', '.join(SUPPORTED_PROVIDERS)}"
    )

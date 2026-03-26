"""
llm/client.py  [Phase 3]

Abstract interface for any LLM provider.
Swap OpenAI for Anthropic, Mistral, Ollama, etc. — just implement this.
"""

from abc import ABC, abstractmethod


class LLMClient(ABC):

    @abstractmethod
    def generate(self, topics: list[str]) -> str:
        """
        Given a list of topics, return a raw HTML string
        containing one <section> per topic.
        """
        ...

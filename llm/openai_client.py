"""
llm/openai_client.py  [Phase 3]

OpenAI implementation of LLMClient.
Reads API key and model from environment variables.
"""

import os
import logging

from openai import OpenAI

from llm.client import LLMClient
from llm.prompt_template import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)


class OpenAIClient(LLMClient):

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "OPENAI_API_KEY is not set. "
                "Copy .env.example to .env and add your key."
            )
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        self.client = OpenAI(api_key=api_key)
        logger.info(f"OpenAI client initialized with model: {self.model}")

    def generate(self, topics: list[str]) -> str:
        logger.info(f"Sending {len(topics)} topic(s) to OpenAI...")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(topics)},
            ],
            temperature=0.7,
        )

        content = response.choices[0].message.content.strip()
        logger.info("LLM response received.")
        return content

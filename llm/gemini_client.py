"""
llm/gemini_client.py  [Phase 3 — Gemini Provider]

Google Gemini implementation of LLMClient.
Uses the new google-genai SDK (google.generativeai is deprecated).
Controlled via env vars:
  GEMINI_API_KEY   — required
  LLM_MODEL        — optional, default: gemini-2.0-flash
"""

import os
import logging

from google import genai
from google.genai import types

from llm.client import LLMClient
from llm.prompt_template import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)


class GeminiClient(LLMClient):

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY is not set. "
                "Copy .env.example to .env and add your key."
            )

        self.model_name = os.getenv("LLM_MODEL", "gemini-2.0-flash")
        self.client = genai.Client(api_key=api_key)
        logger.info(f"Gemini client initialized with model: {self.model_name}")

    def generate(self, topics: list[str]) -> str:
        logger.info(f"Sending {len(topics)} topic(s) to Gemini...")

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=build_user_prompt(topics),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
            ),
        )

        content = response.text.strip()
        logger.info("Gemini response received.")
        return content

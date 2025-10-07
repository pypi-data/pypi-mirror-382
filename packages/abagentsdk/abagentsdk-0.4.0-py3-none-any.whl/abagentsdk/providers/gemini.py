# abagent/providers/gemini.py
from __future__ import annotations

import google.generativeai as genai
from typing import Optional

from .base import ModelProvider
from ..config import SDKConfig


class GeminiProvider(ModelProvider):
    """
    Thin wrapper around google-generativeai. Requires a valid API key.
    """

    def __init__(self, config: SDKConfig):
        # Enforce that the user provided an API key
        self.config = config.require_key()
        genai.configure(api_key=self.config.api_key)

        # Lazily create model object on first call (supports model switching per request if needed)
        self._model_name = self.config.model
        self._model: Optional[genai.GenerativeModel] = None

    @property
    def model(self) -> genai.GenerativeModel:
        if self._model is None or getattr(self._model, "model_name", None) != self._model_name:
            self._model = genai.GenerativeModel(self._model_name)
        return self._model

    def generate(self, prompt: str) -> str:
        """Return plain text from Gemini for a given prompt string."""
        resp = self.model.generate_content(prompt)
        # google-generativeai returns .text for simple text outputs
        return getattr(resp, "text", "") or ""

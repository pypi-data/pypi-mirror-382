import os
import google.generativeai as genai
from ..config import SDKConfig
from .base import ModelProvider
from abagentsdk import config


SYSTEM_INSTRUCTIONS = (
"You are ABZ Agent. Think step-by-step. If a TOOL is needed, respond ONLY with a JSON object\n"
"of the form {\"tool\": \"<name>\", \"args\": { ... }}. Otherwise, respond with a\n"
"final natural-language answer. Do not include extra text with the JSON."
)


class GeminiProvider(ModelProvider):
    def __init__(self, config: SDKConfig):
        config.require_key()
        genai.configure(api_key=config.api_key)
        self.model = genai.GenerativeModel(config.model, system_instruction=SYSTEM_INSTRUCTIONS)
        self.temperature = config.temperature

    def generate(self, prompt: str) -> str:
        resp = self.model.generate_content(prompt, generation_config={
            "temperature": self.temperature,
        })
        # Handle both text and candidates structures
        try:
            return resp.text
        except Exception:
            # Fallback: concatenate parts
            parts = []
            for cand in getattr(resp, "candidates", []) or []:
                for p in getattr(cand, "content", {}).get("parts", []):
                    if isinstance(p, dict) and "text" in p:
                        parts.append(p["text"])
            return "\n".join(parts) if parts else ""
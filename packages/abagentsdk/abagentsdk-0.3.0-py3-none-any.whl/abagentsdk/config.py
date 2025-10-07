# abagent/config.py
from dataclasses import dataclass
import os

@dataclass
class SDKConfig:
    model: str = os.getenv("ABZ_GEMINI_MODEL", "models/gemini-2.0-flash-exp")
    api_key: str = os.getenv("GEMINI_API_KEY", "")
    temperature: float = float(os.getenv("ABZ_TEMPERATURE", "0.4"))
    max_iterations: int = int(os.getenv("ABZ_MAX_ITERS", "4"))
    verbose: bool = os.getenv("ABZ_VERBOSE", "1") == "1"

    def require_key(self) -> "SDKConfig":
        if not self.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Set it in your environment before running."
            )
        return self

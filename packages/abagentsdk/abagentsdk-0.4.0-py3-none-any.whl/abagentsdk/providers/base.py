from abc import ABC, abstractmethod
from typing import Iterable


class ModelProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Return a single text completion for the given prompt."""
...
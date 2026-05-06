from __future__ import annotations

from abc import ABC, abstractmethod


class BaseLLMClient(ABC):
    provider: str
    model: str

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        raise NotImplementedError

    async def embed(self, text: str) -> list[float]:
        values = [float(((ord(char) * (idx + 1)) % 97) / 97) for idx, char in enumerate(text[:64])]
        if not values:
            values = [0.0]
        target_length = 64
        if len(values) < target_length:
            values.extend([0.0] * (target_length - len(values)))
        return values[:target_length]


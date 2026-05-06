from __future__ import annotations

import json

import httpx

from app.services.llm.base import BaseLLMClient


class MockLLMClient(BaseLLMClient):
    def __init__(self, provider: str = "mock", model: str = "mock-analyst"):
        self.provider = provider
        self.model = model

    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        return json.dumps(
            {
                "summary": "Mock analysis generated because no external LLM key is configured.",
                "sentiment": "neutral-positive",
                "impact": "medium",
                "reasoning": prompt[:600],
            },
            ensure_ascii=False,
        )


class OpenAICompatibleClient(BaseLLMClient):
    def __init__(self, provider: str, api_key: str, model: str, base_url: str, timeout: int):
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt or "You are a financial analyst."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        return data["choices"][0]["message"]["content"]


class AnthropicClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str, timeout: int):
        self.provider = "anthropic"
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        payload = {
            "model": self.model,
            "system": system_prompt or "You are a financial analyst.",
            "max_tokens": 1200,
            "messages": [{"role": "user", "content": prompt}],
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                },
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        return "".join(block["text"] for block in data["content"] if block["type"] == "text")


from __future__ import annotations

from app.core.settings import Settings
from app.services.llm.base import BaseLLMClient
from app.services.llm.clients import AnthropicClient, MockLLMClient, OpenAICompatibleClient


class LLMFactory:
    def __init__(self, settings: Settings):
        self.settings = settings

    def status(self) -> dict:
        return {
            "available": self.available_providers(),
            "default": self.get_default_provider_name(),
        }

    def available_providers(self) -> list[str]:
        providers: list[str] = []
        if self.settings.openai_api_key:
            providers.append("gpt")
        if self.settings.anthropic_api_key:
            providers.append("claude")
        if self.settings.deepseek_api_key:
            providers.append("deepseek")
        if self.settings.kimi_api_key:
            providers.append("kimi")
        if self.settings.minimax_api_key:
            providers.append("minimax")
        if self.settings.chatglm_api_key:
            providers.append("chatglm")
        if self.settings.enable_mocks or not providers:
            providers.append("mock")
        return providers

    def get_default_provider_name(self) -> str:
        if self.settings.default_llm_provider:
            return self.settings.default_llm_provider
        if self.settings.enable_mocks:
            return "mock"
        available = self.available_providers()
        return available[0]

    def create(self, preferred: str | None = None) -> BaseLLMClient:
        provider = (preferred or self.get_default_provider_name()).lower()
        s = self.settings
        if provider in {"gpt", "openai"} and s.openai_api_key:
            return OpenAICompatibleClient(
                provider="gpt",
                api_key=s.openai_api_key,
                model=s.openai_model,
                base_url=s.openai_base_url or "https://api.openai.com/v1",
                timeout=s.request_timeout,
            )
        if provider in {"claude", "anthropic"} and s.anthropic_api_key:
            return AnthropicClient(s.anthropic_api_key, s.anthropic_model, s.request_timeout)
        if provider == "deepseek" and s.deepseek_api_key:
            return OpenAICompatibleClient(
                provider="deepseek",
                api_key=s.deepseek_api_key,
                model=s.deepseek_model,
                base_url=s.deepseek_base_url or "https://api.deepseek.com",
                timeout=s.request_timeout,
            )
        if provider == "kimi" and s.kimi_api_key:
            return OpenAICompatibleClient(
                provider="kimi",
                api_key=s.kimi_api_key,
                model=s.kimi_model,
                base_url=s.kimi_base_url or "https://api.moonshot.cn/v1",
                timeout=s.request_timeout,
            )
        if provider == "minimax" and s.minimax_api_key:
            return OpenAICompatibleClient(
                provider="minimax",
                api_key=s.minimax_api_key,
                model=s.minimax_model,
                base_url=s.minimax_base_url or "https://api.minimax.chat/v1",
                timeout=s.request_timeout,
            )
        if provider == "chatglm" and s.chatglm_api_key:
            return OpenAICompatibleClient(
                provider="chatglm",
                api_key=s.chatglm_api_key,
                model=s.chatglm_model,
                base_url=s.chatglm_base_url or "https://open.bigmodel.cn/api/paas/v4",
                timeout=s.request_timeout,
            )
        return MockLLMClient(provider="mock", model="mock-analyst")

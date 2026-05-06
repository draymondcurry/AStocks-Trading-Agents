from __future__ import annotations

from app.core.settings import Settings
from app.services.search.base import BaseSearchProvider
from app.services.search.providers import (
    BochaSearchProvider,
    GoogleSearchProvider,
    MockSearchProvider,
)


class SearchFactory:
    def __init__(self, settings: Settings):
        self.settings = settings

    def available_providers(self) -> list[str]:
        providers: list[str] = []
        if self.settings.bocha_api_key:
            providers.append("bocha")
        if self.settings.google_search_api_key and self.settings.google_search_cx:
            providers.append("google")
        if self.settings.enable_mocks or not providers:
            providers.append("mock")
        return providers

    def get_default_provider_name(self) -> str:
        if self.settings.default_search_provider:
            return self.settings.default_search_provider
        if self.settings.enable_mocks:
            return "mock"
        return self.available_providers()[0]

    def status(self) -> dict:
        return {
            "available": self.available_providers(),
            "default": self.get_default_provider_name(),
        }

    def create(self, preferred: str | None = None) -> BaseSearchProvider:
        provider = (preferred or self.get_default_provider_name()).lower()
        s = self.settings
        if provider == "bocha" and s.bocha_api_key:
            return BochaSearchProvider(s.bocha_api_key, s.bocha_base_url, s.request_timeout)
        if provider == "google" and s.google_search_api_key and s.google_search_cx:
            return GoogleSearchProvider(
                s.google_search_api_key,
                s.google_search_cx,
                s.request_timeout,
            )
        return MockSearchProvider()

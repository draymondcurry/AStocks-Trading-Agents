from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(alias="APP_NAME", default="AStock Alpha Engine")
    app_env: str = Field(alias="APP_ENV", default="dev")
    app_host: str = Field(alias="APP_HOST", default="0.0.0.0")
    app_port: int = Field(alias="APP_PORT", default=8000)
    log_level: str = Field(alias="LOG_LEVEL", default="INFO")
    default_llm_provider: str | None = Field(alias="DEFAULT_LLM_PROVIDER", default=None)
    default_search_provider: str | None = Field(
        alias="DEFAULT_SEARCH_PROVIDER", default=None
    )
    market_data_provider: str = Field(alias="MARKET_DATA_PROVIDER", default="akshare")
    memory_db_path: str = Field(alias="MEMORY_DB_PATH", default="./data/memory.db")
    request_timeout: int = Field(alias="REQUEST_TIMEOUT", default=30)
    short_memory_ttl_minutes: int = Field(
        alias="SHORT_MEMORY_TTL_MINUTES", default=240
    )
    long_memory_top_k: int = Field(alias="LONG_MEMORY_TOP_K", default=5)
    enable_mocks: bool = Field(alias="ENABLE_MOCKS", default=True)
    tui_backend_url: str = Field(
        alias="TUI_BACKEND_URL", default="http://127.0.0.1:8000"
    )
    tui_session_id: str = Field(alias="TUI_SESSION_ID", default="terminal-default")

    openai_api_key: str | None = Field(alias="OPENAI_API_KEY", default=None)
    openai_base_url: str | None = Field(alias="OPENAI_BASE_URL", default=None)
    openai_model: str = Field(alias="OPENAI_MODEL", default="gpt-4.1-mini")

    anthropic_api_key: str | None = Field(alias="ANTHROPIC_API_KEY", default=None)
    anthropic_model: str = Field(
        alias="ANTHROPIC_MODEL", default="claude-3-5-sonnet-latest"
    )

    deepseek_api_key: str | None = Field(alias="DEEPSEEK_API_KEY", default=None)
    deepseek_base_url: str | None = Field(alias="DEEPSEEK_BASE_URL", default=None)
    deepseek_model: str = Field(alias="DEEPSEEK_MODEL", default="deepseek-chat")

    kimi_api_key: str | None = Field(alias="KIMI_API_KEY", default=None)
    kimi_base_url: str | None = Field(alias="KIMI_BASE_URL", default=None)
    kimi_model: str = Field(alias="KIMI_MODEL", default="moonshot-v1-8k")

    minimax_api_key: str | None = Field(alias="MINIMAX_API_KEY", default=None)
    minimax_base_url: str | None = Field(alias="MINIMAX_BASE_URL", default=None)
    minimax_model: str = Field(alias="MINIMAX_MODEL", default="MiniMax-Text-01")

    chatglm_api_key: str | None = Field(alias="CHATGLM_API_KEY", default=None)
    chatglm_base_url: str | None = Field(alias="CHATGLM_BASE_URL", default=None)
    chatglm_model: str = Field(alias="CHATGLM_MODEL", default="glm-4-flash")

    bocha_api_key: str | None = Field(alias="BOCHA_API_KEY", default=None)
    bocha_base_url: str = Field(
        alias="BOCHA_BASE_URL", default="https://api.bochaai.com/v1/web-search"
    )
    google_search_api_key: str | None = Field(
        alias="GOOGLE_SEARCH_API_KEY", default=None
    )
    google_search_cx: str | None = Field(alias="GOOGLE_SEARCH_CX", default=None)


@lru_cache
def get_settings() -> Settings:
    return Settings()

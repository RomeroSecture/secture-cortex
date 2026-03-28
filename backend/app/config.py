"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql+asyncpg://cortex:cortex_dev@localhost:5432/cortex"

    # Deepgram
    deepgram_api_key: str = ""

    # LLM (Groq — OpenAI compatible)
    llm_base_url: str = "https://api.groq.com/openai/v1"
    llm_api_key: str = ""
    llm_model: str = "qwen/qwen3-32b"
    llm_fallback_model: str = "llama-3.1-8b-instant"

    # Embeddings (Jina — OpenAI compatible)
    embeddings_base_url: str = "https://api.jina.ai/v1"
    embeddings_api_key: str = ""
    embeddings_model: str = "jina-embeddings-v3"

    # Auth
    jwt_secret: str  # Required — no insecure default
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    # Agent pipeline (LangGraph multi-agent)
    agent_pipeline_enabled: bool = True
    supervisor_model: str = "qwen/qwen3-32b"
    specialist_model: str = "qwen/qwen3-32b"
    conversation_model: str = "llama-3.1-8b-instant"
    post_meeting_model: str = "qwen/qwen3-32b"

    # Role confidence thresholds (overridable per project via agent_configs)
    confidence_tech_lead: float = 0.6
    confidence_pm: float = 0.7
    confidence_developer: float = 0.6
    confidence_commercial: float = 0.85
    confidence_admin: float = 0.5

    # CORS
    allowed_origins: str = "http://localhost:3000"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

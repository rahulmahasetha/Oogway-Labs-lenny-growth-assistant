"""Application configuration loaded from environment variables."""


from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration for the Lenny Growth Assistant."""

    # --- Database ---
    database_url: str = Field(
        default="postgresql+asyncpg://lenny:lenny_secret@localhost:5432/lenny_growth",
        description="Async PostgreSQL connection string",
    )

    # --- LLM Provider ---
    llm_provider: str = Field(
        default="ollama",
        description="Active LLM provider: ollama, openai, or anthropic",
    )

    # --- Ollama ---
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama API base URL",
    )
    ollama_model: str = Field(
        default="llama3.2",
        description="Ollama model name",
    )

    # --- OpenAI ---
    openai_api_key: str | None = Field(
        default=None,
        description="OpenAI API key",
    )
    openai_model: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model name",
    )

    # --- Anthropic ---
    anthropic_api_key: str | None = Field(
        default=None,
        description="Anthropic API key",
    )
    anthropic_model: str = Field(
        default="claude-sonnet-4-20250514",
        description="Anthropic model name",
    )

    # --- Embedding ---
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        description="Sentence-transformers model for embeddings",
    )

    # --- RAG ---
    rag_top_k: int = Field(default=8, description="Number of chunks to retrieve")
    rag_similarity_threshold: float = Field(
        default=0.35, description="Minimum cosine similarity for retrieval"
    )

    # --- App ---
    data_dir: str = Field(default="./data", description="Path to transcript data")
    log_level: str = Field(default="INFO", description="Logging level")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

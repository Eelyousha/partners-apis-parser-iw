"""Configuration management using pydantic-settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ClickHouse
    clickhouse_host: str = "localhost"
    clickhouse_user: str = "default"
    clickhouse_password: str = ""
    clickhouse_database: str = "default"

    # MongoDB (for queue)
    mongodb_host: str = "mongodb://localhost:27017"

    # Partner M
    partner_m_ssp_access_token: str = ""
    partner_m_dsp_access_token: str = ""

    # Partner A
    partner_a_ssp_grant_type: str = ""
    partner_a_ssp_client_id: str = ""
    partner_a_ssp_username: str = ""
    partner_a_ssp_password: str = ""

    # Partner B SSP
    partner_b_ssp_login: str = ""
    partner_b_ssp_password: str = ""
    partner_b_ssp_user_id: int = 0

    # Partner B DSP
    partner_b_dsp_login: str = ""
    partner_b_dsp_password: str = ""
    partner_b_dsp_user_id: int = 0

    # Partner S DSP
    partner_s_dsp_login: str = ""
    partner_s_dsp_token: str = ""

    # DSP B
    dsp_b_access_token: str = ""

    # Superpartner
    superpartner_token: str = "verisecret"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

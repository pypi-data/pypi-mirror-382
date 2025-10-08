from typing import Tuple, Type, Optional

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    PydanticBaseSettingsSource,
)


class TranscodeConfig(BaseSettings):
    trim_cutoff: Optional[int] = None
    log_level: str = "INFO"
    log_as_json: bool = False

    model_config = SettingsConfigDict(
        env_file=(".env.default", ".env", ".env.local", ".env.dev", ".env.prod"),
        env_prefix="LQS_",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

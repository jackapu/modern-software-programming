from pydantic_settings import BaseSettings


class ActualConfig(BaseSettings):
    actual_server_url: str
    actual_password: str
    actual_file: str
    actual_encryption_password: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


_config: ActualConfig | None = None


def get_config() -> ActualConfig:
    global _config
    if _config is None:
        _config = ActualConfig()
    return _config

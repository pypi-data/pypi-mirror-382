from pydantic import SecretStr
from pydantic_settings import BaseSettings
from pydantic_settings_manager import SettingsManager


class CloudflareAuthSettings(BaseSettings):
    account_id: str

    api_token: SecretStr


settings_manager = SettingsManager(CloudflareAuthSettings, multi=True)

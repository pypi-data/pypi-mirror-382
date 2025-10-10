from pydantic_settings import BaseSettings
from pydantic_settings_manager import SettingsManager


class GoogleCloudStorageSettings(BaseSettings):
    google_auth_config_key: str | None = None

    bucket_name: str | None = None

    blob_name_prefix: str | None = None

    blob_name: str | None = None


settings_manager = SettingsManager(GoogleCloudStorageSettings, multi=True)

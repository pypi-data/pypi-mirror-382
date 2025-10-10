from typing import Any

from google.cloud import storage  # type: ignore[import-untyped]

from ._get_bucket import get_bucket
from .settings import settings_manager


def get_blob(
    config_key: str | None = None, blob_name: str | None = None, **kwargs: Any
) -> storage.Blob:
    settings = settings_manager.get_settings_by_key(config_key)

    if blob_name is None and settings.blob_name is None:
        raise ValueError("blob_name is not set in the settings and not provided")

    if blob_name is None:
        blob_name = settings.blob_name

    if settings.blob_name_prefix:
        blob_name = f"{settings.blob_name_prefix}/{blob_name}"

    bucket = get_bucket(config_key, **kwargs)
    return bucket.blob(blob_name)

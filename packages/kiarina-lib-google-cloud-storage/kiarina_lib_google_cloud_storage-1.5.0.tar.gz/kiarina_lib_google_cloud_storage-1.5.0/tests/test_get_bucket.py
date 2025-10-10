from unittest.mock import MagicMock, patch

import pytest

from kiarina.lib.google.cloud_storage import get_bucket, settings_manager


def test_get_bucket():
    # Setup settings
    settings_manager.user_config = {
        "default": {
            "google_auth_config_key": "test_auth",
            "bucket_name": "test-bucket",
        }
    }

    # Mock get_storage_client and bucket
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_bucket.name = "test-bucket"
    mock_client.bucket.return_value = mock_bucket

    with patch(
        "kiarina.lib.google.cloud_storage._get_bucket.get_storage_client",
        return_value=mock_client,
    ):
        bucket = get_bucket()
        assert bucket.name == "test-bucket"

        # Verify bucket was called with correct bucket name
        mock_client.bucket.assert_called_once_with("test-bucket")


def test_get_bucket_without_bucket_name():
    # Setup settings without bucket_name
    settings_manager.user_config = {
        "default": {
            "google_auth_config_key": "test_auth",
        }
    }

    with pytest.raises(ValueError, match="bucket_name is not set in the settings"):
        get_bucket()


def test_get_bucket_with_custom_config_key():
    # Setup settings with custom config key
    settings_manager.user_config = {
        "custom": {
            "google_auth_config_key": "custom_auth",
            "bucket_name": "custom-bucket",
        }
    }

    # Mock get_storage_client and bucket
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_bucket.name = "custom-bucket"
    mock_client.bucket.return_value = mock_bucket

    with patch(
        "kiarina.lib.google.cloud_storage._get_bucket.get_storage_client",
        return_value=mock_client,
    ) as mock_get_client:
        bucket = get_bucket(config_key="custom")
        assert bucket.name == "custom-bucket"

        # Verify get_storage_client was called with custom config key
        mock_get_client.assert_called_once_with("custom")

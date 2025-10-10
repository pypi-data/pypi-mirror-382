from unittest.mock import MagicMock, patch

import pytest

from kiarina.lib.google.cloud_storage import get_blob, settings_manager


def test_get_blob():
    # Setup settings
    settings_manager.user_config = {
        "default": {
            "google_auth_config_key": "test_auth",
            "bucket_name": "test-bucket",
            "blob_name": "test-blob.txt",
        }
    }

    # Mock get_bucket and blob
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_blob.name = "test-blob.txt"
    mock_bucket.blob.return_value = mock_blob

    with patch(
        "kiarina.lib.google.cloud_storage._get_blob.get_bucket",
        return_value=mock_bucket,
    ):
        blob = get_blob()
        assert blob.name == "test-blob.txt"

        # Verify blob was called with correct blob name
        mock_bucket.blob.assert_called_once_with("test-blob.txt")


def test_get_blob_with_blob_name_parameter():
    # Setup settings
    settings_manager.user_config = {
        "default": {
            "google_auth_config_key": "test_auth",
            "bucket_name": "test-bucket",
        }
    }

    # Mock get_bucket and blob
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_blob.name = "custom-blob.txt"
    mock_bucket.blob.return_value = mock_blob

    with patch(
        "kiarina.lib.google.cloud_storage._get_blob.get_bucket",
        return_value=mock_bucket,
    ):
        blob = get_blob(blob_name="custom-blob.txt")
        assert blob.name == "custom-blob.txt"

        # Verify blob was called with custom blob name
        mock_bucket.blob.assert_called_once_with("custom-blob.txt")


def test_get_blob_with_blob_name_prefix():
    # Setup settings with blob_name_prefix
    settings_manager.user_config = {
        "default": {
            "google_auth_config_key": "test_auth",
            "bucket_name": "test-bucket",
            "blob_name_prefix": "prefix",
            "blob_name": "test-blob.txt",
        }
    }

    # Mock get_bucket and blob
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_blob.name = "prefix/test-blob.txt"
    mock_bucket.blob.return_value = mock_blob

    with patch(
        "kiarina.lib.google.cloud_storage._get_blob.get_bucket",
        return_value=mock_bucket,
    ):
        blob = get_blob()
        assert blob.name == "prefix/test-blob.txt"

        # Verify blob was called with prefixed blob name
        mock_bucket.blob.assert_called_once_with("prefix/test-blob.txt")


def test_get_blob_with_blob_name_prefix_and_parameter():
    # Setup settings with blob_name_prefix
    settings_manager.user_config = {
        "default": {
            "google_auth_config_key": "test_auth",
            "bucket_name": "test-bucket",
            "blob_name_prefix": "prefix",
        }
    }

    # Mock get_bucket and blob
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_blob.name = "prefix/custom-blob.txt"
    mock_bucket.blob.return_value = mock_blob

    with patch(
        "kiarina.lib.google.cloud_storage._get_blob.get_bucket",
        return_value=mock_bucket,
    ):
        blob = get_blob(blob_name="custom-blob.txt")
        assert blob.name == "prefix/custom-blob.txt"

        # Verify blob was called with prefixed custom blob name
        mock_bucket.blob.assert_called_once_with("prefix/custom-blob.txt")


def test_get_blob_without_blob_name():
    # Setup settings without blob_name
    settings_manager.user_config = {
        "default": {
            "google_auth_config_key": "test_auth",
            "bucket_name": "test-bucket",
        }
    }

    with pytest.raises(
        ValueError, match="blob_name is not set in the settings and not provided"
    ):
        get_blob()


def test_get_blob_with_custom_config_key():
    # Setup settings with custom config key
    settings_manager.user_config = {
        "custom": {
            "google_auth_config_key": "custom_auth",
            "bucket_name": "custom-bucket",
            "blob_name": "custom-blob.txt",
        }
    }

    # Mock get_bucket and blob
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_blob.name = "custom-blob.txt"
    mock_bucket.blob.return_value = mock_blob

    with patch(
        "kiarina.lib.google.cloud_storage._get_blob.get_bucket",
        return_value=mock_bucket,
    ) as mock_get_bucket:
        blob = get_blob(config_key="custom")
        assert blob.name == "custom-blob.txt"

        # Verify get_bucket was called with custom config key
        mock_get_bucket.assert_called_once_with("custom")

from unittest.mock import MagicMock, patch

from kiarina.lib.google.cloud_storage import get_storage_client, settings_manager


def test_get_storage_client():
    # Setup settings
    settings_manager.user_config = {
        "default": {
            "google_auth_config_key": "test_auth",
        }
    }

    # Mock get_credentials and storage.Client
    mock_credentials = MagicMock()
    mock_credentials.project_id = "test-project"
    mock_client = MagicMock()
    mock_client.project = "test-project"

    with (
        patch(
            "kiarina.lib.google.cloud_storage._get_storage_client.get_credentials",
            return_value=mock_credentials,
        ),
        patch(
            "kiarina.lib.google.cloud_storage._get_storage_client.storage.Client",
            return_value=mock_client,
        ) as mock_client_class,
    ):
        client = get_storage_client()
        assert client.project == "test-project"

        # Verify Client was called with correct credentials
        mock_client_class.assert_called_once_with(credentials=mock_credentials)

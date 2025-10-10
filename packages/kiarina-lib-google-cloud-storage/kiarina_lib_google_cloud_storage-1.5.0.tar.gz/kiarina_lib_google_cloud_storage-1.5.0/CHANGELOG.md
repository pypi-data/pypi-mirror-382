# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.5.0] - 2025-10-10

### Added
- Initial release of kiarina-lib-google-cloud-storage
- Google Cloud Storage client library with configuration management using pydantic-settings-manager
- `GoogleCloudStorageSettings`: Pydantic settings model for Google Cloud Storage configuration
  - `google_auth_config_key`: Configuration key for kiarina-lib-google-auth integration
  - `bucket_name`: Google Cloud Storage bucket name
  - `blob_name_prefix`: Optional prefix for blob names (e.g., "uploads/2024")
  - `blob_name`: Optional default blob name
- `get_storage_client()`: Get authenticated Google Cloud Storage client
- `get_bucket()`: Get Google Cloud Storage bucket
- `get_blob()`: Get Google Cloud Storage blob with optional name override
- `settings_manager`: Global settings manager instance with multi-configuration support
- Type safety with full type hints and Pydantic validation
- Environment variable configuration support with `KIARINA_LIB_GOOGLE_CLOUD_STORAGE_` prefix
- Runtime configuration overrides via `cli_args`
- Multiple named configurations support (e.g., production, staging)
- Seamless integration with kiarina-lib-google-auth for authentication
- Blob name prefix support for organizing blobs in hierarchical structures

### Dependencies
- google-cloud-storage>=2.19.0
- kiarina-lib-google-auth>=1.4.0
- pydantic-settings>=2.10.1
- pydantic-settings-manager>=2.1.0

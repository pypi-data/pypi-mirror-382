# ADK Extra Services

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python Tests](https://github.com/edu010101/adk-extra-services/actions/workflows/ci.yml/badge.svg)](https://github.com/edu010101/adk-extra-services/actions/workflows/ci.yml)

> Extensions and additional services for the [Agent Development Kit (ADK)](https://github.com/google/adk-python)

ADK Extra Services provides production-ready implementations of common services needed for building robust AI agents with the Google ADK framework.

## 🚀 Installation

```bash
pip install adk-extra-services
```

## 🛠️ Development Setup

If you want to contribute to the project or modify the source code, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/edu010101/adk-extra-services.git
   cd adk-extra-services
   ```

2. Check out our [Contributing Guidelines](CONTRIBUTING.md) for detailed setup instructions and development workflow.


## 📖 Services

### 🔄 [Sessions](examples/sessions/README.md)

Persistent session storage implementations for ADK agents.

#### Available Services:
- **MongoDBSessionService**: Persistent session storage using MongoDB
  ```python
  from adk_extra_services.sessions import MongoSessionService

  mongo_service = MongoSessionService(
    mongo_url="mongodb://your_mongo_uri:your_mongo_port",
    db_name="adk_test"
  )
  ```

- **RedisSessionService**: High-performance session storage using Redis
  ```python
  from adk_extra_services.sessions import RedisSessionService

  redis_service = RedisSessionService(redis_url="redis://your_redis_uri:your_redis_port")
  ```

For complete usage examples and API documentation, see the [Sessions Guide](examples/sessions/README.md).

### 📦 [Artifacts](examples/artifacts/README.md)

Storage and management of agent artifacts.

#### Available Services:
- **S3ArtifactService**: Store and manage artifacts in AWS S3 or compatible storage (Compatible with MinIO, DigitalOcean Spaces, Wasabi, Backblaze B2, and others)

  ```python
  from adk_extra_services.artifacts import S3ArtifactService

  s3_artifact_service = S3ArtifactService(
    bucket_name="your_bucket_name",
    endpoint_url="https://{your-bucket-name}.s3.{region}.amazonaws.com",
  )
  
  ```

- **LocalFolderArtifactService**: Lightweight local-filesystem storage ideal for development & testing environments.

  ```python
  from adk_extra_services.artifacts import LocalFolderArtifactService

  artifact_service = LocalFolderArtifactService(base_path="./artifacts_storage")
  ```

- **AzureBlobArtifactService**: Store and manage artifacts in Azure Blob Storage

  ```python
  from adk_extra_services.artifacts import AzureBlobArtifactService
  from azure.core.credentials import AzureSasCredential

  azure_service = AzureBlobArtifactService(
      account_url="https://yourstorageaccount.blob.core.windows.net",
      container_name="your-container-name",
      credential=AzureSasCredential("your-sas-token"),
      ensure_container=True,
  )
  ```

For complete usage examples and API documentation, see the [Artifacts Guide](examples/artifacts/README.md).

## 🤝 Contributing

Contributions are welcome! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.


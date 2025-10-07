"""Storage service for retrieving MinIO and MLflow credentials.

Handles fetching of storage access credentials and configuration
for MLflow tracking and artifact storage.
"""

from __future__ import annotations

from typing import Dict, Optional

import requests

from .http import HTTPService

__all__ = ["StorageService"]


class StorageService:
    """Service for retrieving storage credentials and configuration.
    
    Handles fetching MinIO access credentials, MLflow tracking URIs,
    and other storage-related configuration needed for artifact
    storage and model tracking operations.
    """

    def __init__(self, backend_url: str, http: HTTPService) -> None:
        """Initialize storage service with backend URL and HTTP client.
        
        Configures the service to communicate with storage credential
        endpoints using the provided HTTP service for consistent request
        handling and debug output capabilities.
        """
        self.backend_url = backend_url.rstrip("/")
        self.http = http

    def get_minio_credentials(self, backend_jwt: str, catalog_id: str) -> Optional[Dict[str, str]]:
        """Fetch MinIO storage access credentials for the specified catalog.
        
        Retrieves S3-compatible storage credentials including access keys,
        endpoint URLs, bucket names, and MLflow tracking URIs needed for
        storing and accessing ML artifacts and model data.
        """
        print("\nGetting MinIO credentials...")
        url = f"{self.backend_url}/api/v1/minio/access"
        headers = {
            "Authorization": f"Bearer {backend_jwt}",
            "X-Catalog-ID": catalog_id,
        }

        try:
            response = self.http.request("GET", url, headers=headers)
        except requests.RequestException as exc:
            print(f"[ERROR] Request failed: {exc}")
            return None

        if response.status_code != 200:
            reason = getattr(response, "reason", "")
            print(f"[ERROR] MinIO credential fetch failed: {response.status_code} {reason}")
            try:
                print(f"[ERROR] MinIO Response: {response.json()}")
            except Exception:  # pragma: no cover - debug output only
                print(f"[ERROR] MinIO Response: {response.text}")
            return None

        try:
            payload = response.json()
        except ValueError:
            print("[ERROR] MinIO response is not valid JSON")
            return None

        return {
            "backend_jwt": backend_jwt,
            "aws_access_key_id": payload.get("access_key", ""),
            "aws_secret_access_key": payload.get("secret_key", ""),
            "endpoint_url": payload.get("endpoint_url", ""),
            "bucket": payload.get("bucket", ""),
            "mlflow_tracking_uri": payload.get("mlflow_tracking_uri", ""),
        }

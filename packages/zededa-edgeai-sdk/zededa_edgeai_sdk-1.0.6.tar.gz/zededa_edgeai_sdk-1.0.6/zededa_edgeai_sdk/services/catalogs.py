"""Catalog management service for user access and token scoping.

Provides functionality to discover available catalogs and obtain
catalog-specific authentication tokens.
"""

from __future__ import annotations

from typing import Dict, List, Optional

import requests

from .http import HTTPService

__all__ = ["CatalogService"]


class CatalogService:
    """Service for managing catalog discovery and authentication token scoping.
    
    Handles retrieving available catalogs for authenticated users and
    obtaining catalog-specific authentication tokens with appropriate
    permissions for accessing catalog resources.
    """

    def __init__(self, backend_url: str, http: HTTPService) -> None:
        """Initialize catalog service with backend URL and HTTP client.
        
        Sets up the service to communicate with the catalog management
        endpoints using the provided HTTP service for consistent
        request handling and debug logging.
        """
        self.backend_url = backend_url.rstrip("/")
        self.http = http

    def get_catalogs(self, backend_jwt: str) -> Dict[str, List[Dict]]:
        """Retrieve catalog information for the authenticated user.
        
        Queries the user-info endpoint to get catalog access information,
        returning both available_catalogs (what user has access to) and
        all_catalogs (complete list for selection UI) in a structured format.
        """
        url = f"{self.backend_url}/api/v1/user-info"
        headers = {"Authorization": f"Bearer {backend_jwt}"}
        try:
            response = self.http.request("GET", url, headers=headers)
        except requests.RequestException as exc:
            print(f"[ERROR] Unable to fetch catalogs: {exc}")
            return []

        if response.status_code != 200:
            print(f"[ERROR] Failed to fetch catalogs: {response.status_code} {response.text}")
            return []

        try:
            data = response.json() or {}
        except ValueError:
            return []

        if not isinstance(data, dict):
            return []

        # Process available_catalogs (what user has access to)
        available_catalogs_list = []
        available_catalogs = data.get("available_catalogs")
        if isinstance(available_catalogs, list):
            for catalog in available_catalogs:
                if isinstance(catalog, str):
                    available_catalogs_list.append({"catalog_id": catalog})

        # Process all_catalogs (complete list for selection UI)
        all_catalogs_list = []
        all_catalogs = data.get("all_catalogs")
        if isinstance(all_catalogs, list):
            for catalog in all_catalogs:
                if isinstance(catalog, str):
                    all_catalogs_list.append({"catalog_id": catalog})

        return {
            "available_catalogs": available_catalogs_list,
            "all_catalogs": all_catalogs_list
        }

    def get_catalog_scoped_token(self, backend_jwt: str, catalog_id: str) -> Optional[Dict]:
        """Request a catalog-specific authentication token.
        
        Exchanges a general authentication token for a catalog-scoped token
        with permissions limited to the specified catalog, enabling secure
        access to catalog-specific resources and operations.
        """
        url = f"{self.backend_url}/api/v1/auth/catalog-scoped-token"
        headers = {
            "Authorization": f"Bearer {backend_jwt}",
            "Content-Type": "application/json",
        }
        payload = {"catalog_id": catalog_id}
        try:
            response = self.http.request("POST", url, headers=headers, json=payload)
        except requests.RequestException as exc:
            print(f"[ERROR] Catalog scoped token request failed: {exc}")
            return None

        if response.status_code != 200:
            print(f"[ERROR] Catalog scoped token request failed: {response.status_code} {response.text}")
            return None

        try:
            return response.json()
        except ValueError:
            print("[ERROR] Catalog scoped token response is not valid JSON")
            return None


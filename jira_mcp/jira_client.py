"""
Jira Client Module

HTTP client for Jira Cloud REST API using Basic Auth.
"""

import base64
from typing import Any, Optional

import requests


class JiraClient:
    """HTTP client for Jira Cloud REST API."""

    def __init__(self, base_url: str, email: str, api_token: str) -> None:
        """
        Initialize the Jira client.

        Args:
            base_url: Jira instance URL (e.g., https://company.atlassian.net)
            email: User email for authentication
            api_token: Jira API token
        """
        self.base_url = base_url.rstrip("/")
        self.email = email
        self.api_token = api_token

        # Create Basic Auth header
        credentials = f"{email}:{api_token}"
        encoded = base64.b64encode(credentials.encode()).decode()
        self.auth_header = f"Basic {encoded}"

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        json_data: Optional[dict[str, Any]] = None,
    ) -> requests.Response:
        """
        Make an authenticated request to the Jira API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (e.g., /rest/api/3/myself)
            params: Optional query parameters
            json_data: Optional JSON body data

        Returns:
            requests.Response object
        """
        url = f"{self.base_url}{endpoint}"

        headers = {
            "Authorization": self.auth_header,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json_data,
        )

        return response

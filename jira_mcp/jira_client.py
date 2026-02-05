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

    def search_issues(
        self,
        jql: str,
        max_results: int = 50,
        fields: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """
        Search issues using JQL.

        Args:
            jql: JQL query string
            max_results: Max results to return (default 50, max 100)
            fields: Fields to return (default: key, summary, status, assignee, created, updated)

        Returns:
            {
                'total': int,
                'issues': [
                    {
                        'key': str,
                        'summary': str,
                        'status': str,
                        'assignee': str (optional),
                        'created': str,
                        'updated': str
                    }
                ]
            }
        """
        if fields is None:
            fields = ["key", "summary", "status", "assignee", "created", "updated"]

        # Cap max_results at 100
        if max_results > 100:
            max_results = 100

        params = {
            "jql": jql,
            "maxResults": max_results,
            "fields": ",".join(fields),
        }

        response = self._request("GET", "/rest/api/3/search/jql", params=params)

        if response.status_code == 400:
            error_data = response.json()
            raise ValueError(f"Invalid JQL: {error_data.get('errorMessages', [])}")

        response.raise_for_status()

        data = response.json()

        # Transform to cleaner format
        issues = []
        for issue in data.get("issues", []):
            fields_data = issue.get("fields", {})
            transformed = {
                "key": issue.get("key"),
                "summary": fields_data.get("summary"),
                "status": fields_data.get("status", {}).get("name") if fields_data.get("status") else None,
                "created": fields_data.get("created"),
                "updated": fields_data.get("updated"),
            }
            # Add assignee if present
            assignee = fields_data.get("assignee")
            if assignee:
                transformed["assignee"] = assignee.get("displayName")

            issues.append(transformed)

        # New API uses pagination tokens instead of total count
        # Return count of returned issues as total when total not available
        return {
            "total": data.get("total", len(issues)),
            "issues": issues,
        }

    def get_issue(self, issue_key: str) -> dict[str, Any]:
        """
        Get full issue details.

        Args:
            issue_key: Issue key like "IT-123"

        Returns:
            {
                'key': str,
                'summary': str,
                'description': str,
                'status': {'name': str, 'id': str},
                'issue_type': str,
                'priority': str,
                'assignee': str (optional),
                'reporter': str,
                'created': str,
                'updated': str,
                'resolution': str (optional),
                'labels': list[str],
                'components': list[str]
            }
        """
        response = self._request("GET", f"/rest/api/3/issue/{issue_key}")

        if response.status_code == 404:
            raise ValueError(f"Issue not found: {issue_key}")

        response.raise_for_status()

        data = response.json()
        fields = data.get("fields", {})

        # Transform to cleaner format
        result = {
            "key": data.get("key"),
            "summary": fields.get("summary"),
            "description": self._extract_description(fields.get("description")),
            "status": {
                "name": fields.get("status", {}).get("name"),
                "id": fields.get("status", {}).get("id"),
            } if fields.get("status") else None,
            "issue_type": fields.get("issuetype", {}).get("name") if fields.get("issuetype") else None,
            "priority": fields.get("priority", {}).get("name") if fields.get("priority") else None,
            "created": fields.get("created"),
            "updated": fields.get("updated"),
            "labels": fields.get("labels", []),
            "components": [c.get("name") for c in fields.get("components", [])],
        }

        # Add optional fields
        assignee = fields.get("assignee")
        if assignee:
            result["assignee"] = assignee.get("displayName")

        reporter = fields.get("reporter")
        if reporter:
            result["reporter"] = reporter.get("displayName")

        resolution = fields.get("resolution")
        if resolution:
            result["resolution"] = resolution.get("name")

        return result

    def _extract_description(self, description: Any) -> Optional[str]:
        """
        Extract plain text from Jira's ADF (Atlassian Document Format) description.

        Args:
            description: ADF document or None

        Returns:
            Plain text string or None
        """
        if description is None:
            return None

        # ADF is a JSON structure - extract text from paragraph nodes
        if isinstance(description, dict) and description.get("type") == "doc":
            texts = []
            for content in description.get("content", []):
                if content.get("type") == "paragraph":
                    for item in content.get("content", []):
                        if item.get("type") == "text":
                            texts.append(item.get("text", ""))
            return "\n".join(texts) if texts else None

        # Fallback for unexpected format
        return str(description) if description else None

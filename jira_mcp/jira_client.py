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

    def _to_adf(self, text: str) -> dict[str, Any]:
        """
        Convert plain text to Atlassian Document Format (ADF).

        Args:
            text: Plain text string

        Returns:
            ADF document dict
        """
        paragraphs = []
        for line in text.split("\n"):
            if line:
                paragraphs.append({
                    "type": "paragraph",
                    "content": [{"type": "text", "text": line}]
                })
            else:
                # Empty line becomes empty paragraph
                paragraphs.append({"type": "paragraph", "content": []})

        return {
            "type": "doc",
            "version": 1,
            "content": paragraphs if paragraphs else [{"type": "paragraph", "content": []}]
        }

    def create_issue(
        self,
        project: str,
        issue_type: str,
        summary: str,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        assignee: Optional[str] = None,
        labels: Optional[list[str]] = None,
        components: Optional[list[str]] = None,
        parent_key: Optional[str] = None,
        epic_link: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Create a new issue.

        Args:
            project: Project key (e.g., "ITPROJ")
            issue_type: Issue type name ("Epic", "Task", "Sub-task", etc.)
            summary: Issue summary (required)
            description: Issue description (plain text, converted to ADF)
            priority: Priority name ("High", "Medium", "Low")
            assignee: Assignee email or account ID
            labels: List of label names
            components: List of component names
            parent_key: Parent issue key (for subtasks)
            epic_link: Epic issue key (for tasks under an epic)

        Returns:
            {'key': 'ITPROJ-123', 'url': 'https://...'}
        """
        fields: dict[str, Any] = {
            "project": {"key": project},
            "issuetype": {"name": issue_type},
            "summary": summary,
        }

        # Description is required by ITPROJ - default to summary if not provided
        if description:
            fields["description"] = self._to_adf(description)
        else:
            fields["description"] = self._to_adf(summary)

        # Priority defaults to Medium
        if priority:
            fields["priority"] = {"name": priority}
        else:
            fields["priority"] = {"name": "Medium"}

        if assignee:
            # Try email format first
            fields["assignee"] = {"id": assignee} if "@" not in assignee else {"emailAddress": assignee}

        if labels:
            fields["labels"] = labels

        if components:
            fields["components"] = [{"name": c} for c in components]

        # Parent for subtasks
        if parent_key:
            fields["parent"] = {"key": parent_key}

        # Epic link for tasks (customfield_10014)
        if epic_link:
            fields["customfield_10014"] = epic_link

        payload = {"fields": fields}

        response = self._request("POST", "/rest/api/3/issue", json_data=payload)

        if response.status_code == 400:
            error_data = response.json()
            errors = error_data.get("errors", {})
            error_messages = error_data.get("errorMessages", [])
            raise ValueError(f"Create failed: {errors} {error_messages}")

        if response.status_code == 404:
            raise ValueError(f"Project or issue type not found: {project}/{issue_type}")

        response.raise_for_status()

        data = response.json()
        issue_key = data.get("key")

        return {
            "key": issue_key,
            "url": f"{self.base_url}/browse/{issue_key}",
        }

    def update_issue(
        self,
        issue_key: str,
        fields: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Update issue fields.

        Args:
            issue_key: Issue key (e.g., "ITPROJ-123")
            fields: Fields to update. Supported:
                - summary: str
                - description: str (plain text, converted to ADF)
                - priority: str (e.g., "High")
                - assignee: str (email or account ID)
                - labels: list[str] (replaces existing)
                - components: list[str] (replaces existing)

        Returns:
            {'key': 'ITPROJ-123', 'updated': '2026-02-04T...'}
        """
        update_fields: dict[str, Any] = {}

        if "summary" in fields:
            update_fields["summary"] = fields["summary"]

        if "description" in fields:
            update_fields["description"] = self._to_adf(fields["description"])

        if "priority" in fields:
            update_fields["priority"] = {"name": fields["priority"]}

        if "assignee" in fields:
            assignee = fields["assignee"]
            update_fields["assignee"] = {"id": assignee} if "@" not in assignee else {"emailAddress": assignee}

        if "labels" in fields:
            update_fields["labels"] = fields["labels"]

        if "components" in fields:
            update_fields["components"] = [{"name": c} for c in fields["components"]]

        payload = {"fields": update_fields}

        response = self._request("PUT", f"/rest/api/3/issue/{issue_key}", json_data=payload)

        if response.status_code == 404:
            raise ValueError(f"Issue not found: {issue_key}")

        if response.status_code == 400:
            error_data = response.json()
            raise ValueError(f"Update failed: {error_data}")

        response.raise_for_status()

        # PUT returns 204 No Content on success - get updated timestamp
        issue = self.get_issue(issue_key)

        return {
            "key": issue_key,
            "updated": issue.get("updated"),
        }

    def add_comment(
        self,
        issue_key: str,
        body: str,
        visibility: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """
        Add a comment to an issue.

        Args:
            issue_key: Issue key (e.g., "ITPROJ-123")
            body: Comment text (plain text, converted to ADF)
            visibility: Optional visibility restriction
                {'type': 'role', 'value': 'Administrators'}

        Returns:
            {'comment_id': '12345', 'created': '2026-02-04T...'}
        """
        payload: dict[str, Any] = {
            "body": self._to_adf(body)
        }

        if visibility:
            payload["visibility"] = visibility

        response = self._request("POST", f"/rest/api/3/issue/{issue_key}/comment", json_data=payload)

        if response.status_code == 404:
            raise ValueError(f"Issue not found: {issue_key}")

        if response.status_code == 400:
            error_data = response.json()
            raise ValueError(f"Comment failed: {error_data}")

        response.raise_for_status()

        data = response.json()

        return {
            "comment_id": data.get("id"),
            "created": data.get("created"),
        }

    def get_transitions(self, issue_key: str) -> list[dict[str, Any]]:
        """
        Get available transitions for an issue.

        Args:
            issue_key: Issue key (e.g., "ITPROJ-45")

        Returns:
            [
                {'id': '2', 'name': 'To Do'},
                {'id': '3', 'name': 'In Progress'},
                ...
            ]
        """
        response = self._request("GET", f"/rest/api/3/issue/{issue_key}/transitions")

        if response.status_code == 404:
            raise ValueError(f"Issue not found: {issue_key}")

        response.raise_for_status()

        data = response.json()
        transitions = data.get("transitions", [])

        return [
            {"id": t["id"], "name": t["name"]}
            for t in transitions
        ]

    def transition_issue(
        self,
        issue_key: str,
        transition_name: str,
    ) -> dict[str, Any]:
        """
        Transition issue through workflow.

        Args:
            issue_key: Issue key (e.g., "ITPROJ-45")
            transition_name: Transition name (case-insensitive), e.g., "In Progress", "Done"

        Returns:
            {
                'key': 'ITPROJ-45',
                'new_status': 'In Progress',
                'transitioned': '2026-02-04T...'
            }

        Raises:
            ValueError: If transition not available (lists valid transitions)
        """
        # Get available transitions
        transitions = self.get_transitions(issue_key)

        if not transitions:
            raise ValueError(f"No transitions available for {issue_key}")

        # Find matching transition (case-insensitive)
        transition_lower = transition_name.lower()
        matches = [t for t in transitions if t["name"].lower() == transition_lower]

        if not matches:
            available = ", ".join(t["name"] for t in transitions)
            raise ValueError(
                f"Transition '{transition_name}' not available for {issue_key}. "
                f"Available: {available}"
            )

        if len(matches) > 1:
            match_names = ", ".join(t["name"] for t in matches)
            raise ValueError(
                f"Multiple transitions match '{transition_name}': {match_names}"
            )

        transition = matches[0]

        # Execute transition
        payload = {"transition": {"id": transition["id"]}}
        response = self._request(
            "POST",
            f"/rest/api/3/issue/{issue_key}/transitions",
            json_data=payload,
        )

        if response.status_code == 400:
            error_data = response.json()
            raise ValueError(f"Transition failed: {error_data}")

        response.raise_for_status()

        # Get updated issue to confirm new status
        issue = self.get_issue(issue_key)

        return {
            "key": issue_key,
            "new_status": issue["status"]["name"],
            "transitioned": issue["updated"],
        }

    def delete_issue(self, issue_key: str) -> dict[str, Any]:
        """
        Delete an issue permanently.

        WARNING: Cannot be undone. Use with caution.
        For cleanup/testing. Consider transition to Done for normal workflow.

        Note: Subtasks must be deleted before parents.

        Args:
            issue_key: Issue key (e.g., "ITPROJ-123")

        Returns:
            {'key': 'ITPROJ-123', 'deleted': True, 'deleted_at': '2026-02-04T...'}
        """
        from datetime import datetime, timezone

        response = self._request("DELETE", f"/rest/api/3/issue/{issue_key}")

        if response.status_code == 404:
            raise ValueError(f"Issue not found: {issue_key}")

        if response.status_code == 400:
            error_data = response.json()
            raise ValueError(f"Delete failed: {error_data}")

        response.raise_for_status()

        return {
            "key": issue_key,
            "deleted": True,
            "deleted_at": datetime.now(timezone.utc).isoformat(),
        }

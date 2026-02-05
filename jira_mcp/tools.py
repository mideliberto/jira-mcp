"""
Jira MCP Tools

Tool functions for MCP server integration.
"""

import os
from typing import Any, Optional

from jira_mcp.auth.credential_manager import get_credential_manager
from jira_mcp.jira_client import JiraClient


def _get_client() -> JiraClient:
    """Get an authenticated JiraClient instance."""
    manager = get_credential_manager()
    credentials = manager.get_credentials()

    if not credentials:
        raise RuntimeError(
            "No Jira credentials found. Run: python scripts/setup_credentials.py"
        )

    return JiraClient(
        base_url=credentials["base_url"],
        email=credentials["email"],
        api_token=credentials["api_token"],
    )


def search_issues_tool(
    jql: str,
    max_results: int = 50,
    fields: Optional[list[str]] = None,
) -> dict[str, Any]:
    """
    Search Jira issues using JQL.

    Args:
        jql: JQL query string (e.g., "project = IT AND status = Open")
        max_results: Maximum number of results to return (default 50, max 100)
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
    client = _get_client()
    return client.search_issues(jql=jql, max_results=max_results, fields=fields)


def get_issue_tool(issue_key: str) -> dict[str, Any]:
    """
    Get full details for a specific Jira issue.

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
    client = _get_client()
    return client.get_issue(issue_key=issue_key)


def create_issue_tool(
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
    Create a new Jira issue.

    Args:
        project: Project key (e.g., "ITPROJ", "ITHELP")
        issue_type: Issue type ("Epic", "Task", "Sub-task", "[System] Service request", etc.)
        summary: Issue summary (required)
        description: Issue description (optional, plain text)
        priority: Priority ("High", "Medium", "Low") - defaults to "Medium"
        assignee: Assignee email or account ID
        labels: List of label names
        components: List of component names
        parent_key: Parent issue key (required for subtasks)
        epic_link: Epic issue key (for tasks under an epic)

    Returns:
        {'key': 'ITPROJ-123', 'url': 'https://...'}
    """
    client = _get_client()
    return client.create_issue(
        project=project,
        issue_type=issue_type,
        summary=summary,
        description=description,
        priority=priority,
        assignee=assignee,
        labels=labels,
        components=components,
        parent_key=parent_key,
        epic_link=epic_link,
    )


def update_issue_tool(
    issue_key: str,
    fields: dict[str, Any],
) -> dict[str, Any]:
    """
    Update fields on an existing Jira issue.

    Args:
        issue_key: Issue key (e.g., "ITPROJ-123")
        fields: Fields to update. Supported:
            - summary: str
            - description: str (plain text)
            - priority: str ("High", "Medium", "Low")
            - assignee: str (email or account ID)
            - labels: list[str] (replaces existing labels)
            - components: list[str] (replaces existing components)

    Returns:
        {'key': 'ITPROJ-123', 'updated': '2026-02-04T...'}
    """
    client = _get_client()
    return client.update_issue(issue_key=issue_key, fields=fields)


def add_comment_tool(
    issue_key: str,
    body: str,
    visibility: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    """
    Add a comment to a Jira issue.

    Args:
        issue_key: Issue key (e.g., "ITPROJ-123")
        body: Comment text (plain text)
        visibility: Optional visibility restriction
            {'type': 'role', 'value': 'Administrators'}

    Returns:
        {'comment_id': '12345', 'created': '2026-02-04T...'}
    """
    client = _get_client()
    return client.add_comment(issue_key=issue_key, body=body, visibility=visibility)

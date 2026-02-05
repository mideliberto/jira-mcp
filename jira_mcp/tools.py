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

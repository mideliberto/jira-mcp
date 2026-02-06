#!/usr/bin/env python3
"""
Jira MCP Server

MCP server for Jira Cloud integration, enabling Claude to manage work items.

Exposes 10 tools:
- search_issues: Search with JQL
- get_issue: Get full issue details
- create_issue: Create epic/task/subtask
- update_issue: Update issue fields
- add_comment: Add comments to issues
- transition_issue: Move through workflow states
- get_transitions: Discover available transitions
- delete_issue: Permanently delete (with confirmation)
- search_users: Find users by name/email for account IDs
- attach_file: Upload file attachments to issues
"""

import os
import sys
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from jira_mcp.jira_client import JiraClient

# Create FastMCP application
mcp = FastMCP(
    name=os.getenv("MCP_SERVER_NAME", "Jira MCP"),
)

# Lazy singleton client
_client: JiraClient | None = None


def _get_client() -> JiraClient:
    """Get authenticated JiraClient instance (cached singleton)."""
    global _client
    if _client is None:
        from jira_mcp.auth.credential_manager import get_credential_manager

        manager = get_credential_manager()
        credentials = manager.get_credentials()

        if not credentials:
            raise RuntimeError(
                "No Jira credentials found. Run: python scripts/setup_credentials.py"
            )

        _client = JiraClient(
            base_url=credentials["base_url"],
            email=credentials["email"],
            api_token=credentials["api_token"],
        )
    return _client


@mcp.tool()
def search_issues(
    jql: str,
    max_results: int = 50,
    fields: Optional[list[str]] = None,
) -> dict[str, Any]:
    """
    Search Jira issues using JQL (Jira Query Language).

    Args:
        jql: JQL query string. Examples:
            - "project = ITHELP AND status = Open"
            - "assignee = currentUser() AND resolution = Unresolved"
            - "text ~ 'email migration'"
            - "created >= -7d"
        max_results: Maximum results to return (default 50, max 100)
        fields: Fields to return (default: key, summary, status, assignee, created, updated)

    Returns:
        Dictionary with:
        - total: Number of matching issues
        - issues: List of issue summaries with key, summary, status, assignee, created, updated
    """
    client = _get_client()
    return client.search_issues(jql=jql, max_results=max_results, fields=fields)


@mcp.tool()
def get_issue(issue_key: str) -> dict[str, Any]:
    """
    Get full details for a specific Jira issue.

    Args:
        issue_key: Issue key like "ITHELP-123" or "ITPROJ-45"

    Returns:
        Dictionary with:
        - key: Issue key
        - summary: Issue title
        - description: Full description text
        - status: Current status (name and id)
        - issue_type: Type (Epic, Task, Sub-task, etc.)
        - priority: Priority level
        - assignee: Assigned user (if any)
        - reporter: User who created the issue
        - created/updated: Timestamps
        - labels: List of labels
        - components: List of components
        - resolution: Resolution status (if resolved)
    """
    client = _get_client()
    return client.get_issue(issue_key=issue_key)


@mcp.tool()
def create_issue(
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
    work_type: Optional[str] = None,
    risk_level: Optional[str] = None,
    approvers: Optional[list[dict[str, Any]]] = None,
    affected_systems: Optional[list[str]] = None,
    implementation_window_start: Optional[str] = None,
    implementation_window_end: Optional[str] = None,
    rollback_plan: Optional[str] = None,
    custom_fields: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    Create a new Jira issue.

    Supports creating epics, tasks, and subtasks with proper hierarchy:
    - Epic: Use issue_type="Epic" in ITPROJ
    - Task under Epic: Use issue_type="Task" with epic_link="ITPROJ-XX"
    - Subtask: Use issue_type="Sub-task" with parent_key="ITPROJ-XX"

    Args:
        project: Project key (e.g., "ITPROJ", "ITHELP", "ITCM")
        issue_type: Issue type name:
            - ITPROJ: "Epic", "Task", "Sub-task"
            - ITHELP: "[System] Service request", "Question", etc.
            - ITCM: "Standard Change", "Normal Change", "Emergency Change"
        summary: Issue title (required)
        description: Issue description (plain text, will be formatted)
        priority: Priority level ("High", "Medium", "Low") - defaults to "Medium"
        assignee: Assignee email or account ID
        labels: List of label names
        components: List of component names
        parent_key: Parent issue key (required for Sub-task)
        epic_link: Epic issue key (for linking Task to Epic)
        work_type: ITHELP/ITCM Work Type (Hardware, Software, Access, Network, Security, Maintenance, Other)
        risk_level: ITCM Risk Level (Low, Medium, High)
        approvers: ITCM Approvers list [{"accountId": "..."}]
        affected_systems: ITCM Affected Systems list
        implementation_window_start: ITCM Implementation Window Start (ISO datetime)
        implementation_window_end: ITCM Implementation Window End (ISO datetime)
        rollback_plan: ITCM Rollback Plan (plain text)
        custom_fields: Raw custom field values (escape hatch for unmapped fields)

    Returns:
        Dictionary with:
        - key: Created issue key (e.g., "ITPROJ-123")
        - url: Direct link to the issue
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
        work_type=work_type,
        risk_level=risk_level,
        approvers=approvers,
        affected_systems=affected_systems,
        implementation_window_start=implementation_window_start,
        implementation_window_end=implementation_window_end,
        rollback_plan=rollback_plan,
        custom_fields=custom_fields,
    )


@mcp.tool()
def update_issue(
    issue_key: str,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    assignee: Optional[str] = None,
    labels: Optional[list[str]] = None,
    components: Optional[list[str]] = None,
    work_type: Optional[str] = None,
    risk_level: Optional[str] = None,
    approvers: Optional[list[dict[str, Any]]] = None,
    affected_systems: Optional[list[str]] = None,
    implementation_window_start: Optional[str] = None,
    implementation_window_end: Optional[str] = None,
    rollback_plan: Optional[str] = None,
    custom_fields: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    Update fields on an existing Jira issue.

    Only provided fields will be updated. Arrays (labels, components) replace existing values.

    Args:
        issue_key: Issue key (e.g., "ITPROJ-123")
        summary: New summary/title
        description: New description (plain text)
        priority: New priority ("High", "Medium", "Low")
        assignee: New assignee (email or account ID)
        labels: New labels (replaces existing)
        components: New components (replaces existing)
        work_type: ITHELP/ITCM Work Type (Hardware, Software, Access, Network, Security, Maintenance, Other)
        risk_level: ITCM Risk Level (Low, Medium, High)
        approvers: ITCM Approvers list [{"accountId": "..."}]
        affected_systems: ITCM Affected Systems list
        implementation_window_start: ITCM Implementation Window Start (ISO datetime)
        implementation_window_end: ITCM Implementation Window End (ISO datetime)
        rollback_plan: ITCM Rollback Plan (plain text)
        custom_fields: Raw custom field values (escape hatch for unmapped fields)

    Returns:
        Dictionary with:
        - key: Issue key
        - updated: Timestamp of update
    """
    # Build fields dict from provided arguments
    fields: dict[str, Any] = {}
    if summary is not None:
        fields["summary"] = summary
    if description is not None:
        fields["description"] = description
    if priority is not None:
        fields["priority"] = priority
    if assignee is not None:
        fields["assignee"] = assignee
    if labels is not None:
        fields["labels"] = labels
    if components is not None:
        fields["components"] = components
    if work_type is not None:
        fields["work_type"] = work_type
    if risk_level is not None:
        fields["risk_level"] = risk_level
    if approvers is not None:
        fields["approvers"] = approvers
    if affected_systems is not None:
        fields["affected_systems"] = affected_systems
    if implementation_window_start is not None:
        fields["implementation_window_start"] = implementation_window_start
    if implementation_window_end is not None:
        fields["implementation_window_end"] = implementation_window_end
    if rollback_plan is not None:
        fields["rollback_plan"] = rollback_plan

    if not fields and not custom_fields:
        raise ValueError("At least one field must be provided to update")

    client = _get_client()
    return client.update_issue(issue_key=issue_key, fields=fields, custom_fields=custom_fields)


@mcp.tool()
def add_comment(
    issue_key: str,
    body: str,
) -> dict[str, Any]:
    """
    Add a comment to a Jira issue.

    Args:
        issue_key: Issue key (e.g., "ITPROJ-123")
        body: Comment text (plain text, will be formatted)

    Returns:
        Dictionary with:
        - comment_id: ID of created comment
        - created: Timestamp of creation
    """
    client = _get_client()
    return client.add_comment(issue_key=issue_key, body=body)


@mcp.tool()
def transition_issue(
    issue_key: str,
    transition_name: str,
) -> dict[str, Any]:
    """
    Transition a Jira issue through its workflow.

    ITPROJ workflow: Backlog → To Do → In Progress → In Review → Done

    Args:
        issue_key: Issue key (e.g., "ITPROJ-123")
        transition_name: Target transition name (case-insensitive). Examples:
            - "To Do"
            - "In Progress"
            - "In Review"
            - "Done"

    Returns:
        Dictionary with:
        - key: Issue key
        - new_status: New status after transition
        - transitioned: Timestamp of transition

    Raises:
        ValueError: If transition not available (error includes valid transitions)
    """
    client = _get_client()
    return client.transition_issue(issue_key=issue_key, transition_name=transition_name)


@mcp.tool()
def get_transitions(issue_key: str) -> list[dict[str, Any]]:
    """
    Get available transitions for an issue.

    Use this to see what workflow transitions are available from the current status.

    Args:
        issue_key: Issue key (e.g., "ITPROJ-123")

    Returns:
        List of available transitions, each with:
        - id: Transition ID
        - name: Transition name (e.g., "In Progress", "Done")
    """
    client = _get_client()
    return client.get_transitions(issue_key=issue_key)


@mcp.tool()
def delete_issue(
    issue_key: str,
    confirm_delete: bool = False,
) -> dict[str, Any]:
    """
    ⚠️ PERMANENTLY delete a Jira issue. Cannot be undone.

    For normal workflow, use transition_issue to move to "Done" instead.
    This is for cleanup and testing only.

    Note: Subtasks must be deleted before their parent tasks.

    Args:
        issue_key: Issue key (e.g., "ITPROJ-123")
        confirm_delete: Must be True to proceed (safety check to prevent accidents)

    Returns:
        Dictionary with:
        - key: Deleted issue key
        - deleted: True
        - deleted_at: Timestamp of deletion

    Raises:
        ValueError: If confirm_delete is not True
    """
    if not confirm_delete:
        raise ValueError(
            f"delete_issue requires confirm_delete=True. "
            f"This will permanently delete {issue_key} and cannot be undone. "
            f"Consider transition_issue to 'Done' instead."
        )

    client = _get_client()
    return client.delete_issue(issue_key=issue_key)


@mcp.tool()
def search_users(
    query: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """
    Search for Jira users by name or email to get their account IDs.

    Use this to find account IDs for user fields like approvers, assignee, etc.

    Args:
        query: Name or email to search for. Examples:
            - Full name: "Shari Clark"
            - Email: "sclark@pwphealth.com"
            - Partial: "Clark" (returns all matches)
        max_results: Maximum results to return (default 10)

    Returns:
        Dictionary with:
        - users: List of matching users with accountId, displayName, emailAddress, active
        - count: Number of results

    Example:
        result = search_users("Shari Clark")
        account_id = result['users'][0]['accountId']
        # Use in create_issue: approvers=[{'accountId': account_id}]
    """
    client = _get_client()
    users = client.search_users(query=query, max_results=max_results)

    return {
        "users": users,
        "count": len(users),
    }


@mcp.tool()
def attach_file(
    issue_key: str,
    file_path: str,
    filename: Optional[str] = None,
) -> dict[str, Any]:
    """
    Attach a file to a Jira issue.

    Args:
        issue_key: Issue key (e.g., "ITPROJ-123")
        file_path: Path to file to upload. Supports:
            - Absolute paths: "/Users/mike/report.pdf"
            - Home directory: "~/Documents/report.pdf"
            - Relative paths: "./report.pdf"
        filename: Override filename in Jira (default: basename of file_path)

    Returns:
        Dictionary with:
        - key: Issue key
        - filename: Filename as stored in Jira
        - id: Attachment ID
        - size: File size in bytes

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If issue not found or upload fails
    """
    from pathlib import Path

    # Expand ~ and resolve path
    resolved_path = Path(file_path).expanduser().resolve()

    client = _get_client()
    return client.attach_file(
        issue_key=issue_key,
        file_path=str(resolved_path),
        filename=filename,
    )


def main() -> None:
    """Run the Jira MCP server."""
    try:
        # Verify credentials exist before starting
        from jira_mcp.auth.credential_manager import get_credential_manager
        manager = get_credential_manager()
        if not manager.credentials_exist():
            print("Error: No Jira credentials found.", file=sys.stderr)
            print("Run: python scripts/setup_credentials.py", file=sys.stderr)
            sys.exit(1)

        # Run the MCP server
        mcp.run()
    except Exception as e:
        print(f"Error starting Jira MCP server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

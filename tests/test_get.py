"""Tests for get_issue functionality."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

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


def test_get_issue():
    """Test getting a specific issue."""
    client = _get_client()

    # First, find an issue to get
    results = client.search_issues(jql="project = ITHELP", max_results=1)

    if not results["issues"]:
        print("No issues found in IT project, skipping test")
        return

    issue_key = results["issues"][0]["key"]
    print(f"Getting issue: {issue_key}")

    issue = client.get_issue(issue_key)

    # Verify required fields
    assert issue["key"] == issue_key
    assert "summary" in issue
    assert "status" in issue
    assert "issue_type" in issue
    assert "created" in issue
    assert "updated" in issue

    print(f"  Key: {issue['key']}")
    print(f"  Summary: {issue['summary']}")
    print(f"  Status: {issue['status']['name']}")
    print(f"  Type: {issue['issue_type']}")
    print(f"  Priority: {issue.get('priority', 'None')}")
    print(f"  Assignee: {issue.get('assignee', 'Unassigned')}")
    print(f"  Reporter: {issue.get('reporter', 'Unknown')}")
    print(f"  Labels: {issue.get('labels', [])}")
    print(f"  Components: {issue.get('components', [])}")

    if issue.get("description"):
        desc_preview = issue["description"][:100] + "..." if len(issue["description"]) > 100 else issue["description"]
        print(f"  Description: {desc_preview}")


def test_get_nonexistent_issue():
    """Test getting a non-existent issue returns error."""
    client = _get_client()
    try:
        client.get_issue("NONEXISTENT-99999")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "not found" in str(e).lower()
        print(f"Correctly raised error: {e}")


if __name__ == "__main__":
    print("Running get tests...")
    print()
    print("Test 1: Get existing issue")
    test_get_issue()
    print()
    print("Test 2: Get non-existent issue")
    test_get_nonexistent_issue()
    print()
    print("All get tests passed!")

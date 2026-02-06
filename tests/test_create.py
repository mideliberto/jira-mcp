"""Tests for create_issue functionality."""

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


def test_create_task():
    """Test creating a simple task."""
    client = _get_client()
    result = client.create_issue(
        project="ITPROJ",
        issue_type="Task",
        summary="TEST - Create task test - DELETE ME",
        description="Automated test - please delete",
    )

    assert "key" in result
    assert result["key"].startswith("ITPROJ-")
    assert "url" in result
    print(f"Created task: {result['key']}")
    print(f"URL: {result['url']}")

    # Verify it exists
    issue = client.get_issue(result["key"])
    assert issue["summary"] == "TEST - Create task test - DELETE ME"
    print(f"Verified: {issue['summary']}")

    return result["key"]


def test_create_with_priority():
    """Test creating an issue with priority."""
    client = _get_client()
    result = client.create_issue(
        project="ITPROJ",
        issue_type="Task",
        summary="TEST - High priority task - DELETE ME",
        priority="High",
    )

    issue = client.get_issue(result["key"])
    assert issue["priority"] == "High"
    print(f"Created high priority task: {result['key']}")

    return result["key"]


if __name__ == "__main__":
    print("Running create tests...")
    print()
    print("Test 1: Create simple task")
    key1 = test_create_task()
    print()
    print("Test 2: Create with priority")
    key2 = test_create_with_priority()
    print()
    print("All create tests passed!")
    print(f"Created issues: {key1}, {key2}")
    print("Please delete these test issues in Jira.")

"""Tests for update_issue functionality."""

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


def test_update_summary():
    """Test updating issue summary."""
    client = _get_client()

    # Create test issue
    result = client.create_issue(
        project="ITPROJ",
        issue_type="Task",
        summary="TEST - Update test - DELETE ME",
    )
    key = result["key"]
    print(f"Created: {key}")

    # Update summary
    update_result = client.update_issue(
        issue_key=key,
        fields={"summary": "TEST - Update test - UPDATED - DELETE ME"}
    )

    assert update_result["key"] == key
    assert "updated" in update_result
    print(f"Updated at: {update_result['updated']}")

    # Verify
    issue = client.get_issue(key)
    assert "UPDATED" in issue["summary"]
    print(f"Verified: {issue['summary']}")

    return key


def test_update_description():
    """Test updating issue description."""
    client = _get_client()

    # Create test issue
    result = client.create_issue(
        project="ITPROJ",
        issue_type="Task",
        summary="TEST - Description update test - DELETE ME",
    )
    key = result["key"]

    # Update description
    client.update_issue(
        issue_key=key,
        fields={"description": "Updated description via API test"}
    )

    # Verify
    issue = client.get_issue(key)
    assert "Updated description" in issue["description"]
    print(f"Description updated for: {key}")

    return key


if __name__ == "__main__":
    print("Running update tests...")
    print()
    print("Test 1: Update summary")
    key1 = test_update_summary()
    print()
    print("Test 2: Update description")
    key2 = test_update_description()
    print()
    print("All update tests passed!")
    print(f"Created issues: {key1}, {key2}")
    print("Please delete these test issues in Jira.")

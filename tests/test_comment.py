"""Tests for add_comment functionality."""

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


def test_add_comment():
    """Test adding a comment to an issue."""
    client = _get_client()

    # Create test issue
    result = client.create_issue(
        project="ITPROJ",
        issue_type="Task",
        summary="TEST - Comment test - DELETE ME",
    )
    key = result["key"]
    print(f"Created: {key}")

    # Add comment
    comment_result = client.add_comment(
        issue_key=key,
        body="Test comment from jira-mcp automated test"
    )

    assert "comment_id" in comment_result
    assert "created" in comment_result
    print(f"Comment ID: {comment_result['comment_id']}")
    print(f"Created: {comment_result['created']}")

    return key


def test_multiline_comment():
    """Test adding a multiline comment."""
    client = _get_client()

    # Create test issue
    result = client.create_issue(
        project="ITPROJ",
        issue_type="Task",
        summary="TEST - Multiline comment test - DELETE ME",
    )
    key = result["key"]

    # Add multiline comment
    comment_result = client.add_comment(
        issue_key=key,
        body="Line 1\nLine 2\nLine 3"
    )

    assert comment_result["comment_id"]
    print(f"Multiline comment added to: {key}")

    return key


if __name__ == "__main__":
    print("Running comment tests...")
    print()
    print("Test 1: Add simple comment")
    key1 = test_add_comment()
    print()
    print("Test 2: Add multiline comment")
    key2 = test_multiline_comment()
    print()
    print("All comment tests passed!")
    print(f"Created issues: {key1}, {key2}")
    print("Please delete these test issues in Jira.")

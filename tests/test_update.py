"""Tests for update_issue functionality."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from jira_mcp.tools import create_issue_tool, update_issue_tool, get_issue_tool


def test_update_summary():
    """Test updating issue summary."""
    # Create test issue
    result = create_issue_tool(
        project="ITPROJ",
        issue_type="Task",
        summary="TEST - Update test - DELETE ME",
    )
    key = result["key"]
    print(f"Created: {key}")

    # Update summary
    update_result = update_issue_tool(
        issue_key=key,
        fields={"summary": "TEST - Update test - UPDATED - DELETE ME"}
    )

    assert update_result["key"] == key
    assert "updated" in update_result
    print(f"Updated at: {update_result['updated']}")

    # Verify
    issue = get_issue_tool(key)
    assert "UPDATED" in issue["summary"]
    print(f"Verified: {issue['summary']}")

    return key


def test_update_description():
    """Test updating issue description."""
    # Create test issue
    result = create_issue_tool(
        project="ITPROJ",
        issue_type="Task",
        summary="TEST - Description update test - DELETE ME",
    )
    key = result["key"]

    # Update description
    update_issue_tool(
        issue_key=key,
        fields={"description": "Updated description via API test"}
    )

    # Verify
    issue = get_issue_tool(key)
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

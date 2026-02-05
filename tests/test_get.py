"""Tests for get_issue functionality."""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from jira_mcp.tools import search_issues_tool, get_issue_tool


def test_get_issue():
    """Test getting a specific issue."""
    # First, find an issue to get
    results = search_issues_tool(jql="project = ITHELP", max_results=1)

    if not results["issues"]:
        print("No issues found in IT project, skipping test")
        return

    issue_key = results["issues"][0]["key"]
    print(f"Getting issue: {issue_key}")

    issue = get_issue_tool(issue_key)

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
    try:
        get_issue_tool("NONEXISTENT-99999")
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

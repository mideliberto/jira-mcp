"""Tests for search_issues functionality."""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from jira_mcp.tools import search_issues_tool


def test_search_open_issues():
    """Test searching for open issues in IT project."""
    results = search_issues_tool(
        jql="project = ITHELP AND status = Open",
        max_results=5,
    )

    assert "total" in results
    assert "issues" in results
    assert isinstance(results["issues"], list)

    print(f"Found {results['total']} total issues, returned {len(results['issues'])}")

    for issue in results["issues"]:
        assert "key" in issue
        assert "summary" in issue
        assert "status" in issue
        print(f"  {issue['key']}: {issue['summary']} [{issue['status']}]")


def test_search_with_custom_fields():
    """Test searching with custom field selection."""
    results = search_issues_tool(
        jql="project = ITHELP",
        max_results=3,
        fields=["key", "summary", "status", "priority"],
    )

    assert len(results["issues"]) <= 3
    print(f"Returned {len(results['issues'])} issues with custom fields")


if __name__ == "__main__":
    print("Running search tests...")
    print()
    print("Test 1: Search open issues")
    test_search_open_issues()
    print()
    print("Test 2: Search with custom fields")
    test_search_with_custom_fields()
    print()
    print("All search tests passed!")

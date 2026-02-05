#!/usr/bin/env python3
"""
Phase 2 Integration Test

Tests search and get functionality against actual Jira.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from jira_mcp.tools import search_issues_tool, get_issue_tool


def main():
    """Run Phase 2 integration tests."""
    print("Phase 2 Integration Test")
    print("=" * 40)
    print()

    # Test 1: Search for open issues
    print("Test 1: Search for open issues in IT project")
    print("-" * 40)
    try:
        results = search_issues_tool(
            jql="project = ITHELP AND status = Open",
            max_results=5,
        )
        print(f"Found {results['total']} issues, showing {len(results['issues'])}")
        for issue in results["issues"]:
            assignee = issue.get("assignee", "Unassigned")
            print(f"  {issue['key']}: {issue['summary']} [{issue['status']}] - {assignee}")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    print()

    # Test 2: Get specific issue
    print("Test 2: Get specific issue details")
    print("-" * 40)
    if results["issues"]:
        key = results["issues"][0]["key"]
        try:
            issue = get_issue_tool(key)
            print(f"Issue {key}: {issue['summary']}")
            print(f"  Type: {issue['issue_type']}")
            print(f"  Status: {issue['status']['name']}")
            print(f"  Priority: {issue.get('priority', 'None')}")
            print(f"  Assignee: {issue.get('assignee', 'Unassigned')}")
            print(f"  Reporter: {issue.get('reporter', 'Unknown')}")
            if issue.get("description"):
                desc = issue["description"][:80] + "..." if len(issue["description"]) > 80 else issue["description"]
                print(f"  Description: {desc}")
        except Exception as e:
            print(f"ERROR: {e}")
            sys.exit(1)
    else:
        print("No issues found to test get_issue")

    print()
    print("=" * 40)
    print("Phase 2 tests passed!")


if __name__ == "__main__":
    main()

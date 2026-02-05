#!/usr/bin/env python3
"""
Integration test: Complete project creation workflow.

Creates:
- Epic
- Task under epic
- Subtask under task

Performs:
- Search for created issues
- Update task description
- Add comments
- Transition through workflow
- Cleanup
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from jira_mcp.tools import (
    search_issues_tool,
    get_issue_tool,
    create_issue_tool,
    update_issue_tool,
    add_comment_tool,
    transition_issue_tool,
    get_transitions_tool,
)
from jira_mcp.auth.credential_manager import get_credential_manager
from jira_mcp.jira_client import JiraClient


def cleanup_issues(keys: list[str]) -> None:
    """Delete test issues (subtasks first)."""
    manager = get_credential_manager()
    creds = manager.get_credentials()
    client = JiraClient(creds["base_url"], creds["email"], creds["api_token"])

    for key in reversed(keys):  # Delete children first
        try:
            response = client._request("DELETE", f"/rest/api/3/issue/{key}")
            if response.status_code == 204:
                print(f"  Deleted {key}")
            else:
                print(f"  Failed to delete {key}: {response.status_code}")
        except Exception as e:
            print(f"  Error deleting {key}: {e}")


def test_full_workflow():
    """Run complete workflow integration test."""
    print("=" * 60)
    print("INTEGRATION TEST: Full Project Workflow")
    print("=" * 60)
    print()

    created_keys = []

    try:
        # 1. Create Epic
        print("1. CREATE EPIC")
        print("-" * 40)
        epic = create_issue_tool(
            project="ITPROJ",
            issue_type="Epic",
            summary="INTEGRATION TEST - Email Migration Project",
            description="Test epic for integration testing. DELETE ME.",
            labels=["integration-test"],
        )
        created_keys.append(epic["key"])
        print(f"   Created Epic: {epic['key']}")
        print(f"   URL: {epic['url']}")
        print()

        # 2. Create Task under Epic
        print("2. CREATE TASK UNDER EPIC")
        print("-" * 40)
        task = create_issue_tool(
            project="ITPROJ",
            issue_type="Task",
            summary="Phase 1: Planning",
            description="Planning phase for the migration project.",
            epic_link=epic["key"],
            priority="High",
        )
        created_keys.append(task["key"])
        print(f"   Created Task: {task['key']} (linked to {epic['key']})")
        print()

        # 3. Create Subtask under Task
        print("3. CREATE SUBTASK UNDER TASK")
        print("-" * 40)
        subtask = create_issue_tool(
            project="ITPROJ",
            issue_type="Sub-task",
            summary="Document current mailbox sizes",
            description="Inventory all mailboxes and their sizes.",
            parent_key=task["key"],
        )
        created_keys.append(subtask["key"])
        print(f"   Created Subtask: {subtask['key']} (parent: {task['key']})")
        print()

        # 4. Search for created issues
        print("4. SEARCH FOR CREATED ISSUES")
        print("-" * 40)
        results = search_issues_tool(
            jql=f"project = ITPROJ AND labels = integration-test",
            max_results=10,
        )
        print(f"   Found {results['total']} issues with integration-test label")
        for issue in results["issues"]:
            print(f"   - {issue['key']}: {issue['summary']}")
        print()

        # 5. Get issue details
        print("5. GET ISSUE DETAILS")
        print("-" * 40)
        details = get_issue_tool(task["key"])
        print(f"   Key: {details['key']}")
        print(f"   Summary: {details['summary']}")
        print(f"   Type: {details['issue_type']}")
        print(f"   Priority: {details['priority']}")
        print(f"   Status: {details['status']['name']}")
        print()

        # 6. Update task
        print("6. UPDATE TASK")
        print("-" * 40)
        update_result = update_issue_tool(
            issue_key=task["key"],
            fields={
                "description": "Updated description via integration test.",
                "priority": "Medium",
            },
        )
        print(f"   Updated {task['key']} at {update_result['updated']}")
        print()

        # 7. Add comment
        print("7. ADD COMMENT")
        print("-" * 40)
        comment = add_comment_tool(
            issue_key=task["key"],
            body="Integration test comment.\n\nThis verifies the comment API works.",
        )
        print(f"   Added comment {comment['comment_id']} at {comment['created']}")
        print()

        # 8. Transition through workflow
        print("8. TRANSITION THROUGH WORKFLOW")
        print("-" * 40)

        # Check available transitions
        transitions = get_transitions_tool(task["key"])
        print(f"   Available transitions: {[t['name'] for t in transitions]}")

        # Walk through workflow
        workflow = ["To Do", "In Progress", "In Review", "Done"]
        for target in workflow:
            transitions = get_transitions_tool(task["key"])
            if any(t["name"] == target for t in transitions):
                result = transition_issue_tool(task["key"], target)
                print(f"   → {result['new_status']}")
            else:
                print(f"   (skipping {target})")
        print()

        # 9. Verify final state
        print("9. VERIFY FINAL STATE")
        print("-" * 40)
        final = get_issue_tool(task["key"])
        print(f"   Final status: {final['status']['name']}")
        assert final["status"]["name"] == "Done", f"Expected Done, got {final['status']['name']}"
        print("   ✓ Status verified as Done")
        print()

        print("=" * 60)
        print("INTEGRATION TEST PASSED!")
        print("=" * 60)

    except Exception as e:
        print(f"\nERROR: {e}")
        print()
        print("Test failed. Created issues:")
        for key in created_keys:
            print(f"  - {key}")
        raise

    finally:
        # Cleanup
        print()
        print("CLEANUP")
        print("-" * 40)
        if created_keys:
            cleanup_issues(created_keys)
        print()


if __name__ == "__main__":
    test_full_workflow()

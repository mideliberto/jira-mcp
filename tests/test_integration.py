#!/usr/bin/env python3
"""
Integration tests for jira-mcp.

Consolidated test suite covering all JiraClient functionality.
Creates test issues and cleans them up automatically.

Run with: python tests/test_integration.py
"""

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


def cleanup_issues(client: JiraClient, keys: list[str]) -> None:
    """Delete test issues (subtasks first)."""
    for key in reversed(keys):  # Delete children first
        try:
            response = client._request("DELETE", f"/rest/api/3/issue/{key}")
            if response.status_code == 204:
                print(f"  Deleted {key}")
            else:
                print(f"  Failed to delete {key}: {response.status_code}")
        except Exception as e:
            print(f"  Error deleting {key}: {e}")


# =============================================================================
# READ-ONLY TESTS (no cleanup needed)
# =============================================================================

def test_search_open_issues(client: JiraClient) -> None:
    """Test searching for open issues."""
    print("  Searching for open issues in ITHELP...")
    results = client.search_issues(
        jql="project = ITHELP AND status = Open",
        max_results=5,
    )
    assert "total" in results
    assert "issues" in results
    assert isinstance(results["issues"], list)
    print(f"  Found {results['total']} total, returned {len(results['issues'])}")


def test_search_with_custom_fields(client: JiraClient) -> None:
    """Test searching with custom field selection."""
    print("  Searching with custom fields...")
    results = client.search_issues(
        jql="project = ITHELP",
        max_results=3,
        fields=["key", "summary", "status", "priority"],
    )
    assert len(results["issues"]) <= 3
    print(f"  Returned {len(results['issues'])} issues")


def test_get_nonexistent_issue(client: JiraClient) -> None:
    """Test getting a non-existent issue returns error."""
    print("  Getting non-existent issue...")
    try:
        client.get_issue("NONEXISTENT-99999")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "not found" in str(e).lower()
        print(f"  Correctly raised: {e}")


def test_invalid_transition(client: JiraClient, issue_key: str) -> None:
    """Test that invalid transition produces helpful error."""
    print("  Testing invalid transition error...")
    try:
        client.transition_issue(issue_key, "Nonexistent State")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "not available" in str(e).lower()
        assert "Available:" in str(e)
        print(f"  Correctly raised error with available transitions")


# =============================================================================
# MUTATING TESTS (with cleanup)
# =============================================================================

def test_full_workflow(client: JiraClient, created_keys: list[str]) -> None:
    """Test complete workflow: hierarchy, search, get, update, comment, transition."""

    # 1. Create Epic
    print("  Creating Epic...")
    epic = client.create_issue(
        project="ITPROJ",
        issue_type="Epic",
        summary="INTEGRATION TEST - Email Migration Project",
        description="Test epic for integration testing.",
        labels=["integration-test"],
    )
    created_keys.append(epic["key"])
    print(f"    Created: {epic['key']}")

    # 2. Create Task under Epic with priority
    print("  Creating Task under Epic (High priority)...")
    task = client.create_issue(
        project="ITPROJ",
        issue_type="Task",
        summary="Phase 1: Planning",
        description="Planning phase for the migration project.",
        epic_link=epic["key"],
        priority="High",
    )
    created_keys.append(task["key"])
    print(f"    Created: {task['key']} linked to {epic['key']}")

    # Verify priority was set
    task_details = client.get_issue(task["key"])
    assert task_details["priority"] == "High", f"Expected High priority, got {task_details['priority']}"
    print(f"    Verified priority: {task_details['priority']}")

    # 3. Create Subtask under Task
    print("  Creating Subtask...")
    subtask = client.create_issue(
        project="ITPROJ",
        issue_type="Sub-task",
        summary="Document current mailbox sizes",
        description="Inventory all mailboxes and their sizes.",
        parent_key=task["key"],
    )
    created_keys.append(subtask["key"])
    print(f"    Created: {subtask['key']} parent: {task['key']}")

    # 4. Search for created issues
    print("  Searching for created issues...")
    results = client.search_issues(
        jql="project = ITPROJ AND labels = integration-test",
        max_results=10,
    )
    assert results["total"] >= 1
    print(f"    Found {results['total']} with integration-test label")

    # 5. Get issue details
    print("  Getting issue details...")
    details = client.get_issue(task["key"])
    assert details["key"] == task["key"]
    assert "summary" in details
    assert "status" in details
    assert "issue_type" in details
    print(f"    Key: {details['key']}, Type: {details['issue_type']}, Status: {details['status']['name']}")

    # 6. Update task
    print("  Updating task...")
    update_result = client.update_issue(
        issue_key=task["key"],
        fields={
            "summary": "Phase 1: Planning - UPDATED",
            "description": "Updated description via integration test.",
        },
    )
    assert update_result["key"] == task["key"]
    assert "updated" in update_result
    # Verify update
    updated = client.get_issue(task["key"])
    assert "UPDATED" in updated["summary"]
    print(f"    Updated: {updated['summary']}")

    # 7. Add comment (simple)
    print("  Adding simple comment...")
    comment = client.add_comment(
        issue_key=task["key"],
        body="Integration test comment.",
    )
    assert "comment_id" in comment
    assert "created" in comment
    print(f"    Comment ID: {comment['comment_id']}")

    # 8. Add multiline comment
    print("  Adding multiline comment...")
    comment2 = client.add_comment(
        issue_key=task["key"],
        body="Line 1\nLine 2\nLine 3",
    )
    assert comment2["comment_id"]
    print(f"    Multiline comment ID: {comment2['comment_id']}")

    # 9. Get transitions
    print("  Getting transitions...")
    transitions = client.get_transitions(task["key"])
    assert len(transitions) > 0
    assert all("id" in t and "name" in t for t in transitions)
    print(f"    Available: {[t['name'] for t in transitions]}")

    # 10. Test invalid transition error
    test_invalid_transition(client, task["key"])

    # 11. Transition through workflow (case-insensitive)
    print("  Transitioning through workflow...")
    workflow = ["TO DO", "In Progress", "IN REVIEW", "done"]  # Mixed case to test case insensitivity
    for target in workflow:
        transitions = client.get_transitions(task["key"])
        # Find matching transition (case-insensitive)
        if any(t["name"].lower() == target.lower() for t in transitions):
            result = client.transition_issue(task["key"], target)
            print(f"    -> {result['new_status']}")
        else:
            print(f"    (skipping {target})")

    # 12. Verify final state
    print("  Verifying final state...")
    final = client.get_issue(task["key"])
    assert final["status"]["name"] == "Done", f"Expected Done, got {final['status']['name']}"
    print(f"    Final status: {final['status']['name']} ✓")


def run_tests() -> None:
    """Run all integration tests."""
    print("=" * 60)
    print("JIRA-MCP INTEGRATION TESTS")
    print("=" * 60)
    print()

    client = _get_client()
    created_keys: list[str] = []

    try:
        # Read-only tests
        print("1. READ-ONLY TESTS")
        print("-" * 40)
        test_search_open_issues(client)
        test_search_with_custom_fields(client)
        test_get_nonexistent_issue(client)
        print()

        # Full workflow test (creates issues)
        print("2. FULL WORKFLOW TEST")
        print("-" * 40)
        test_full_workflow(client, created_keys)
        print()

        print("=" * 60)
        print("ALL TESTS PASSED!")
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
            cleanup_issues(client, created_keys)
        else:
            print("  No issues to clean up")
        print()


if __name__ == "__main__":
    run_tests()

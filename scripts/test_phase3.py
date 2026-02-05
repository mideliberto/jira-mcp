#!/usr/bin/env python3
"""
Phase 3 Integration Test

Tests full workflow: Epic → Task → Subtask with updates and comments.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from jira_mcp.tools import (
    create_issue_tool,
    update_issue_tool,
    add_comment_tool,
    get_issue_tool,
)


def main():
    """Run Phase 3 integration tests."""
    print("Phase 3 Integration Test")
    print("=" * 50)
    print()

    created_issues = []

    try:
        # 1. Create Epic
        print("Step 1: Create Epic")
        print("-" * 50)
        epic = create_issue_tool(
            project="ITPROJ",
            issue_type="Epic",
            summary="TEST EPIC - Phase 3 Verification - DELETE ME",
            description="Automated test epic - please delete after verification",
        )
        created_issues.append(epic["key"])
        print(f"Created Epic: {epic['key']}")
        print(f"URL: {epic['url']}")
        print()

        # 2. Create Task under Epic
        print("Step 2: Create Task under Epic")
        print("-" * 50)
        task = create_issue_tool(
            project="ITPROJ",
            issue_type="Task",
            summary="TEST Task under Epic - DELETE ME",
            description="Task linked to epic via epic_link field",
            epic_link=epic["key"],
        )
        created_issues.append(task["key"])
        print(f"Created Task: {task['key']} (linked to {epic['key']})")
        print(f"URL: {task['url']}")
        print()

        # 3. Create Subtask under Task
        print("Step 3: Create Subtask under Task")
        print("-" * 50)
        subtask = create_issue_tool(
            project="ITPROJ",
            issue_type="Sub-task",
            summary="TEST Subtask - DELETE ME",
            description="Subtask linked to parent task",
            parent_key=task["key"],
        )
        created_issues.append(subtask["key"])
        print(f"Created Subtask: {subtask['key']} (parent: {task['key']})")
        print(f"URL: {subtask['url']}")
        print()

        # 4. Update Task
        print("Step 4: Update Task")
        print("-" * 50)
        update_result = update_issue_tool(
            issue_key=task["key"],
            fields={
                "description": "Updated via jira-mcp API test",
                "priority": "High",
            }
        )
        print(f"Updated {task['key']} at {update_result['updated']}")

        # Verify update
        updated_task = get_issue_tool(task["key"])
        print(f"Verified priority: {updated_task['priority']}")
        print()

        # 5. Add Comment
        print("Step 5: Add Comment")
        print("-" * 50)
        comment = add_comment_tool(
            issue_key=task["key"],
            body="Test comment from jira-mcp Phase 3 integration test\n\nThis verifies the comment API works correctly.",
        )
        print(f"Added comment {comment['comment_id']} at {comment['created']}")
        print()

        # Summary
        print("=" * 50)
        print("Phase 3 Integration Test PASSED!")
        print()
        print("Created hierarchy:")
        print(f"  Epic: {epic['key']}")
        print(f"    └─ Task: {task['key']} (priority: High)")
        print(f"         └─ Subtask: {subtask['key']}")
        print()
        print("Verify in Jira, then delete these test issues:")
        for key in created_issues:
            print(f"  - {key}")

    except Exception as e:
        print(f"ERROR: {e}")
        print()
        print("Created issues before failure:")
        for key in created_issues:
            print(f"  - {key}")
        sys.exit(1)


if __name__ == "__main__":
    main()

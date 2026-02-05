#!/usr/bin/env python3
"""
Phase 4 Integration Test

Tests workflow transitions.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from jira_mcp.tools import (
    create_issue_tool,
    get_transitions_tool,
    transition_issue_tool,
    get_issue_tool,
)


def main():
    """Run Phase 4 integration tests."""
    print("Phase 4 Integration Test - Transitions")
    print("=" * 50)
    print()

    # Create test issue
    print("Step 1: Create test issue")
    print("-" * 50)
    issue = create_issue_tool(
        project="ITPROJ",
        issue_type="Task",
        summary="TEST - Phase 4 Transitions - DELETE ME",
        description="Testing workflow transitions",
    )
    key = issue["key"]
    print(f"Created: {key}")
    print()

    try:
        # Show initial status
        initial = get_issue_tool(key)
        print(f"Initial status: {initial['status']['name']}")
        print()

        # Show available transitions
        print("Step 2: Get available transitions")
        print("-" * 50)
        transitions = get_transitions_tool(key)
        print(f"Available: {[t['name'] for t in transitions]}")
        print()

        # Walk through the workflow
        print("Step 3: Walk through workflow")
        print("-" * 50)

        # ITPROJ workflow: Backlog → To Do → In Progress → In Review → Done
        workflow_path = ["To Do", "In Progress", "In Review", "Done"]

        for target_status in workflow_path:
            transitions = get_transitions_tool(key)
            available_names = [t["name"] for t in transitions]

            if target_status in available_names:
                result = transition_issue_tool(key, target_status)
                print(f"  → {result['new_status']}")
            else:
                print(f"  (skipping {target_status} - not available)")
                print(f"    Available: {available_names}")

        print()

        # Final status
        final = get_issue_tool(key)
        print(f"Final status: {final['status']['name']}")
        print()

        # Test error handling
        print("Step 4: Test invalid transition error")
        print("-" * 50)
        try:
            transition_issue_tool(key, "Nonexistent Status")
        except ValueError as e:
            print(f"Expected error: {e}")
        print()

        print("=" * 50)
        print("Phase 4 Integration Test PASSED!")
        print()
        print(f"Test issue: {key}")
        print("Please delete this issue after verification.")

    except Exception as e:
        print(f"ERROR: {e}")
        print(f"Test issue to clean up: {key}")
        sys.exit(1)


if __name__ == "__main__":
    main()

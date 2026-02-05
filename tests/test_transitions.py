"""Tests for transition functionality."""

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


def test_get_transitions():
    """Test getting available transitions."""
    # Create test issue
    issue = create_issue_tool(
        project="ITPROJ",
        issue_type="Task",
        summary="TEST - Get transitions test - DELETE ME",
    )
    key = issue["key"]
    print(f"Created: {key}")

    # Get transitions
    transitions = get_transitions_tool(key)
    assert len(transitions) > 0
    assert all("id" in t and "name" in t for t in transitions)

    print(f"Available transitions: {[t['name'] for t in transitions]}")
    return key


def test_transition_issue():
    """Test transitioning an issue."""
    # Create test issue
    issue = create_issue_tool(
        project="ITPROJ",
        issue_type="Task",
        summary="TEST - Transition test - DELETE ME",
    )
    key = issue["key"]
    print(f"Created: {key}")

    # Check initial status
    initial = get_issue_tool(key)
    print(f"Initial status: {initial['status']['name']}")

    # Get available transitions and pick first one
    transitions = get_transitions_tool(key)
    if transitions:
        target = transitions[0]["name"]
        result = transition_issue_tool(key, target)
        assert result["key"] == key
        print(f"Transitioned to: {result['new_status']}")

    return key


def test_invalid_transition():
    """Test that invalid transition produces helpful error."""
    # Create test issue
    issue = create_issue_tool(
        project="ITPROJ",
        issue_type="Task",
        summary="TEST - Invalid transition test - DELETE ME",
    )
    key = issue["key"]

    try:
        transition_issue_tool(key, "Nonexistent State")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "not available" in str(e).lower()
        assert "Available:" in str(e)
        print(f"Expected error: {e}")

    return key


def test_case_insensitive():
    """Test case-insensitive transition matching."""
    issue = create_issue_tool(
        project="ITPROJ",
        issue_type="Task",
        summary="TEST - Case insensitive test - DELETE ME",
    )
    key = issue["key"]

    transitions = get_transitions_tool(key)
    if transitions:
        # Try with different case
        target = transitions[0]["name"]
        result = transition_issue_tool(key, target.upper())
        print(f"Case-insensitive transition worked: {result['new_status']}")

    return key


if __name__ == "__main__":
    print("Running transition tests...")
    print()

    created = []

    print("Test 1: Get transitions")
    created.append(test_get_transitions())
    print()

    print("Test 2: Transition issue")
    created.append(test_transition_issue())
    print()

    print("Test 3: Invalid transition error")
    created.append(test_invalid_transition())
    print()

    print("Test 4: Case-insensitive matching")
    created.append(test_case_insensitive())
    print()

    print("All transition tests passed!")
    print(f"Created issues: {', '.join(created)}")
    print("Please delete these test issues.")

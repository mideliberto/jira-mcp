"""Tests for transition functionality."""

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


def test_get_transitions():
    """Test getting available transitions."""
    client = _get_client()

    # Create test issue
    issue = client.create_issue(
        project="ITPROJ",
        issue_type="Task",
        summary="TEST - Get transitions test - DELETE ME",
    )
    key = issue["key"]
    print(f"Created: {key}")

    # Get transitions
    transitions = client.get_transitions(key)
    assert len(transitions) > 0
    assert all("id" in t and "name" in t for t in transitions)

    print(f"Available transitions: {[t['name'] for t in transitions]}")
    return key


def test_transition_issue():
    """Test transitioning an issue."""
    client = _get_client()

    # Create test issue
    issue = client.create_issue(
        project="ITPROJ",
        issue_type="Task",
        summary="TEST - Transition test - DELETE ME",
    )
    key = issue["key"]
    print(f"Created: {key}")

    # Check initial status
    initial = client.get_issue(key)
    print(f"Initial status: {initial['status']['name']}")

    # Get available transitions and pick first one
    transitions = client.get_transitions(key)
    if transitions:
        target = transitions[0]["name"]
        result = client.transition_issue(key, target)
        assert result["key"] == key
        print(f"Transitioned to: {result['new_status']}")

    return key


def test_invalid_transition():
    """Test that invalid transition produces helpful error."""
    client = _get_client()

    # Create test issue
    issue = client.create_issue(
        project="ITPROJ",
        issue_type="Task",
        summary="TEST - Invalid transition test - DELETE ME",
    )
    key = issue["key"]

    try:
        client.transition_issue(key, "Nonexistent State")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "not available" in str(e).lower()
        assert "Available:" in str(e)
        print(f"Expected error: {e}")

    return key


def test_case_insensitive():
    """Test case-insensitive transition matching."""
    client = _get_client()

    issue = client.create_issue(
        project="ITPROJ",
        issue_type="Task",
        summary="TEST - Case insensitive test - DELETE ME",
    )
    key = issue["key"]

    transitions = client.get_transitions(key)
    if transitions:
        # Try with different case
        target = transitions[0]["name"]
        result = client.transition_issue(key, target.upper())
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

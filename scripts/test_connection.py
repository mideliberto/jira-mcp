#!/usr/bin/env python3
"""
Test script for Jira connection.

Loads credentials and tests connection with GET /myself endpoint.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from jira_mcp.auth.credential_manager import get_credential_manager
from jira_mcp.jira_client import JiraClient


def main() -> None:
    """Test Jira connection."""
    # Load credentials
    manager = get_credential_manager()
    credentials = manager.get_credentials()

    if not credentials:
        print("Error: No credentials found. Run setup_credentials.py first.")
        sys.exit(1)

    # Create client
    client = JiraClient(
        base_url=credentials["base_url"],
        email=credentials["email"],
        api_token=credentials["api_token"],
    )

    # Test connection
    response = client._request("GET", "/rest/api/3/myself")

    if response.status_code != 200:
        print(f"Error: API returned {response.status_code}")
        print(response.text)
        sys.exit(1)

    user_data = response.json()

    print(f"Connected as: {user_data.get('displayName', 'Unknown')}")
    print(f"Email: {credentials['email']}")
    print(f"Base URL: {credentials['base_url']}")


if __name__ == "__main__":
    main()

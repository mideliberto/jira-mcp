#!/usr/bin/env python3
"""
Setup script for Jira credentials.

Prompts for credentials and stores them encrypted.
"""

import os
import sys
from getpass import getpass
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from jira_mcp.auth.credential_manager import CredentialManager


def main() -> None:
    """Run credential setup."""
    print("Jira MCP Credential Setup")
    print("=" * 40)
    print()

    # Check for encryption key
    if not os.environ.get("JIRA_ENCRYPTION_KEY"):
        print("Error: JIRA_ENCRYPTION_KEY environment variable not set.")
        print()
        print("Generate one with:")
        print('  python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"')
        print()
        print("Then set it:")
        print("  export JIRA_ENCRYPTION_KEY='your-generated-key'")
        sys.exit(1)

    # Prompt for credentials
    email = input("Email [mdeliberto@pwphealth.com]: ").strip()
    if not email:
        email = "mdeliberto@pwphealth.com"

    api_token = getpass("API Token: ").strip()
    if not api_token:
        print("Error: API token is required")
        sys.exit(1)

    base_url = input("Base URL [https://pwphealth.atlassian.net]: ").strip()
    if not base_url:
        base_url = "https://pwphealth.atlassian.net"

    # Store credentials
    manager = CredentialManager()
    manager.store_credentials(base_url=base_url, email=email, api_token=api_token)

    print()
    print(f"Credentials encrypted and saved to {manager.credentials_path}")


if __name__ == "__main__":
    main()

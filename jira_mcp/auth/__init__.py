"""Authentication module for Jira MCP."""

from jira_mcp.auth.credential_manager import CredentialManager, get_credential_manager

__all__ = ["CredentialManager", "get_credential_manager"]

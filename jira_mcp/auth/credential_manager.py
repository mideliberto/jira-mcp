"""
Credential Manager Module

Securely stores and manages Jira API credentials.
Encrypts the API token while keeping email and base_url in plaintext.
"""

import base64
import json
import os
from pathlib import Path
from typing import Optional, TypedDict

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class JiraCredentials(TypedDict):
    """Jira credential structure."""

    base_url: str
    email: str
    api_token: str


# Singleton instance
_instance: Optional["CredentialManager"] = None


def get_credential_manager() -> "CredentialManager":
    """Get the singleton CredentialManager instance."""
    global _instance
    if _instance is None:
        _instance = CredentialManager()
    return _instance


class CredentialManager:
    """Securely stores and manages Jira API credentials."""

    def __init__(self) -> None:
        """Initialize the CredentialManager."""
        # Project root is parent of jira_mcp package
        self.project_root = Path(__file__).parent.parent.parent
        self.salt_path = self.project_root / "encryption_salt"
        self.credentials_path = self.project_root / "config" / "credentials.json"

        self.encryption_key = self._get_encryption_key()
        self.fernet = Fernet(self.encryption_key)

    def _get_salt(self) -> bytes:
        """
        Get the encryption salt from the salt file.

        Raises:
            FileNotFoundError: If the salt file doesn't exist.

        Returns:
            bytes: The salt for key derivation.
        """
        if not self.salt_path.exists():
            raise FileNotFoundError(
                f"Encryption salt not found at {self.salt_path}. "
                "Copy from google-mcp: cp ~/dev/google-mcp/encryption_salt ~/dev/jira-mcp/"
            )

        with open(self.salt_path, "rb") as f:
            return f.read()

    def _get_encryption_key(self) -> bytes:
        """
        Get the encryption key from environment and derive using PBKDF2.

        Raises:
            ValueError: If JIRA_ENCRYPTION_KEY is not set.

        Returns:
            bytes: The derived encryption key.
        """
        key = os.environ.get("JIRA_ENCRYPTION_KEY", "")

        if not key:
            raise ValueError(
                "JIRA_ENCRYPTION_KEY environment variable is required. "
                "Generate one with: python3 -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
            )

        salt = self._get_salt()

        # Derive a proper 32-byte key using PBKDF2 with the salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(key.encode()))

    def _encrypt(self, plaintext: str) -> str:
        """Encrypt a string value."""
        return self.fernet.encrypt(plaintext.encode()).decode()

    def _decrypt(self, ciphertext: str) -> str:
        """Decrypt a string value."""
        return self.fernet.decrypt(ciphertext.encode()).decode()

    def store_credentials(
        self, base_url: str, email: str, api_token: str
    ) -> None:
        """
        Store Jira credentials securely.

        Args:
            base_url: Jira instance URL (e.g., https://company.atlassian.net)
            email: User email for authentication
            api_token: Jira API token (will be encrypted)
        """
        # Encrypt only the API token
        encrypted_token = self._encrypt(api_token)

        credentials_data = {
            "base_url": base_url,
            "email": email,
            "api_token_encrypted": encrypted_token,
        }

        # Ensure config directory exists
        self.credentials_path.parent.mkdir(parents=True, exist_ok=True)

        # Write credentials with restrictive permissions
        with open(self.credentials_path, "w") as f:
            json.dump(credentials_data, f, indent=2)
        self.credentials_path.chmod(0o600)

    def get_credentials(self) -> Optional[JiraCredentials]:
        """
        Get stored Jira credentials.

        Returns:
            JiraCredentials dict or None if not found.
        """
        if not self.credentials_path.exists():
            return None

        with open(self.credentials_path, "r") as f:
            data = json.load(f)

        # Decrypt the API token
        api_token = self._decrypt(data["api_token_encrypted"])

        return JiraCredentials(
            base_url=data["base_url"],
            email=data["email"],
            api_token=api_token,
        )

    def credentials_exist(self) -> bool:
        """Check if credentials file exists."""
        return self.credentials_path.exists()

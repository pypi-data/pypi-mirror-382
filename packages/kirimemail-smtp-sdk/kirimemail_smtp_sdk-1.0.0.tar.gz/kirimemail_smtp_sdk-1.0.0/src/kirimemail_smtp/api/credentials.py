"""
Credentials API for SMTP credential management.
"""

from typing import Any, Optional

from ..client.smtp_client import SmtpClient


class CredentialsApi:
    """
    API class for SMTP credential management.
    """

    def __init__(self, client: SmtpClient) -> None:
        """
        Initialize the Credentials API.

        Args:
            client: SMTP client instance
        """
        self.client = client

    async def list_credentials(
        self,
        domain: str,
        limit: Optional[int] = None,
        page: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        List credentials for a domain.

        Args:
            domain: Domain name
            limit: Number of credentials per page
            page: Page number

        Returns:
            List of credentials with pagination
        """
        params = {}
        if limit is not None:
            params["limit"] = limit
        if page is not None:
            params["page"] = page

        return await self.client.get(f"/api/domains/{domain}/credentials", params=params)

    async def create_credential(
        self,
        domain: str,
        username: str,
    ) -> dict[str, Any]:
        """
        Create a new SMTP credential.

        Args:
            domain: Domain name
            username: Username for the credential

        Returns:
            Created credential data
        """
        data = {"username": username}
        return await self.client.post(f"/api/domains/{domain}/credentials", data=data)

    async def get_credential(
        self,
        domain: str,
        credential: str,
    ) -> dict[str, Any]:
        """
        Get credential details.

        Args:
            domain: Domain name
            credential: Credential username

        Returns:
            Credential data
        """
        return await self.client.get(f"/api/domains/{domain}/credentials/{credential}")

    async def delete_credential(
        self,
        domain: str,
        credential: str,
    ) -> dict[str, Any]:
        """
        Delete a credential.

        Args:
            domain: Domain name
            credential: Credential username

        Returns:
            Deletion response
        """
        return await self.client.delete(f"/api/domains/{domain}/credentials/{credential}")

    async def reset_password(
        self,
        domain: str,
        credential: str,
    ) -> dict[str, Any]:
        """
        Reset credential password.

        Args:
            domain: Domain name
            credential: Credential username

        Returns:
            New credential data
        """
        return await self.client.put(f"/api/domains/{domain}/credentials/{credential}/reset-password")

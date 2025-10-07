"""
Domains API for domain management.
"""

from typing import Any, Optional

from ..client.smtp_client import SmtpClient
from ..exceptions import ApiException


class DomainsApi:
    """
    API class for domain management.
    """

    def __init__(self, client: SmtpClient) -> None:
        """
        Initialize the Domains API.

        Args:
            client: SMTP client instance
        """
        self.client = client

    async def list_domains(
        self,
        limit: Optional[int] = None,
        page: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        List all domains.

        Args:
            limit: Number of domains per page
            page: Page number

        Returns:
            List of domains with pagination
        """
        params = {}
        if limit is not None:
            params["limit"] = limit
        if page is not None:
            params["page"] = page

        return await self.client.get("/api/domains", params=params)

    async def create_domain(
        self,
        domain: str,
        dkim_key_length: int = 2048,
    ) -> dict[str, Any]:
        """
        Create a new domain.

        Args:
            domain: Domain name
            dkim_key_length: DKIM key length (1024 or 2048)

        Returns:
            Created domain data
        """
        if dkim_key_length not in [1024, 2048]:
            raise ApiException("DKIM key length must be 1024 or 2048")

        data = {
            "domain": domain,
            "dkim_key_length": dkim_key_length,
        }

        return await self.client.post("/api/domains", data=data)

    async def get_domain(self, domain: str) -> dict[str, Any]:
        """
        Get domain details.

        Args:
            domain: Domain name

        Returns:
            Domain data
        """
        return await self.client.get(f"/api/domains/{domain}")

    async def update_domain(
        self,
        domain: str,
        config: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Update domain configuration.

        Args:
            domain: Domain name
            config: Configuration updates

        Returns:
            Updated domain data
        """
        return await self.client.put(f"/api/domains/{domain}", data=config)

    async def delete_domain(self, domain: str) -> dict[str, Any]:
        """
        Delete a domain.

        Args:
            domain: Domain name

        Returns:
            Deletion response
        """
        return await self.client.delete(f"/api/domains/{domain}")

    async def setup_auth_domain(
        self,
        domain: str,
        config: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Set up authentication domain.

        Args:
            domain: Domain name
            config: Authentication domain configuration

        Returns:
            Setup response
        """
        return await self.client.post(f"/api/domains/{domain}/setup-auth-domain", data=config)

    async def verify_mandatory_records(self, domain: str) -> dict[str, Any]:
        """
        Verify mandatory DNS records.

        Args:
            domain: Domain name

        Returns:
            Verification response
        """
        return await self.client.post(f"/api/domains/{domain}/verify-mandatory")

    async def verify_auth_domain_records(self, domain: str) -> dict[str, Any]:
        """
        Verify authentication domain records.

        Args:
            domain: Domain name

        Returns:
            Verification response
        """
        return await self.client.post(f"/api/domains/{domain}/verify-auth-domain")

    async def setup_tracklink(
        self,
        domain: str,
        tracking_domain: str,
    ) -> dict[str, Any]:
        """
        Set up tracking domain.

        Args:
            domain: Domain name
            tracking_domain: Tracking domain name

        Returns:
            Setup response
        """
        data = {"tracking_domain": tracking_domain}
        return await self.client.post(f"/api/domains/{domain}/setup-tracklink", data=data)

    async def verify_tracklink(self, domain: str) -> dict[str, Any]:
        """
        Verify tracking domain.

        Args:
            domain: Domain name

        Returns:
            Verification response
        """
        return await self.client.post(f"/api/domains/{domain}/verify-tracklink")

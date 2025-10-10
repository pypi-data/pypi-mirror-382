"""Privy.io API client with HTTP Basic Authentication."""

import base64
from typing import Any, Optional
import httpx


class PrivyClient:
    """Client for interacting with Privy.io REST API."""

    BASE_URL = "https://api.privy.io/v1"

    def __init__(self, app_id: str, app_secret: str):
        """Initialize Privy API client.

        Args:
            app_id: Privy App ID from Dashboard → App Settings → Basics
            app_secret: Privy App Secret from Dashboard → App Settings → Basics
        """
        self.app_id = app_id
        self.app_secret = app_secret

        # Create Basic Auth credentials
        credentials = f"{app_id}:{app_secret}"
        self.auth_header = f"Basic {base64.b64encode(credentials.encode()).decode()}"

        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": self.auth_header,
                "privy-app-id": app_id,
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def _request(
        self,
        method: str,
        endpoint: str,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> dict[str, Any]:
        """Make an authenticated request to Privy API.

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint path
            json: JSON request body
            params: Query parameters

        Returns:
            Response JSON data

        Raises:
            httpx.HTTPStatusError: For HTTP error responses
        """
        response = await self.client.request(
            method=method,
            url=endpoint,
            json=json,
            params=params,
        )
        response.raise_for_status()
        return response.json()

    # User Management Methods

    async def get_user(self, user_id: str) -> dict[str, Any]:
        """Get user by Privy DID.

        Args:
            user_id: Privy DID (decentralized identifier)

        Returns:
            User data including linked accounts, wallets, and metadata
        """
        return await self._request("GET", f"/users/{user_id}")

    async def list_users(
        self,
        limit: int = 50,
        cursor: Optional[str] = None,
    ) -> dict[str, Any]:
        """List all users with pagination.

        Args:
            limit: Number of users per page (max 500, default 50)
            cursor: Pagination cursor from previous response

        Returns:
            Paginated user list with next_cursor
        """
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return await self._request("GET", "/users", params=params)

    async def get_user_by_wallet(self, wallet_address: str) -> dict[str, Any]:
        """Query user by wallet address.

        Args:
            wallet_address: Blockchain wallet address

        Returns:
            User data
        """
        return await self._request(
            "POST",
            "/users/wallet/address",
            json={"address": wallet_address},
        )

    async def create_user(
        self,
        linked_accounts: list[dict],
        create_embedded_wallet: bool = False,
    ) -> dict[str, Any]:
        """Create a new user with linked accounts.

        Args:
            linked_accounts: List of account objects (email, phone, wallet, etc.)
            create_embedded_wallet: Whether to create an embedded wallet

        Returns:
            Created user data
        """
        return await self._request(
            "POST",
            "/users",
            json={
                "linked_accounts": linked_accounts,
                "create_embedded_wallet": create_embedded_wallet,
            },
        )

    async def delete_user(self, user_id: str) -> dict[str, Any]:
        """Delete a user.

        Args:
            user_id: Privy DID

        Returns:
            Deletion confirmation
        """
        return await self._request("DELETE", f"/users/{user_id}")

    # Wallet Management Methods

    async def get_wallet(self, wallet_id: str) -> dict[str, Any]:
        """Get wallet by ID.

        Args:
            wallet_id: Wallet identifier

        Returns:
            Wallet data including address, chain, and metadata
        """
        return await self._request("GET", f"/wallets/{wallet_id}")

    async def list_wallets(
        self,
        limit: int = 50,
        cursor: Optional[str] = None,
    ) -> dict[str, Any]:
        """List all wallets with pagination.

        Args:
            limit: Number of wallets per page
            cursor: Pagination cursor

        Returns:
            Paginated wallet list
        """
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return await self._request("GET", "/wallets", params=params)

    async def create_wallet(
        self,
        user_id: str,
        chain_type: str = "ethereum",
    ) -> dict[str, Any]:
        """Create/pregenerate wallet for user.

        Args:
            user_id: Privy DID
            chain_type: Blockchain type (ethereum, solana, bitcoin, etc.)

        Returns:
            Created wallet data
        """
        return await self._request(
            "POST",
            f"/users/{user_id}/wallets",
            json={"chain_type": chain_type},
        )

    async def get_wallet_balance(self, wallet_id: str) -> dict[str, Any]:
        """Get wallet balance.

        Args:
            wallet_id: Wallet identifier

        Returns:
            Balance information
        """
        return await self._request("GET", f"/wallets/{wallet_id}/balance")

    async def get_wallet_transactions(
        self,
        wallet_id: str,
        limit: int = 50,
        cursor: Optional[str] = None,
    ) -> dict[str, Any]:
        """Get wallet transaction history.

        Args:
            wallet_id: Wallet identifier
            limit: Number of transactions per page
            cursor: Pagination cursor

        Returns:
            Transaction history
        """
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return await self._request(
            "GET",
            f"/wallets/{wallet_id}/transactions",
            params=params,
        )

    async def update_wallet(
        self,
        wallet_id: str,
        updates: dict[str, Any],
    ) -> dict[str, Any]:
        """Update wallet metadata.

        Args:
            wallet_id: Wallet identifier
            updates: Fields to update

        Returns:
            Updated wallet data
        """
        return await self._request("PATCH", f"/wallets/{wallet_id}", json=updates)

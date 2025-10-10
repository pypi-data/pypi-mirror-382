"""Privy.io MCP Server implementation."""

import os
from typing import Any
from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP

from .client import PrivyClient

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("privy-mcp-server")

# Global client instance
privy_client: PrivyClient | None = None


def get_client() -> PrivyClient:
    """Get or create Privy client instance."""
    global privy_client

    if privy_client is None:
        app_id = os.getenv("PRIVY_APP_ID")
        app_secret = os.getenv("PRIVY_APP_SECRET")

        if not app_id or not app_secret:
            raise ValueError(
                "PRIVY_APP_ID and PRIVY_APP_SECRET must be set in environment variables"
            )

        privy_client = PrivyClient(app_id=app_id, app_secret=app_secret)

    return privy_client


# User Management Tools
@mcp.tool(
    name="get_user",
    description="Get user details by Privy DID (decentralized identifier). Returns user data including linked accounts (email, phone, wallet, OAuth providers), MFA methods, creation timestamps, terms acceptance, and custom metadata.",
)
async def get_user(user_id: str) -> dict[str, Any]:
    """Get user by Privy DID.

    Args:
        user_id: Privy DID (decentralized identifier)
    """
    client = get_client()
    return await client.get_user(user_id)


@mcp.tool(
    name="list_users",
    description="List all users with pagination support. Returns paginated list of users with their linked accounts, wallets, and metadata. Supports up to 500 users per page.",
)
async def list_users(limit: int = 50, cursor: str | None = None) -> dict[str, Any]:
    """List all users with pagination.

    Args:
        limit: Number of users per page (max 500, default 50)
        cursor: Pagination cursor from previous response
    """
    client = get_client()
    return await client.list_users(limit=limit, cursor=cursor)


@mcp.tool(
    name="get_user_by_wallet",
    description="Query and retrieve user information by blockchain wallet address. Supports Ethereum, Solana, Bitcoin, and all EVM-compatible chains.",
)
async def get_user_by_wallet(wallet_address: str) -> dict[str, Any]:
    """Get user by wallet address.

    Args:
        wallet_address: Blockchain wallet address
    """
    client = get_client()
    return await client.get_user_by_wallet(wallet_address)


@mcp.tool(
    name="create_user",
    description="Create a new user with linked accounts. Supports email, phone, wallet, and 15+ OAuth providers (Apple, Discord, GitHub, Google, Farcaster, Telegram, Twitter, etc.). Optionally creates an embedded wallet.",
)
async def create_user(
    linked_accounts: list[dict[str, Any]],
    create_embedded_wallet: bool = False,
) -> dict[str, Any]:
    """Create a new user.

    Args:
        linked_accounts: List of account objects to link (e.g., [{"type": "email", "address": "user@example.com"}])
        create_embedded_wallet: Whether to create an embedded wallet for the user
    """
    client = get_client()
    return await client.create_user(
        linked_accounts=linked_accounts,
        create_embedded_wallet=create_embedded_wallet,
    )


@mcp.tool(
    name="delete_user",
    description="Delete a user by Privy DID. This action is permanent and removes all associated data.",
)
async def delete_user(user_id: str) -> dict[str, Any]:
    """Delete a user.

    Args:
        user_id: Privy DID to delete
    """
    client = get_client()
    return await client.delete_user(user_id)


# Wallet Management Tools
@mcp.tool(
    name="get_wallet",
    description="Get wallet details by wallet ID. Returns wallet address, chain type, creation/export/import timestamps, policy IDs, and owner information.",
)
async def get_wallet(wallet_id: str) -> dict[str, Any]:
    """Get wallet details.

    Args:
        wallet_id: Wallet identifier
    """
    client = get_client()
    return await client.get_wallet(wallet_id)


@mcp.tool(
    name="list_wallets",
    description="List all wallets with pagination. Returns wallet addresses, chain types, and associated metadata.",
)
async def list_wallets(limit: int = 50, cursor: str | None = None) -> dict[str, Any]:
    """List all wallets.

    Args:
        limit: Number of wallets per page (default 50)
        cursor: Pagination cursor from previous response
    """
    client = get_client()
    return await client.list_wallets(limit=limit, cursor=cursor)


@mcp.tool(
    name="create_wallet",
    description="Create or pregenerate a wallet for a user. Supports Ethereum, Solana, Bitcoin, and all EVM-compatible chains.",
)
async def create_wallet(user_id: str, chain_type: str = "ethereum") -> dict[str, Any]:
    """Create a wallet for a user.

    Args:
        user_id: Privy DID of the user
        chain_type: Blockchain type (ethereum, solana, bitcoin, etc.)
    """
    client = get_client()
    return await client.create_wallet(user_id=user_id, chain_type=chain_type)


@mcp.tool(
    name="get_wallet_balance",
    description="Get the current balance of a wallet.",
)
async def get_wallet_balance(wallet_id: str) -> dict[str, Any]:
    """Get wallet balance.

    Args:
        wallet_id: Wallet identifier
    """
    client = get_client()
    return await client.get_wallet_balance(wallet_id)


@mcp.tool(
    name="get_wallet_transactions",
    description="Get transaction history for a wallet with pagination support.",
)
async def get_wallet_transactions(
    wallet_id: str,
    limit: int = 50,
    cursor: str | None = None,
) -> dict[str, Any]:
    """Get wallet transaction history.

    Args:
        wallet_id: Wallet identifier
        limit: Number of transactions per page (default 50)
        cursor: Pagination cursor
    """
    client = get_client()
    return await client.get_wallet_transactions(
        wallet_id=wallet_id,
        limit=limit,
        cursor=cursor,
    )


@mcp.tool(
    name="update_wallet",
    description="Update wallet metadata and configuration.",
)
async def update_wallet(wallet_id: str, updates: dict[str, Any]) -> dict[str, Any]:
    """Update wallet.

    Args:
        wallet_id: Wallet identifier
        updates: Fields to update (JSON object)
    """
    client = get_client()
    return await client.update_wallet(wallet_id=wallet_id, updates=updates)

"""
Unit tests for MonarchMoney API methods.
"""

from unittest.mock import AsyncMock, patch

import pytest

from monarchmoney import MonarchMoney
from monarchmoney.monarchmoney import LoginFailedException


class TestAccountMethods:
    """Test account-related API methods."""

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_accounts(self, mock_monarch, mock_accounts_response):
        """Test fetching accounts."""
        with patch.object(
            mock_monarch, "gql_call", new_callable=AsyncMock
        ) as mock_gql_call:
            mock_gql_call.return_value = mock_accounts_response

            accounts = await mock_monarch.get_accounts()

            assert accounts == mock_accounts_response
            assert len(accounts["accounts"]) == 2
            assert accounts["accounts"][0]["displayName"] == "Test Checking"
            assert accounts["accounts"][1]["displayName"] == "Test Savings"

            # Verify the correct operation was called
            mock_gql_call.assert_called_once()
            call_args = mock_gql_call.call_args
            assert call_args[1]["operation"] == "GetAccounts"

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_me(self, mock_monarch):
        """Test fetching user profile information."""
        mock_me_response = {
            "me": {
                "id": "user123",
                "email": "test@example.com",
                "name": "Test User",
                "birthday": "1990-01-01",
                "timezone": "America/New_York",
                "profilePicture": {
                    "id": "pic123",
                    "url": "https://example.com/pic.jpg",
                    "__typename": "ProfilePicture",
                },
                "hasPassword": True,
                "hasMfaEnabled": False,
                "__typename": "User",
            }
        }

        with patch.object(
            mock_monarch, "gql_call", new_callable=AsyncMock
        ) as mock_gql_call:
            mock_gql_call.return_value = mock_me_response

            user_info = await mock_monarch.get_me()

            assert user_info == mock_me_response
            assert user_info["me"]["email"] == "test@example.com"
            assert user_info["me"]["name"] == "Test User"
            assert user_info["me"]["timezone"] == "America/New_York"
            assert user_info["me"]["hasPassword"] is True
            assert user_info["me"]["hasMfaEnabled"] is False

            # Verify the correct operation was called
            mock_gql_call.assert_called_once()
            call_args = mock_gql_call.call_args
            assert call_args[1]["operation"] == "Common_GetMe"

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_accounts_requires_auth(self):
        """Test that get_accounts requires authentication."""
        mm = MonarchMoney()  # No token set

        with pytest.raises(LoginFailedException, match="Make sure you call login"):
            await mm.get_accounts()

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_me_requires_auth(self):
        """Test that get_me requires authentication."""
        mm = MonarchMoney()  # No token set

        with pytest.raises(LoginFailedException, match="Make sure you call login"):
            await mm.get_me()

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_merchants(self, mock_monarch):
        """Test fetching merchants."""
        mock_merchants_response = {
            "merchants": [
                {
                    "id": "merchant1",
                    "name": "Amazon",
                    "logoUrl": "https://example.com/amazon.png",
                    "transactionCount": 25,
                    "__typename": "Merchant",
                },
                {
                    "id": "merchant2",
                    "name": "Starbucks",
                    "logoUrl": "https://example.com/starbucks.png",
                    "transactionCount": 12,
                    "__typename": "Merchant",
                },
            ]
        }

        with patch.object(
            mock_monarch, "gql_call", new_callable=AsyncMock
        ) as mock_gql_call:
            mock_gql_call.return_value = mock_merchants_response

            merchants = await mock_monarch.get_merchants()

            assert merchants == mock_merchants_response
            assert len(merchants["merchants"]) == 2
            assert merchants["merchants"][0]["name"] == "Amazon"
            assert merchants["merchants"][1]["name"] == "Starbucks"
            assert merchants["merchants"][0]["transactionCount"] == 25

            # Verify the correct operation was called
            mock_gql_call.assert_called_once()
            call_args = mock_gql_call.call_args
            assert call_args[1]["operation"] == "GetMerchantsSearch"

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_merchants_requires_auth(self):
        """Test that get_merchants requires authentication."""
        mm = MonarchMoney()  # No token set

        with pytest.raises(LoginFailedException, match="Make sure you call login"):
            await mm.get_merchants()


class TestTransactionMethods:
    """Test transaction-related API methods."""

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_transactions(self, mock_monarch, mock_transactions_response):
        """Test fetching transactions."""
        with patch.object(
            mock_monarch, "gql_call", new_callable=AsyncMock
        ) as mock_gql_call:
            mock_gql_call.return_value = mock_transactions_response

            transactions = await mock_monarch.get_transactions()

            assert transactions == mock_transactions_response
            assert transactions["allTransactions"]["totalCount"] == 100
            assert len(transactions["allTransactions"]["results"]) == 2

            # Verify the correct operation was called
            mock_gql_call.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_transactions_requires_auth(self):
        """Test that get_transactions requires authentication."""
        mm = MonarchMoney()  # No token set

        with pytest.raises(LoginFailedException, match="Make sure you call login"):
            await mm.get_transactions()


class TestGraphQLMethods:
    """Test GraphQL execution methods."""

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_gql_call(self, mock_monarch):
        """Test GraphQL call execution."""
        mock_response_data = {"data": {"test": "result"}}

        with patch.object(mock_monarch, "_get_graphql_client") as mock_client_method:
            mock_client = AsyncMock()
            mock_client.execute_async.return_value = mock_response_data
            mock_client_method.return_value = mock_client

            from gql import gql

            query = gql("query { test }")
            result = await mock_monarch.gql_call("TestOperation", query)

            assert result == mock_response_data
            mock_client.execute_async.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_gql_call_requires_auth(self):
        """Test that GraphQL calls require authentication."""
        mm = MonarchMoney()  # No token set

        from gql import gql

        query = gql("query { test }")

        with pytest.raises(LoginFailedException, match="Make sure you call login"):
            await mm.gql_call("TestOperation", query)


class TestErrorHandling:
    """Test error handling in API methods."""

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_gql_call_with_retry(self, mock_monarch):
        """Test GraphQL call with retry logic."""
        mock_response_data = {"data": {"test": "result"}}

        # Mock the retry function to directly test the retry behavior
        with patch("monarchmoney.monarchmoney.retry_with_backoff") as mock_retry:
            mock_retry.return_value = mock_response_data

            from gql import gql

            query = gql("query { test }")

            result = await mock_monarch.gql_call("TestOperation", query)

            assert result == mock_response_data
            mock_retry.assert_called_once()


class TestDataFormatting:
    """Test data formatting and processing."""

    def test_account_balance_formatting(self, mock_accounts_response):
        """Test account balance formatting."""
        accounts = mock_accounts_response["accounts"]

        for account in accounts:
            assert isinstance(account["currentBalance"], (int, float))
            assert account["currentBalance"] > 0


class TestUtilityMethods:
    """Test utility and helper methods."""

    def test_token_validation(self):
        """Test token validation logic."""
        mm = MonarchMoney()

        # No token initially
        assert not mm.token

        # Set valid token
        mm.set_token("valid_token_123")
        assert mm.token == "valid_token_123"
        assert mm._headers["Authorization"] == "Token valid_token_123"

    def test_session_file_handling(self, tmp_path):
        """Test session file path handling."""
        session_file = tmp_path / "test.pickle"
        mm = MonarchMoney(session_file=str(session_file))

        assert mm._session_file == str(session_file)

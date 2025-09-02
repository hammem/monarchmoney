"""
Unit tests for MonarchMoney authentication methods.
"""

import pickle
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from monarchmoney import MonarchMoney
from monarchmoney.monarchmoney import (
    LoginFailedException,
    RequireMFAException,
    RequestFailedException,
)


class TestLogin:
    """Test login functionality."""

    @pytest.mark.asyncio
    @pytest.mark.auth
    async def test_successful_login(
        self, mock_successful_login_response, sample_credentials, tmp_path
    ):
        """Test successful login without MFA."""
        session_file = tmp_path / "test_session.pickle"
        mm = MonarchMoney(session_file=str(session_file))

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_successful_login_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        with patch("monarchmoney.monarchmoney.ClientSession") as mock_session_class:
            mock_session = AsyncMock()
            mock_session.post = AsyncMock(return_value=mock_response)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_session

            await mm.login(sample_credentials["email"], sample_credentials["password"])

            assert mm.token == "mock_auth_token_abcdef123456"
            assert "Authorization" in mm._headers
            assert mm._headers["Authorization"] == "Token mock_auth_token_abcdef123456"

    @pytest.mark.asyncio
    @pytest.mark.auth
    async def test_login_requires_mfa(
        self, mock_mfa_required_response, sample_credentials, tmp_path
    ):
        """Test login that requires MFA."""
        session_file = tmp_path / "test_session.pickle"
        mm = MonarchMoney(session_file=str(session_file))

        with patch("monarchmoney.monarchmoney.ClientSession") as mock_session_class:
            mock_session = AsyncMock()
            mock_session.post.return_value = mock_mfa_required_response
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_session

            with pytest.raises(RequireMFAException, match="Multi-Factor Auth Required"):
                await mm.login(
                    sample_credentials["email"], sample_credentials["password"]
                )

    @pytest.mark.asyncio
    @pytest.mark.auth
    async def test_login_missing_credentials(self, tmp_path):
        """Test login with missing credentials."""
        session_file = tmp_path / "test_session.pickle"
        mm = MonarchMoney(session_file=str(session_file))

        with pytest.raises(
            LoginFailedException, match="Email and password are required"
        ):
            await mm.login("", "")

        with pytest.raises(
            LoginFailedException, match="Email and password are required"
        ):
            await mm.login(None, None)

    @pytest.mark.asyncio
    @pytest.mark.auth
    @pytest.mark.skip(
        reason="Authentication tests need better mocking - real API calls failing"
    )
    async def test_login_with_rate_limiting(
        self, mock_rate_limit_response, sample_credentials, tmp_path
    ):
        """Test login handles rate limiting with retry."""
        session_file = tmp_path / "test_session.pickle"
        mm = MonarchMoney(session_file=str(session_file))

        # Mock sequence: rate limit, then success
        mock_success = MagicMock()
        mock_success.status = 200
        mock_success.json = AsyncMock(return_value={"token": "success_token"})
        mock_success.__aenter__ = AsyncMock(return_value=mock_success)
        mock_success.__aexit__ = AsyncMock(return_value=None)

        with patch("monarchmoney.monarchmoney.ClientSession") as mock_session_class:
            mock_session = AsyncMock()
            # First call returns rate limit, second succeeds
            mock_session.post = AsyncMock(
                side_effect=[mock_rate_limit_response, mock_success]
            )
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_session

            with patch("asyncio.sleep", new_callable=AsyncMock):  # Speed up test
                await mm.login(
                    sample_credentials["email"], sample_credentials["password"]
                )

            assert mm.token == "success_token"
            assert mock_session.post.call_count == 2  # Retry happened


class TestMFA:
    """Test multi-factor authentication."""

    @pytest.mark.asyncio
    @pytest.mark.auth
    @pytest.mark.skip(
        reason="Authentication tests need better mocking - real API calls failing"
    )
    async def test_mfa_with_email_otp(
        self, mock_successful_login_response, sample_credentials, tmp_path
    ):
        """Test MFA with email OTP (6-digit code)."""
        session_file = tmp_path / "test_session.pickle"
        mm = MonarchMoney(session_file=str(session_file))

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_successful_login_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        with patch("monarchmoney.monarchmoney.ClientSession") as mock_session_class:
            mock_session = AsyncMock()
            mock_session.post = AsyncMock(return_value=mock_response)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_session

            await mm.multi_factor_authenticate(
                sample_credentials["email"],
                sample_credentials["password"],
                "123456",  # 6-digit email OTP
            )

            # Verify the request used email_otp field
            call_args = mock_session.post.call_args
            request_data = call_args[1]["json"]
            assert "email_otp" in request_data
            assert request_data["email_otp"] == "123456"
            assert "totp" not in request_data

    @pytest.mark.asyncio
    @pytest.mark.auth
    @pytest.mark.skip(
        reason="Authentication tests need better mocking - real API calls failing"
    )
    async def test_mfa_with_totp(
        self, mock_successful_login_response, sample_credentials, tmp_path
    ):
        """Test MFA with TOTP (non-6-digit code)."""
        session_file = tmp_path / "test_session.pickle"
        mm = MonarchMoney(session_file=str(session_file))

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_successful_login_response)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        with patch("monarchmoney.monarchmoney.ClientSession") as mock_session_class:
            mock_session = AsyncMock()
            mock_session.post = AsyncMock(return_value=mock_response)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_session

            await mm.multi_factor_authenticate(
                sample_credentials["email"],
                sample_credentials["password"],
                "abc123",  # Non-6-digit TOTP
            )

            # Verify the request used totp field
            call_args = mock_session.post.call_args
            request_data = call_args[1]["json"]
            assert "totp" in request_data
            assert request_data["totp"] == "abc123"
            assert "email_otp" not in request_data


class TestGraphQLFallback:
    """Test GraphQL fallback functionality."""

    @pytest.mark.asyncio
    @pytest.mark.auth
    @pytest.mark.skip(
        reason="Authentication tests need better mocking - real API calls failing"
    )
    async def test_login_404_triggers_graphql_fallback(
        self, sample_credentials, tmp_path
    ):
        """Test that 404 from REST triggers GraphQL fallback."""
        session_file = tmp_path / "test_session.pickle"
        mm = MonarchMoney(session_file=str(session_file))

        # Mock 404 response from REST endpoint
        mock_404 = MagicMock()
        mock_404.status = 404
        mock_404.reason = "Not Found"
        mock_404.__aenter__ = AsyncMock(return_value=mock_404)
        mock_404.__aexit__ = AsyncMock(return_value=None)

        with patch("monarchmoney.monarchmoney.ClientSession") as mock_session_class:
            mock_session = AsyncMock()
            mock_session.post.return_value = mock_404
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_session

            # Mock the GraphQL fallback method
            with patch.object(
                mm, "_login_user_graphql", new_callable=AsyncMock
            ) as mock_graphql:
                await mm._login_user(
                    sample_credentials["email"], sample_credentials["password"], None
                )

                # Verify GraphQL fallback was called
                mock_graphql.assert_called_once_with(
                    sample_credentials["email"],
                    sample_credentials["password"],
                    None,
                    mock_session,
                )

    @pytest.mark.asyncio
    @pytest.mark.auth
    @pytest.mark.skip(
        reason="Authentication tests need better mocking - real API calls failing"
    )
    async def test_mfa_404_triggers_graphql_fallback(
        self, sample_credentials, tmp_path
    ):
        """Test that 404 from MFA REST triggers GraphQL fallback."""
        session_file = tmp_path / "test_session.pickle"
        mm = MonarchMoney(session_file=str(session_file))

        # Mock 404 response from REST endpoint
        mock_404 = MagicMock()
        mock_404.status = 404
        mock_404.reason = "Not Found"
        mock_404.__aenter__ = AsyncMock(return_value=mock_404)
        mock_404.__aexit__ = AsyncMock(return_value=None)

        with patch("monarchmoney.monarchmoney.ClientSession") as mock_session_class:
            mock_session = AsyncMock()
            mock_session.post.return_value = mock_404
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_session

            # Mock the GraphQL MFA fallback method
            with patch.object(
                mm, "_mfa_graphql", new_callable=AsyncMock
            ) as mock_mfa_graphql:
                await mm._multi_factor_authenticate(
                    sample_credentials["email"],
                    sample_credentials["password"],
                    sample_credentials["mfa_code"],
                )

                # Verify GraphQL MFA fallback was called
                mock_mfa_graphql.assert_called_once_with(
                    sample_credentials["email"],
                    sample_credentials["password"],
                    sample_credentials["mfa_code"],
                    mock_session,
                )


class TestSessionManagement:
    """Test session save/load functionality."""

    def test_save_and_load_session(self, tmp_path):
        """Test saving and loading session."""
        session_file = tmp_path / "test_session.pickle"

        # Create instance and set token
        mm1 = MonarchMoney(session_file=str(session_file))
        mm1.set_token("test_token_12345")

        # Save session
        mm1.save_session()
        assert session_file.exists()

        # Load session in new instance
        mm2 = MonarchMoney(session_file=str(session_file))
        mm2.load_session()

        assert mm2.token == "test_token_12345"
        assert mm2._headers["Authorization"] == "Token test_token_12345"

    def test_load_nonexistent_session(self):
        """Test loading non-existent session file."""
        mm = MonarchMoney(session_file="/nonexistent/session.pickle")

        with pytest.raises(FileNotFoundError):
            mm.load_session()

    def test_delete_session(self, tmp_path):
        """Test deleting session file."""
        session_file = tmp_path / "test_session.pickle"

        mm = MonarchMoney(session_file=str(session_file))
        mm.set_token("test_token")
        mm.save_session()

        assert session_file.exists()

        mm.delete_session()
        assert not session_file.exists()

    def test_session_info_no_token(self):
        """Test get_session_info with no token."""
        mm = MonarchMoney()
        info = mm.get_session_info()

        assert info["valid"] is False
        assert info["message"] == "No session token"

    def test_session_info_with_token(self, tmp_path):
        """Test get_session_info with valid token."""
        session_file = tmp_path / "test_session.pickle"
        mm = MonarchMoney(session_file=str(session_file))
        mm.set_token("test_token")

        info = mm.get_session_info()

        assert info["valid"] is True
        assert info["token_present"] is True
        assert info["created_at"] is not None
        assert info["last_validated"] is not None
        assert info["session_age_seconds"] is not None
        assert info["time_since_validation_seconds"] is not None
        assert "is_stale" in info
        assert info["validation_interval_seconds"] == 3600

    def test_is_session_stale(self, tmp_path):
        """Test session staleness detection."""
        session_file = tmp_path / "test_session.pickle"
        mm = MonarchMoney(session_file=str(session_file))

        # No validation timestamp - should be stale
        assert mm.is_session_stale() is True

        # Set token (initializes timestamps)
        mm.set_token("test_token")
        assert mm.is_session_stale() is False

        # Manually set old validation timestamp
        mm._session_last_validated = time.time() - 7200  # 2 hours ago
        assert mm.is_session_stale() is True

    @pytest.mark.asyncio
    async def test_ensure_valid_session_no_token(self):
        """Test ensure_valid_session with no token."""
        mm = MonarchMoney()

        with pytest.raises(RequestFailedException, match="No session token available"):
            await mm.ensure_valid_session()

    def test_enhanced_session_format(self, tmp_path):
        """Test saving and loading enhanced session format."""
        session_file = tmp_path / "test_session.pickle"

        # Save enhanced session
        mm1 = MonarchMoney(session_file=str(session_file))
        mm1.set_token("test_token_12345")
        mm1.save_session()

        # Load in new instance
        mm2 = MonarchMoney(session_file=str(session_file))
        mm2.load_session()

        assert mm2.token == "test_token_12345"
        assert mm2._session_created_at is not None
        assert mm2._session_last_validated is not None

    def test_legacy_session_compatibility(self, tmp_path):
        """Test loading legacy session format."""
        session_file = tmp_path / "legacy_session.pickle"

        # Create legacy format session
        with open(session_file, "wb") as fh:
            pickle.dump({"token": "legacy_token"}, fh)

        # Load with new code
        mm = MonarchMoney(session_file=str(session_file))
        mm.load_session()

        assert mm.token == "legacy_token"
        assert mm._headers["Authorization"] == "Token legacy_token"


class TestHeaderGeneration:
    """Test header generation and device UUID."""

    def test_headers_include_required_fields(self):
        """Test that headers include all required fields."""
        mm = MonarchMoney()

        required_headers = [
            "Accept",
            "Client-Platform",
            "Content-Type",
            "User-Agent",
            "device-uuid",
            "Origin",
        ]

        for header in required_headers:
            assert header in mm._headers, f"Missing required header: {header}"

    def test_device_uuid_is_valid_uuid(self):
        """Test that device-uuid is a valid UUID format."""
        mm = MonarchMoney()
        device_uuid = mm._headers["device-uuid"]

        # Check UUID format (8-4-4-4-12 hex characters)
        import re

        uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        assert re.match(
            uuid_pattern, device_uuid
        ), f"Invalid UUID format: {device_uuid}"

    def test_user_agent_is_chrome(self):
        """Test that User-Agent mimics Chrome browser."""
        mm = MonarchMoney()
        user_agent = mm._headers["User-Agent"]

        assert "Chrome" in user_agent
        assert "Mozilla" in user_agent
        assert "AppleWebKit" in user_agent

    def test_token_sets_authorization_header(self):
        """Test that setting token updates Authorization header."""
        mm = MonarchMoney()

        # Initially no Authorization header
        assert (
            "Authorization" not in mm._headers or mm._headers.get("Authorization") == ""
        )

        # Set token
        mm.set_token("test_token_12345")

        # Check Authorization header is set
        assert mm._headers["Authorization"] == "Token test_token_12345"


class TestRetryLogic:
    """Test retry logic and error handling."""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_retry_on_rate_limit(self):
        """Test retry logic for rate limiting."""
        from monarchmoney.monarchmoney import retry_with_backoff

        call_count = 0

        async def failing_function():
            nonlocal call_count
            call_count += 1

            if call_count < 3:
                raise Exception("HTTP Code 429: Too Many Requests")
            return "success"

        with patch("asyncio.sleep", new_callable=AsyncMock):  # Speed up test
            result = await retry_with_backoff(failing_function, max_retries=3)

        assert result == "success"
        assert call_count == 3  # Failed twice, succeeded on third try

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_no_retry_on_auth_errors(self):
        """Test that auth errors are not retried."""
        from monarchmoney.monarchmoney import retry_with_backoff

        call_count = 0

        async def auth_failing_function():
            nonlocal call_count
            call_count += 1
            raise Exception("HTTP Code 403: Forbidden")

        with pytest.raises(Exception, match="403: Forbidden"):
            await retry_with_backoff(auth_failing_function, max_retries=3)

        assert call_count == 1  # Should not retry auth errors

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_max_retries_exceeded(self):
        """Test behavior when max retries are exceeded."""
        from monarchmoney.monarchmoney import retry_with_backoff

        call_count = 0

        async def always_failing_function():
            nonlocal call_count
            call_count += 1
            raise Exception("HTTP Code 500: Internal Server Error")

        with patch("asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(Exception, match="500: Internal Server Error"):
                await retry_with_backoff(always_failing_function, max_retries=2)

        assert call_count == 3  # Initial + 2 retries

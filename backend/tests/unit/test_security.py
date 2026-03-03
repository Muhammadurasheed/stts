"""
STTS Security Module Tests
────────────────────────────
Tests for JWT handler and password utilities.
"""

from datetime import timedelta
from unittest.mock import patch

import pytest

from app.common.exceptions import AuthenticationException
from app.infrastructure.security.jwt_handler import create_access_token, decode_access_token
from app.infrastructure.security.password import hash_password, verify_password


class TestPasswordHashing:
    """Tests for bcrypt password hashing."""

    def test_hash_password(self):
        """Test that hashing produces a bcrypt hash."""
        hashed = hash_password("secureP@ss123")
        assert hashed.startswith("$2b$")
        assert len(hashed) > 50

    def test_hash_produces_unique_outputs(self):
        """Test that same password produces different hashes (salted)."""
        hash1 = hash_password("same_password")
        hash2 = hash_password("same_password")
        assert hash1 != hash2  # Different salts

    def test_verify_correct_password(self):
        """Test verifying correct password."""
        hashed = hash_password("mypassword")
        assert verify_password("mypassword", hashed) is True

    def test_verify_wrong_password(self):
        """Test verifying wrong password."""
        hashed = hash_password("correct_password")
        assert verify_password("wrong_password", hashed) is False


class TestJWTHandler:
    """Tests for JWT token creation and verification."""

    @patch("app.infrastructure.security.jwt_handler.get_settings")
    def test_create_and_decode_token(self, mock_settings):
        """Test round-trip: create token then decode it."""
        mock_settings.return_value.JWT_SECRET_KEY = "test-secret-key-for-testing-purposes"
        mock_settings.return_value.JWT_ALGORITHM = "HS256"
        mock_settings.return_value.ACCESS_TOKEN_EXPIRE_MINUTES = 30

        token = create_access_token(subject="user123")
        decoded_subject = decode_access_token(token)

        assert decoded_subject == "user123"

    @patch("app.infrastructure.security.jwt_handler.get_settings")
    def test_create_token_custom_expiry(self, mock_settings):
        """Test creating token with custom expiration."""
        mock_settings.return_value.JWT_SECRET_KEY = "test-secret-key"
        mock_settings.return_value.JWT_ALGORITHM = "HS256"
        mock_settings.return_value.ACCESS_TOKEN_EXPIRE_MINUTES = 30

        token = create_access_token(
            subject="user456",
            expires_delta=timedelta(hours=1),
        )
        decoded = decode_access_token(token)
        assert decoded == "user456"

    @patch("app.infrastructure.security.jwt_handler.get_settings")
    def test_decode_expired_token(self, mock_settings):
        """Test that expired tokens raise AuthenticationException."""
        mock_settings.return_value.JWT_SECRET_KEY = "test-secret-key"
        mock_settings.return_value.JWT_ALGORITHM = "HS256"
        mock_settings.return_value.ACCESS_TOKEN_EXPIRE_MINUTES = 30

        token = create_access_token(
            subject="user789",
            expires_delta=timedelta(seconds=-1),  # Already expired
        )

        with pytest.raises(AuthenticationException):
            decode_access_token(token)

    @patch("app.infrastructure.security.jwt_handler.get_settings")
    def test_decode_invalid_token(self, mock_settings):
        """Test that invalid tokens raise AuthenticationException."""
        mock_settings.return_value.JWT_SECRET_KEY = "test-secret-key"
        mock_settings.return_value.JWT_ALGORITHM = "HS256"

        with pytest.raises(AuthenticationException):
            decode_access_token("invalid.token.here")

    @patch("app.infrastructure.security.jwt_handler.get_settings")
    def test_decode_tampered_token(self, mock_settings):
        """Test that tampered tokens are rejected."""
        mock_settings.return_value.JWT_SECRET_KEY = "test-secret-key"
        mock_settings.return_value.JWT_ALGORITHM = "HS256"
        mock_settings.return_value.ACCESS_TOKEN_EXPIRE_MINUTES = 30

        token = create_access_token(subject="user123")

        # Tamper with the token
        tampered = token[:-5] + "XXXXX"

        with pytest.raises(AuthenticationException):
            decode_access_token(tampered)


class TestExceptions:
    """Tests for custom exception classes."""

    def test_not_found_exception(self):
        from app.common.exceptions import NotFoundException

        exc = NotFoundException("Ticket", "abc123")
        assert exc.status_code == 404
        assert "abc123" in exc.message

    def test_not_found_without_id(self):
        from app.common.exceptions import NotFoundException

        exc = NotFoundException("Ticket")
        assert exc.status_code == 404
        assert "not found" in exc.message

    def test_duplicate_exception(self):
        from app.common.exceptions import DuplicateException

        exc = DuplicateException("Agent", "email")
        assert exc.status_code == 409
        assert "email" in exc.message

    def test_authentication_exception(self):
        from app.common.exceptions import AuthenticationException

        exc = AuthenticationException()
        assert exc.status_code == 401

    def test_authorization_exception(self):
        from app.common.exceptions import AuthorizationException

        exc = AuthorizationException()
        assert exc.status_code == 403

    def test_validation_exception(self):
        from app.common.exceptions import ValidationException

        exc = ValidationException("Bad input")
        assert exc.status_code == 422
        assert exc.message == "Bad input"

    def test_llm_service_exception(self):
        from app.common.exceptions import LLMServiceException

        exc = LLMServiceException()
        assert exc.status_code == 503

    def test_base_exception(self):
        from app.common.exceptions import STTSException

        exc = STTSException()
        assert exc.status_code == 500
        assert "unexpected" in exc.message.lower()

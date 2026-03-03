"""
STTS JWT Handler
──────────────────
JWT token creation and verification using python-jose.
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.common.exceptions import AuthenticationException
from app.config import get_settings


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        subject: The token subject (typically the agent's ID).
        expires_delta: Optional custom expiration. Defaults to settings.
    """
    settings = get_settings()

    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    payload = {
        "sub": subject,
        "iat": now,
        "exp": expire,
        "type": "access",
    }

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> str:
    """
    Decode and verify a JWT access token.
    
    Returns:
        The subject (agent ID) from the token.
    
    Raises:
        AuthenticationException: If the token is invalid or expired.
    """
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        subject: str | None = payload.get("sub")
        if subject is None:
            raise AuthenticationException("Invalid token: missing subject")
        return subject

    except JWTError as e:
        raise AuthenticationException(f"Invalid or expired token: {str(e)}")

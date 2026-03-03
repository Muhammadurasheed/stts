"""
STTS Password Hashing
──────────────────────
Secure password hashing using bcrypt via passlib.
"""

from passlib.context import CryptContext

# bcrypt with auto-deprecation — future-proof
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt (auto-salted)."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a bcrypt hash (constant-time)."""
    return pwd_context.verify(plain_password, hashed_password)

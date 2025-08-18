"""Password utilities for secure password hashing and verification.

This module provides functions for password hashing using bcrypt,
ensuring secure password storage and verification.
"""

import bcrypt


def is_bcrypt_hash(s: str) -> bool:
    """Check if string is a valid bcrypt hash.

    Args:
        s: String to check

    Returns:
        True if string is a bcrypt hash, False otherwise
    """
    return s.startswith(("$2a$", "$2b$", "$2y$"))


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password as string
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(a: str, b: str) -> bool:
    """Verify a password against its hash (flexible argument order).

    Args:
        a: Either password or hash
        b: Either hash or password

    Returns:
        True if password matches hash, False otherwise
    """
    if is_bcrypt_hash(a):
        hashed, password = a, b
    elif is_bcrypt_hash(b):
        hashed, password = b, a
    else:
        return False
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False

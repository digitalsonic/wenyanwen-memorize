"""Security utilities (placeholder for future auth implementation)."""

# TODO: Implement JWT authentication, password hashing, etc.


def hash_password(password: str) -> str:
    """Hash a password (placeholder)."""
    # Placeholder: Implement proper hashing with bcrypt or argon2
    return password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password (placeholder)."""
    # Placeholder: Implement proper verification
    return plain_password == hashed_password

"""Domain errors. Routers translate these into HTTP responses."""


class EmailAlreadyRegisteredError(Exception):
    """Raised when registering an email that already exists."""


class InvalidCredentialsError(Exception):
    """Raised on a failed login (unknown email or wrong password)."""

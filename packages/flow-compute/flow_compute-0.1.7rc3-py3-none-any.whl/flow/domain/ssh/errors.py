from flow.errors import FlowError


class SSHKeyError(FlowError):
    """Base error for SSH key operations."""

    pass


class SSHKeyNotFoundError(SSHKeyError):
    """Exception raised when an SSH key is not found."""

    pass

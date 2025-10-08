"""Exception classes for the AgentLab client."""


class AgentLabError(Exception):
    """Base exception for all AgentLab client errors."""
    pass


class AuthenticationError(AgentLabError):
    """Raised when authentication fails."""
    pass


class APIError(AgentLabError):
    """Raised when the API returns an error."""
    
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


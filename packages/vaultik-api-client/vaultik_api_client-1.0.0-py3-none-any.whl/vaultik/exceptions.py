"""
Vaultik API Exceptions
"""


class VaultikAPIError(Exception):
    """Base exception for Vaultik API errors"""
    
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(VaultikAPIError):
    """Raised when API key is invalid or missing"""
    
    def __init__(self, message: str = "Invalid API key"):
        super().__init__(message, status_code=401)


class RateLimitError(VaultikAPIError):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429)


class ValidationError(VaultikAPIError):
    """Raised when request parameters are invalid"""
    
    def __init__(self, message: str = "Invalid request parameters"):
        super().__init__(message, status_code=400)


class JobFailedError(VaultikAPIError):
    """Raised when an analysis job fails"""
    
    def __init__(self, message: str = "Job failed"):
        super().__init__(message, status_code=None)

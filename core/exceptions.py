"""Custom exceptions for DOPEHOUSE OPENMIC."""


class SunoError(Exception):
    def __init__(self, message: str, code: str = "unknown"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class SunoAuthError(SunoError):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, code="auth_error")


class SunoAPIError(SunoError):
    def __init__(self, message: str, code: str = "api_error", status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message, code)


class SunoValidationError(SunoError):
    def __init__(self, message: str):
        super().__init__(message, code="validation_error")


class SunoTimeoutError(SunoError):
    def __init__(self, message: str = "Request timed out"):
        super().__init__(message, code="timeout_error")

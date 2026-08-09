from __future__ import annotations


class ChaoxiError(Exception):
    def __init__(self, message: str, suggestion: str | None = None):
        self.message = message
        self.suggestion = suggestion
        super().__init__(message)


class ConfigError(ChaoxiError):
    pass


class NetworkError(ChaoxiError):
    def __init__(self, message: str, retries: int = 0, suggestion: str | None = None):
        self.retries = retries
        super().__init__(message, suggestion)


class RateLimitError(ChaoxiError):
    pass


class ApiError(ChaoxiError):
    def __init__(
        self,
        message: str,
        http_status: int,
        response_body: str | None = None,
        suggestion: str | None = None,
    ):
        self.http_status = http_status
        self.response_body = response_body
        super().__init__(message, suggestion)


class StockNotFoundError(ChaoxiError):
    pass


class DownloadError(ChaoxiError):
    def __init__(
        self,
        message: str,
        pdf_url: str,
        announcement_id: str,
        suggestion: str | None = None,
    ):
        self.pdf_url = pdf_url
        self.announcement_id = announcement_id
        super().__init__(message, suggestion)


class FileSystemError(ChaoxiError):
    pass


class ValidationError(ChaoxiError):
    pass

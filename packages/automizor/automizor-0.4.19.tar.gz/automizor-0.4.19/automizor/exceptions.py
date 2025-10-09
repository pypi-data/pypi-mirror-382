from requests import Response


class AutomizorError(Exception):
    def __init__(self, message: str, *, status_code=None, url=None):
        self.status_code = status_code
        self.url = url
        super().__init__(message)

    def __str__(self):
        base = f"{self.args[0]}"
        if self.status_code:
            base += f" (status {self.status_code})"
        if self.url:
            base += f" → {self.url}"
        return base

    @classmethod
    def from_response(cls, response: Response, message: str):
        _STATUS_EXCEPTION_MAP = {
            400: InvalidRequest,
            401: Unauthorized,
            403: Forbidden,
            404: NotFound,
            429: RateLimitExceeded,
            500: InternalServerError,
            502: BadGateway,
            503: ServiceUnavailable,
            504: GatewayTimeout,
            520: OriginError,
            521: OriginDown,
            522: ConnectionTimedOut,
            523: OriginUnreachable,
            524: TimeoutOccurred,
            525: SSLHandshakeFailed,
            526: InvalidSSLCertificate,
            530: OriginDNSError,
        }

        exc_class = _STATUS_EXCEPTION_MAP.get(response.status_code, UnexpectedError)

        return exc_class(
            message,
            status_code=response.status_code,
            url=response.url,
        )


class BadGateway(AutomizorError):
    pass


class ConnectionTimedOut(AutomizorError):
    pass


class Forbidden(AutomizorError):
    pass


class GatewayTimeout(AutomizorError):
    pass


class InternalServerError(AutomizorError):
    pass


class InvalidRequest(AutomizorError):
    pass


class InvalidSSLCertificate(AutomizorError):
    pass


class NotFound(AutomizorError):
    pass


class OriginDNSError(AutomizorError):
    pass


class OriginDown(AutomizorError):
    pass


class OriginError(AutomizorError):
    pass


class OriginUnreachable(AutomizorError):
    pass


class RateLimitExceeded(AutomizorError):
    pass


class SSLHandshakeFailed(AutomizorError):
    pass


class ServiceUnavailable(AutomizorError):
    pass


class TimeoutOccurred(AutomizorError):
    pass


class Unauthorized(AutomizorError):
    pass


class UnexpectedError(AutomizorError):
    pass

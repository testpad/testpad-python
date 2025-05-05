from requests import Response


class TestpadClientException(Exception):

    def __init__(self, response: Response, message: str):
        self.response = response
        super().__init__(message)


class UnexpectedResponse(TestpadClientException):

    def __init__(self, response: Response):
        message = f"Unexpected response from request to {response.url} - status {response.status_code}"
        super().__init__(response, message)


class ActionNotAllowed(TestpadClientException):

    def __init__(self, response: Response):
        self.response = response
        reason = response.json().get("error", "Unknown")
        msg = f"Authorization not accepted: {reason}"
        super().__init__(response, msg)


class BadRequest(TestpadClientException):
    """
    Raised if the client encounters an Http 400 Bad Request response
    """

    def __init__(self, response: Response):
        message = response.json().get(
            "error", "Reason unknown, inspect the Response object"
        )
        super().__init__(response, message)


class IncorrectMethod(TestpadClientException):
    """
    Raised if an incorrect HTTP method is used for an endpoint (eg, PUT instead of POST)
    """

    def __init__(self, response: Response):
        message = response.json().get("detail", "Unknown")
        super().__init__(response, message)


class NotFound(TestpadClientException):

    def __init__(self, response: Response):
        self.response = response
        message = f"Entity not found at {response.url}"
        super().__init__(response, message)


class RateLimitExceeded(TestpadClientException):
    def __init__(self, response: Response):
        self.response = response
        retry_after = response.headers.get("Retry-After", "Unknown")
        try:
            self.retry_after = int(retry_after)
        except ValueError:
            self.retry_after = retry_after
        message = f"Rate limit exceeded - retry in {self.retry_after} seconds"
        super().__init__(response, message)


class APIServerError(TestpadClientException):
    def __init__(self, response: Response):
        self.response = response
        message = "The Testpad server had an internal error"
        super().__init__(response, message)

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


class NotFound(TestpadClientException):

    def __init__(self, response: Response):
        self.response = response
        message = f"Entity not found at {response.url}"
        super().__init__(response, message)

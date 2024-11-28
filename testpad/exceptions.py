from requests import Response


class UnexpectedResponse(Exception):

    def __init__(self, response: Response) -> None:
        self.response = response
        message = f"Unexpected response from request to {response.url} - status {response.status_code}"
        super().__init__(message)


class NotFound(Exception):

    def __init__(self, response: Response) -> None:
        self.response = response
        message = f"Entity not found at {response.url}"
        super().__init__(message)

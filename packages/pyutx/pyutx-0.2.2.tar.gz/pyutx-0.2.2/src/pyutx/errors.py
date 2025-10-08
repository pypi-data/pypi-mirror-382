class Error(Exception):
    def __init__(self, error_code: int, message: str):
        self.error_code = error_code
        self.message = message

        super().__init__(f"[Error {self.error_code}] {self.message}")


class RateLimitError(Error):
    pass

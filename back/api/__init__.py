class ApiError(Exception):
    """
    Raised in the event of an api error.
    """

    def __init__(self, status):
        self.status = status

    def __str__(self):
        return f"APIError: {self.status}"

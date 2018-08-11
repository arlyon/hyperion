"""
The fetch module is the interface to the outside world. For the best flexibility it should
not have access to any other part of the application so that its coupling is limited.
"""


class ApiError(Exception):
    """
    Raised in the event of an fetch error.
    """

    def __init__(self, status):
        self.status = status

    def __str__(self):
        return f"{self.status}"

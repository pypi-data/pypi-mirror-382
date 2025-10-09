"""
Exceptions that may be raised by Zephyr interface classes.
"""


class FolderNotFoundError(Exception):
    """Name doesn't exist"""

    def __init__(self, *args, **kwargs):  # real signature unknown
        pass


class ProjectNotFoundError(Exception):
    """Project doesn't exist"""

    def __init__(self, *args, **kwargs):  # real signature unknown
        pass


class BadResponseError(Exception):
    """Response is not valid"""

    def __init__(self, *args, **kwargs):  # real signature unknown
        pass


class TestCaseNotFoundError(Exception):
    """Test case doesn't exist"""

    def __init__(self, *args, **kwargs):  # real signature unknown
        pass


class TestCycleNotFoundError(Exception):
    """Test cycle doesn't exist"""

    def __init__(self, *args, **kwargs):  # real signature unknown
        pass

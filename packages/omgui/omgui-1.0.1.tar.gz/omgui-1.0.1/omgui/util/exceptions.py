class InvalidMoleculeInput(Exception):
    """Exception for when provided input is not valid."""

    pass


class InvalidMolset(Exception):
    """Exception for when a molset is not valid."""

    pass


class NoResult(Exception):
    """Exception for when no result can be returned."""

    pass


class FailedOperation(Exception):
    """Exception for when an operation fails to complete successfully."""

    pass


class FileAlreadyExists(Exception):
    """Exception for when a file already exists."""

    pass


class CacheFileNotFound(Exception):
    """Exception for when a cache file cannot be found."""

    pass


class MissingDependenciesViz(Exception):
    """Exception for when optional dependencies for /viz routes are not installed."""

    pass

"""Search engine exceptions."""


class SearchError(Exception):
    """Base exception for search errors."""
    pass


class InvalidQueryError(SearchError):
    """Raised when query is invalid."""
    pass


class QueryBuildError(SearchError):
    """Raised when TQL query construction fails."""
    pass


class SearchExecutionError(SearchError):
    """Raised when search execution fails."""
    pass

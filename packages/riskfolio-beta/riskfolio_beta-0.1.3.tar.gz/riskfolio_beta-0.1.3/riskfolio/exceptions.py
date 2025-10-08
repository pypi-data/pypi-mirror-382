# exceptions.py
class PortfolioValidationError(Exception):
    """Raised when portfolio dataframe fails validation."""

class MissingColumnError(Exception):
    """Raised when required columns are missing from dataframe."""
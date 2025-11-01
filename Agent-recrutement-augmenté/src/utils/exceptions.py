"""
Custom exceptions for the Agent de Recrutement Augmenté.
"""

class RecruitmentAgentException(Exception):
    """Base exception for all recruitment agent errors."""
    pass

class CVParsingException(RecruitmentAgentException):
    """Exception raised when CV parsing fails."""
    def __init__(self, filename: str, message: str = "Failed to parse CV"):
        self.filename = filename
        self.message = f"{message}: {filename}"
        super().__init__(self.message)

class EntityExtractionException(RecruitmentAgentException):
    """Exception raised when entity extraction fails."""
    pass

class RankingException(RecruitmentAgentException):
    """Exception raised when ranking process fails."""
    pass

class ConfigurationException(RecruitmentAgentException):
    """Exception raised when configuration is invalid."""
    pass

class APIException(RecruitmentAgentException):
    """Exception raised when API calls fail."""
    def __init__(self, api_name: str, message: str):
        self.api_name = api_name
        self.message = f"{api_name} API error: {message}"
        super().__init__(self.message)

class ValidationException(RecruitmentAgentException):
    """Exception raised when input validation fails."""
    pass

class FileFormatException(RecruitmentAgentException):
    """Exception raised when file format is not supported."""
    def __init__(self, filename: str, expected_formats: list):
        self.filename = filename
        self.expected_formats = expected_formats
        self.message = f"Invalid file format for {filename}. Expected: {', '.join(expected_formats)}"
        super().__init__(self.message)

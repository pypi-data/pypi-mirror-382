class DataExtractionError(Exception):
    """Custom exception for data extraction errors"""

    def __init__(self, message: str, error_type: str = "other"):
        self.message = message
        self.error_type = error_type
        super().__init__(self.message)

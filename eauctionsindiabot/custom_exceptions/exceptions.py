class DatabaseError(Exception):
    def __init__(self, message, partial_count=0):
        super().__init__(message)
        self.partial_count = partial_count
class StartScrapperError(Exception):
    def __init__(self, message, partial_count=0):
        super().__init__(message)
        self.partial_count = partial_count

class SingleScrapperError(Exception):
    def __init__(self, message, partial_count=0):
        super().__init__(message)
        self.partial_count = partial_count

class GeminiApiError(Exception):
    def __init__(self, message, partial_count=0):
        super().__init__(message)
        self.partial_count = partial_count
class TesseractOCRError(Exception):
    def __init__(self, message, partial_count=0):
        super().__init__(message)
        self.partial_count = partial_count
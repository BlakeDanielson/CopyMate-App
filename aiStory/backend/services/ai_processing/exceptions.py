class AIProcessingError(Exception):
    """
    Base exception for AI processing errors.
    """
    def __init__(self, message: str, provider_name: str = None):
        self.provider_name = provider_name
        self.message = message
        super().__init__(self.format_message())
        
    def format_message(self) -> str:
        if self.provider_name:
            return f"AI Provider '{self.provider_name}' error: {self.message}"
        return f"AI Processing error: {self.message}"


class AIProviderNotFoundError(AIProcessingError):
    """
    Exception raised when the requested AI provider is not found.
    """
    def __init__(self, provider_name: str):
        super().__init__(f"AI provider '{provider_name}' not found", provider_name)


class AIProviderConfigurationError(AIProcessingError):
    """
    Exception raised when there's a configuration error for an AI provider.
    """
    def __init__(self, provider_name: str, message: str):
        super().__init__(f"Configuration error: {message}", provider_name)


class AIProviderConnectionError(AIProcessingError):
    """
    Exception raised when there's a connection error to an AI provider service.
    """
    def __init__(self, provider_name: str, message: str):
        super().__init__(f"Connection error: {message}", provider_name)


class ImageProcessingError(AIProcessingError):
    """
    Exception raised when there's an error processing an image.
    """
    def __init__(self, provider_name: str, message: str, image_path: str = None):
        self.image_path = image_path
        msg = f"Failed to process image{f' {image_path}' if image_path else ''}: {message}"
        super().__init__(msg, provider_name)
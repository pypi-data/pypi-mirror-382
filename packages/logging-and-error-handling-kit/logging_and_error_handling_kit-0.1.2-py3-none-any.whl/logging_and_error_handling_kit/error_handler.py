from . import get_logger
import traceback
from typing import Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass

class ErrorType(Enum):
    """Enumeration of error types for better categorization"""
    VALIDATION_ERROR = "validation_error"
    API_ERROR = "api_error"
    PROCESSING_ERROR = "processing_error"
    CONFIGURATION_ERROR = "configuration_error"
    NETWORK_ERROR = "network_error"
    UNKNOWN_ERROR = "unknown_error"

@dataclass
class ServiceError:
    """Structured error information"""
    error_type: ErrorType
    message: str
    details: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    original_exception: Optional[Exception] = None

class ErrorHandler:
    """Centralized error handling and logging"""
    
    def __init__(self, logger_name: str):
        self.logger = get_logger(logger_name)
    
    def handle_error(self, 
                    error: Exception, 
                    error_type: ErrorType = ErrorType.UNKNOWN_ERROR,
                    context: Optional[Dict[str, Any]] = None,
                    user_message: Optional[str] = None) -> ServiceError:
        """
        Handle and log errors with proper categorization
        
        Args:
            error: The original exception
            error_type: Type of error for categorization
            context: Additional context information
            user_message: User-friendly error message
        
        Returns:
            ServiceError: Structured error information
        """
        
        # Create error context
        error_context = {
            "error_type": error_type.value,
            "exception_type": type(error).__name__,
            "traceback": traceback.format_exc(),
            **(context or {})
        }
        
        # Determine user-friendly message
        if user_message:
            friendly_message = user_message
        else:
            friendly_message = self._get_friendly_message(error_type, error)
        
        # Log the error with appropriate level
        if error_type in [ErrorType.VALIDATION_ERROR]:
            self.logger.warning(
                f"Validation error: {friendly_message}",
                extra={"context": error_context},
                display_on_stdout=True
            )
        elif error_type in [ErrorType.API_ERROR, ErrorType.NETWORK_ERROR]:
            self.logger.error(
                f"External service error: {friendly_message}",
                extra={"context": error_context},
                display_on_stdout=True
            )
        else:
            self.logger.error(
                f"Service error: {friendly_message}",
                extra={"context": error_context},
                exc_info=True,
                display_on_stdout=True
            )
        
        return ServiceError(
            error_type=error_type,
            message=friendly_message,
            details=str(error),
            context=error_context,
            original_exception=error
        )
    
    def _get_friendly_message(self, error_type: ErrorType, error: Exception) -> str:
        """Generate user-friendly error messages"""
        
        error_messages = {
            ErrorType.VALIDATION_ERROR: "Invalid input provided",
            ErrorType.API_ERROR: "External service temporarily unavailable",
            ErrorType.PROCESSING_ERROR: "Error processing your request",
            ErrorType.CONFIGURATION_ERROR: "Service configuration error",
            ErrorType.NETWORK_ERROR: "Network connectivity issue",
            ErrorType.UNKNOWN_ERROR: "An unexpected error occurred"
        }
        
        return error_messages.get(error_type, "An unexpected error occurred")
    
    def log_info(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log informational message with context"""
        self.logger.info(message, extra={"context": context or {}}, display_on_stdout=True)
        
    def log_warning(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log warning message with context"""
        self.logger.warning(message, extra={"context": context or {}}, display_on_stdout=True)
    
    def log_debug(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log debug message with context"""
        self.logger.debug(message, extra={"context": context or {}}, display_on_stdout=True)
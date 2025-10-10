"""
Base Lambda handler with common functionality.

Provides a foundation for creating Lambda handlers with standardized
request/response handling, error management, and service injection.
"""

import json
from typing import Dict, Any, Callable, Optional, Type, TypeVar
from aws_lambda_powertools import Logger

from geek_cafe_services.utilities.response import (
    error_response,
    service_result_to_response,
)
from geek_cafe_services.utilities.lambda_event_utility import LambdaEventUtility
from geek_cafe_services.middleware import handle_cors, handle_errors
from geek_cafe_services.middleware.auth import extract_user_context
from .service_pool import ServicePool

logger = Logger()

T = TypeVar('T')  # Service type


class BaseLambdaHandler:
    """
    Base class for Lambda handlers with common functionality.
    
    Handles:
    - Request body parsing and case conversion
    - Service initialization and pooling
    - User context extraction
    - Response formatting
    - Event unwrapping (SQS, SNS, etc.)
    
    Subclasses should implement security/validation logic.
    """
    
    def __init__(
        self,
        service_class: Optional[Type[T]] = None,
        require_body: bool = True,
        convert_case: bool = True,
        unwrap_message: bool = True,
        apply_cors: bool = True,
        apply_error_handling: bool = True,
    ):
        """
        Initialize the handler.
        
        Args:
            service_class: Service class to instantiate (optional)
            require_body: Whether request body is required
            convert_case: Whether to convert camelCase to snake_case
            unwrap_message: Whether to unwrap message events (SQS/SNS)
            apply_cors: Whether to apply CORS headers
            apply_error_handling: Whether to apply error handling decorator
        """
        self.service_class = service_class
        self.require_body = require_body
        self.convert_case = convert_case
        self.unwrap_message = unwrap_message
        self.apply_cors = apply_cors
        self.apply_error_handling = apply_error_handling
        
        # Initialize service pool if service class provided
        self._service_pool: Optional[ServicePool] = None
        if service_class:
            self._service_pool = ServicePool(service_class)
    
    def execute(
        self,
        event: Dict[str, Any],
        context: Any,
        business_logic: Callable[[Dict[str, Any], Any, Dict[str, str]], Any],
        injected_service: Optional[T] = None,
    ) -> Dict[str, Any]:
        """
        Execute the Lambda handler with business logic.
        
        Args:
            event: Lambda event
            context: Lambda context
            business_logic: Function containing business logic
                Signature: (event, service, user_context) -> result
            injected_service: Service instance for testing (optional)
            
        Returns:
            Lambda response dict
        """
        # Apply decorators if configured
        handler_func = self._execute_internal
        if self.apply_cors:
            handler_func = handle_cors(handler_func)
        if self.apply_error_handling:
            handler_func = handle_errors(handler_func)
        
        return handler_func(event, context, business_logic, injected_service)
    
    def _execute_internal(
        self,
        event: Dict[str, Any],
        context: Any,
        business_logic: Callable,
        injected_service: Optional[T] = None,
    ) -> Dict[str, Any]:
        """Internal execution logic (before decorators)."""
        
        # Unwrap message events (SQS, SNS, etc.)
        if self.unwrap_message and "message" in event:
            event = event["message"]
        
        # Validate security (implemented by subclasses)
        security_check = self._validate_security(event)
        if security_check:
            return security_check
        
        # Extract user context
        user_context = extract_user_context(event)
        
        # Parse request body
        body = None
        if self.require_body or event.get("body"):
            body = LambdaEventUtility.get_body_from_event(event)
            if self.require_body and not body:
                return error_response("Request body is required", 400)
        
        # Convert case if needed
        if body and self.convert_case:
            backend_payload = LambdaEventUtility.to_snake_case_for_backend(body)
            event["parsed_body"] = backend_payload
        elif body:
            event["parsed_body"] = body
        
        # Get service instance
        service = self._get_service(injected_service)
        
        # Execute business logic
        try:
            result = business_logic(event, service, user_context)
            
            # Handle different return types
            if isinstance(result, dict):
                # Check if it's already a formatted response
                if "statusCode" in result:
                    return result
                # Otherwise wrap it as data
                return {
                    "statusCode": 200,
                    "body": json.dumps({"data": result}),
                    "headers": {"Content-Type": "application/json"}
                }
            elif hasattr(result, "success"):
                # ServiceResult object
                return service_result_to_response(result, success_status=200)
            else:
                # Raw response
                return {
                    "statusCode": 200,
                    "body": json.dumps({"data": result}),
                    "headers": {"Content-Type": "application/json"}
                }
                
        except Exception as e:
            logger.exception("Error in business logic")
            return error_response(str(e), 500)
    
    def _validate_security(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Validate security requirements.
        
        Override in subclasses for specific security logic.
        
        Returns:
            Error response if validation fails, None if valid
        """
        return None
    
    def _get_service(self, injected_service: Optional[T]) -> Optional[T]:
        """
        Get service instance (injected or from pool).
        
        Args:
            injected_service: Injected service for testing
            
        Returns:
            Service instance or None
        """
        if injected_service:
            return injected_service
        
        if self._service_pool:
            return self._service_pool.get()
        
        return None

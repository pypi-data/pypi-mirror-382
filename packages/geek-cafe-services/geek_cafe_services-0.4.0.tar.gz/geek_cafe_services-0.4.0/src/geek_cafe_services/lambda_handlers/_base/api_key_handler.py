"""
Lambda handler with API key validation.

Implements the API key validation pattern used across the application.
"""

import os
from typing import Dict, Any, Optional
from aws_lambda_powertools import Logger

from geek_cafe_services.utilities.response import error_response
from geek_cafe_services.utilities.lambda_event_utility import LambdaEventUtility
from .base_handler import BaseLambdaHandler

logger = Logger()


class ApiKeyLambdaHandler(BaseLambdaHandler):
    """
    Lambda handler with API key validation.
    
    Validates that requests include a valid API key in the x-api-key header.
    The expected API key is read from the API_KEY environment variable.
    
    Example:
        handler = ApiKeyLambdaHandler(
            service_class=VoteService,
            require_body=True
        )
        
        def lambda_handler(event, context):
            return handler.execute(event, context, process_vote)
        
        def process_vote(event, service, user_context):
            payload = event["parsed_body"]
            return service.create_vote(...)
    """
    
    def __init__(
        self,
        api_key_env_var: str = "API_KEY",
        api_key_header: str = "x-api-key",
        **kwargs
    ):
        """
        Initialize the API key handler.
        
        Args:
            api_key_env_var: Environment variable name for API key
            api_key_header: Header name to check for API key
            **kwargs: Arguments passed to BaseLambdaHandler
        """
        super().__init__(**kwargs)
        self.api_key_env_var = api_key_env_var
        self.api_key_header = api_key_header
    
    def _validate_security(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Validate API key is present and correct.
        
        Returns:
            Error response if validation fails, None if valid
        """
        # Check if API key is configured
        if not self._is_key_set():
            return error_response(
                "API key not found. System is not configured to accept "
                "requests without an API key. Set API_KEY environment variable.",
                "UNAUTHORIZED",
                401,
            )
        
        # Validate the provided API key
        if not self._is_valid_api_key(event):
            return error_response("Invalid API key", "UNAUTHORIZED", 401)
        
        return None
    
    def _is_key_set(self) -> bool:
        """
        Check if API key environment variable is set.
        
        Returns:
            True if API key is configured
        """
        expected_api_key = os.getenv(self.api_key_env_var)
        if not expected_api_key:
            logger.error(
                f"API key not found. Set {self.api_key_env_var} environment variable."
            )
            return False
        return True
    
    def _is_valid_api_key(self, event: Dict[str, Any]) -> bool:
        """
        Validate the API key from the request.
        
        Args:
            event: Lambda event
            
        Returns:
            True if API key is valid
        """
        expected_api_key = os.getenv(self.api_key_env_var)
        if not expected_api_key:
            logger.error(
                f"API key not found. Set {self.api_key_env_var} environment variable."
            )
            return False
        
        # Get the key from headers
        provided_api_key = LambdaEventUtility.get_value_from_header(
            event, self.api_key_header
        )
        if not provided_api_key:
            logger.error(f"No API key provided in {self.api_key_header} header")
            return False
        
        valid = provided_api_key == expected_api_key
        if not valid:
            logger.error("Invalid API key provided")
        return valid

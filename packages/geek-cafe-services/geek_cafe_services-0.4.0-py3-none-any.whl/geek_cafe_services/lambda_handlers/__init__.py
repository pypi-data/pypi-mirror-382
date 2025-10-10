"""
Lambda handler wrappers for reducing boilerplate in AWS Lambda functions.

This module provides a flexible, composable system for creating Lambda handlers
with built-in support for:
- API key validation
- Request/response transformation
- Service initialization and pooling
- Error handling and CORS
- User context extraction

Example Usage:
    from geek_cafe_services.lambda_handlers import ApiKeyLambdaHandler
    from geek_cafe_services.services.vote_service import VoteService
    
    # Create handler with service pooling
    handler = ApiKeyLambdaHandler(
        service_class=VoteService,
        require_body=True,
        convert_case=True
    )
    
    def lambda_handler(event, context):
        return handler.execute(event, context, business_logic)
    
    def business_logic(event, service, user_context):
        # Your business logic here - all boilerplate handled
        payload = event["parsed_body"]
        return service.create_vote(...)
"""

from ._base.base_handler import BaseLambdaHandler
from ._base.api_key_handler import ApiKeyLambdaHandler
from ._base.public_handler import PublicLambdaHandler
from ._base.service_pool import ServicePool

__all__ = [
    "BaseLambdaHandler",
    "ApiKeyLambdaHandler", 
    "PublicLambdaHandler",
    "ServicePool",
]

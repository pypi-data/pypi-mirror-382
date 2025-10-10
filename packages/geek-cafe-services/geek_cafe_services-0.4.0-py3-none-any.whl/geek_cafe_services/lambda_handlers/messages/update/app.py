# src/geek_cafe_services/lambda_handlers/messages/update/app.py

import json
from typing import Dict, Any

from geek_cafe_services.services import MessageThreadService
from geek_cafe_services.lambda_handlers import ServicePool
from geek_cafe_services.utilities.response import service_result_to_response, error_response
from geek_cafe_services.utilities.lambda_event_utility import LambdaEventUtility

message_service_pool = ServicePool(MessageThreadService)

def handler(event: Dict[str, Any], context: object, injected_services=None) -> Dict[str, Any]:
    """
    Lambda handler for updating an existing message thread.
    
    Args:
        event: API Gateway event
        context: Lambda context
        injected_services: Optional MessageThreadService for testing
    """
    try:
        message_service = injected_services if injected_services else message_service_pool.get()
        body = LambdaEventUtility.get_body_from_event(event)
        user_id = LambdaEventUtility.get_authenticated_user_id(event)
        tenant_id = LambdaEventUtility.get_authenticated_user_tenant_id(event)
        resource_id = LambdaEventUtility.get_value_from_path_parameters(event, 'id')

        if not resource_id:
            return error_response("Message thread ID is required in the path.", "VALIDATION_ERROR", 400)

        result = message_service.update(
            resource_id=resource_id,
            tenant_id=tenant_id,
            user_id=user_id,
            updates=body
        )

        return service_result_to_response(result)

    except json.JSONDecodeError:
        return error_response("Invalid JSON in request body.", "VALIDATION_ERROR", 400)
    except Exception as e:
        return error_response(f"An unexpected error occurred: {str(e)}", "INTERNAL_ERROR", 500)

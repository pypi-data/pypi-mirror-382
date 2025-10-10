# src/geek_cafe_services/lambda_handlers/groups/update/app.py

import json
from typing import Dict, Any

from geek_cafe_services.services import GroupService
from geek_cafe_services.lambda_handlers import ServicePool
from geek_cafe_services.utilities.response import service_result_to_response, error_response
from geek_cafe_services.utilities.lambda_event_utility import LambdaEventUtility

group_service_pool = ServicePool(GroupService)

def handler(event: Dict[str, Any], context: object, injected_services=None) -> Dict[str, Any]:
    """
    Lambda handler for updating an existing group.
    
    Args:
        event: API Gateway event
        context: Lambda context
        injected_services: Optional GroupService for testing
    """
    try:
        group_service = injected_services if injected_services else group_service_pool.get()
        body = LambdaEventUtility.get_body_from_event(event)
        user_id = LambdaEventUtility.get_authenticated_user_id(event)
        tenant_id = LambdaEventUtility.get_authenticated_user_tenant_id(event)
        resource_id = LambdaEventUtility.get_value_from_path_parameters(event, 'id')

        if not resource_id:
            return error_response("Group ID is required in the path.", "VALIDATION_ERROR", 400)

        result = group_service.update(
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

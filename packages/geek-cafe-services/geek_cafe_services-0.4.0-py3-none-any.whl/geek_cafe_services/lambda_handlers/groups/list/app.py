# src/geek_cafe_services/lambda_handlers/groups/list/app.py

from typing import Dict, Any

from geek_cafe_services.services import GroupService
from geek_cafe_services.lambda_handlers import ServicePool
from geek_cafe_services.utilities.response import service_result_to_response, error_response
from geek_cafe_services.utilities.lambda_event_utility import LambdaEventUtility

group_service_pool = ServicePool(GroupService)

def handler(event: Dict[str, Any], context: object, injected_services=None) -> Dict[str, Any]:
    """
    Lambda handler for listing groups with optional filters.
    
    Args:
        event: API Gateway event
        context: Lambda context
        injected_services: Optional GroupService for testing
    """
    try:
        group_service = injected_services if injected_services else group_service_pool.get()
        user_id = LambdaEventUtility.get_authenticated_user_id(event)
        tenant_id = LambdaEventUtility.get_authenticated_user_tenant_id(event)
        query_params = event.get('queryStringParameters', {}) or {}

        # GroupService has list_by_tenant method
        result = group_service.list_by_tenant(
            tenant_id=tenant_id,
            user_id=user_id
        )

        return service_result_to_response(result)

    except Exception as e:
        return error_response(f"An unexpected error occurred: {str(e)}", "INTERNAL_ERROR", 500)

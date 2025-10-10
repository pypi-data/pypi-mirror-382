# src/geek_cafe_services/lambda_handlers/events/delete/app.py

from typing import Dict, Any

from geek_cafe_services.services import EventService
from geek_cafe_services.lambda_handlers import ServicePool
from geek_cafe_services.utilities.response import service_result_to_response, error_response, success_response
from geek_cafe_services.utilities.lambda_event_utility import LambdaEventUtility

event_service_pool = ServicePool(EventService)

def handler(event: Dict[str, Any], context: object, injected_services=None) -> Dict[str, Any]:
    """
    Lambda handler for deleting an event by its ID.
    
    Args:
        event: API Gateway event
        context: Lambda context
        injected_services: Optional EventService for testing
    """
    try:
        event_service = injected_services if injected_services else event_service_pool.get()
        user_id = LambdaEventUtility.get_authenticated_user_id(event)
        tenant_id = LambdaEventUtility.get_authenticated_user_tenant_id(event)
        resource_id = LambdaEventUtility.get_value_from_path_parameters(event, 'id')

        if not resource_id:
            return error_response("Event ID is required in the path.", "VALIDATION_ERROR", 400)

        result = event_service.delete(
            resource_id=resource_id,
            tenant_id=tenant_id,
            user_id=user_id
        )

        if result.success:
            return success_response(None, status_code=204)
        else:
            return service_result_to_response(result)

    except Exception as e:
        return error_response(f"An unexpected error occurred: {str(e)}", "INTERNAL_ERROR", 500)

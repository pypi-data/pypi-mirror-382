# src/geek_cafe_services/lambda_handlers/events/create/app.py

import json
from typing import Dict, Any

from geek_cafe_services.services import EventService
from geek_cafe_services.lambda_handlers import ServicePool
from geek_cafe_services.utilities.response import service_result_to_response, error_response
from geek_cafe_services.utilities.lambda_event_utility import LambdaEventUtility

event_service_pool = ServicePool(EventService)

def handler(event: Dict[str, Any], context: object, injected_services=None) -> Dict[str, Any]:
    """
    Lambda handler for creating a new event.
    
    Args:
        event: API Gateway event
        context: Lambda context
        injected_services: Optional EventService for testing
    """
    try:
        # Use injected service (testing) or pool (production)
        event_service = injected_services if injected_services else event_service_pool.get()
        body = LambdaEventUtility.get_body_from_event(event)
        user_id = LambdaEventUtility.get_authenticated_user_id(event)
        tenant_id = LambdaEventUtility.get_authenticated_user_tenant_id(event)

        # Pass all body parameters to the service
        result = event_service.create(
            tenant_id=tenant_id,
            user_id=user_id,
            **body
        )

        return service_result_to_response(result, success_status=201)

    except json.JSONDecodeError:
        return error_response("Invalid JSON format in request body.", "VALIDATION_ERROR", 400)
    except Exception as e:
        # In a production environment, log the exception e
        return error_response(f"An unexpected error occurred: {str(e)}", "INTERNAL_ERROR", 500)

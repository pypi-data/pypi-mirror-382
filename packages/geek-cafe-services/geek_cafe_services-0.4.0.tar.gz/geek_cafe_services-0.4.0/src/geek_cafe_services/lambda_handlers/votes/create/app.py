"""
Lambda handler for creating votes.

REFACTORED VERSION using ApiKeyLambdaHandler wrapper.
Reduces code from 156 lines to ~40 lines while maintaining all functionality.

Compare to: app.py (original version with boilerplate)
"""

from typing import Dict, Any
from geek_cafe_services.lambda_handlers import ApiKeyLambdaHandler
from geek_cafe_services.services.vote_service import VoteService
from geek_cafe_services.utilities.response import error_response

# ⚡ Initialize handler at module level for Lambda warm starts
# This automatically handles:
# - API key validation
# - Request body parsing
# - Case conversion (camelCase → snake_case)
# - Service pooling (connection reuse)
# - User context extraction
# - CORS headers
# - Error handling
handler = ApiKeyLambdaHandler(
    service_class=VoteService,
    require_body=True,
    convert_case=True
)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Create or update a vote.

    Expected request body:
    {
        "userId": "user_id",
        "targetId": "health-meter-ui-choice",
        "choiceId": "gauge" | "traffic_light",
        "voteType": "single_choice",
        "availableChoices": ["gauge", "traffic_light"],
        "content": {
            "description": "User preference for health meter display type",
            "metadata": {...}
        }
    }
    """
    return handler.execute(event, context, create_vote)


def create_vote(
    event: Dict[str, Any],
    service: VoteService,
    user_context: Dict[str, str]
) -> Any:
    """
    Business logic for creating a vote.
    
    All boilerplate has been handled by the wrapper:
    ✅ API key validation
    ✅ Body parsing and case conversion
    ✅ Service initialization
    ✅ User context extraction
    
    Focus purely on business logic here.
    
    Args:
        event: Enhanced event with parsed_body containing snake_case data
        service: VoteService instance (pooled for warm starts)
        user_context: Extracted user info (user_id, tenant_id, etc.)
    
    Returns:
        ServiceResult that will be formatted into Lambda response
    """
    # Get parsed and converted body (camelCase → snake_case already done)
    payload = event["parsed_body"]
    
    # Validate required fields
    target_id = payload.get("target_id")
    if not target_id:
        return error_response("target_id is required", 400)
    
    choice_id = payload.get("choice_id")
    if not choice_id:
        return error_response("choice_id is required", 400)
    
    vote_type = payload.get("vote_type", "single_choice")
    available_choices = payload.get("available_choices", [])
    content = payload.get("content", {})
    
    # Validate choice_id is in available_choices if provided
    if available_choices and choice_id not in available_choices:
        return error_response(
            f"choice_id '{choice_id}' must be one of: {available_choices}", 400
        )
    
    # Get user info from context
    tenant_id = user_context.get("tenant_id", "anonymous")
    # we will get the logged in user if there is one, or a sudo user id sent by the client
    user_id = user_context.get("user_id") or payload.get("user_id", "anonymous")
    
    # Create the vote based on type
    if vote_type == "single_choice":
        result = service.create_single_choice_vote(
            tenant_id=tenant_id,
            user_id=user_id,
            target_id=target_id,
            choice_id=choice_id,
            available_choices=available_choices if available_choices else None,
            content=content if content else None,
        )
    else:
        return error_response(f"Unsupported vote_type: {vote_type}", 400)
    
    # Return ServiceResult - handler will automatically format to Lambda response
    return result

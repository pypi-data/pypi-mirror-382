# Event Service

from typing import Dict, Any, Optional, List
from boto3_assist.dynamodb.dynamodb import DynamoDB
from .database_service import DatabaseService
from ..core.service_result import ServiceResult
from ..core.service_errors import ValidationError, NotFoundError, AccessDeniedError
from ..models.event import Event
from ..utilities.dynamodb_utils import build_projection_with_reserved_keywords
import datetime as dt


class EventService(DatabaseService[Event]):
    """Service for Event database operations."""

    def __init__(self, *, dynamodb: DynamoDB = None, table_name: str = None):
        super().__init__(dynamodb=dynamodb, table_name=table_name)

    def create(self, tenant_id: str, user_id: str, **kwargs) -> ServiceResult[Event]:
        """Create a new event."""
        try:
            # Validate required fields
            required_fields = ['title', 'date']
            self._validate_required_fields(kwargs, required_fields)

            # Validate date is in future
            event_date = kwargs.get('date')
            if not self._is_future_date(event_date):
                raise ValidationError("Event date must be in the future")

            # Create event instance using map() approach
            event = Event().map(kwargs)
            event.organizer_id = user_id  # Creator is the organizer
            event.tenant_id = tenant_id
            event.user_id = user_id
            event.created_by_id = user_id

            # Prepare for save (sets ID and timestamps)
            event.prep_for_save()

            # Save to database
            return self._save_model(event)

        except Exception as e:
            return self._handle_service_exception(e, 'create_event', tenant_id=tenant_id, user_id=user_id)

    def create_draft(self, tenant_id: str, user_id: str, **kwargs) -> ServiceResult[Event]:
        """Create a new event draft (partial data allowed)."""
        try:
            # For drafts, only title is required
            if not kwargs.get('title'):
                kwargs['title'] = f"Draft Event - {dt.datetime.now(dt.UTC).strftime('%Y-%m-%d %H:%M')}"

            # Set default date if not provided
            if not kwargs.get('date'):
                # Default to tomorrow
                tomorrow = dt.datetime.now(dt.UTC) + dt.timedelta(days=1)
                kwargs['date'] = tomorrow.isoformat()

            # Mark as draft
            kwargs['is_draft'] = True

            # Create the event
            return self.create(tenant_id, user_id, **kwargs)

        except Exception as e:
            return self._handle_service_exception(e, 'create_event_draft', tenant_id=tenant_id, user_id=user_id)

    def get_by_id(self, resource_id: str, tenant_id: str, user_id: str) -> ServiceResult[Event]:
        """Get event by ID with access control."""
        try:
            event = self._get_model_by_id(resource_id, Event)

            if not event:
                raise NotFoundError(f"Event with ID {resource_id} not found")

            # Check if deleted
            if event.is_deleted():
                raise NotFoundError(f"Event with ID {resource_id} not found")

            # Validate tenant access
            if hasattr(event, 'tenant_id'):
                self._validate_tenant_access(event.tenant_id, tenant_id)

            return ServiceResult.success_result(event)

        except Exception as e:
            return self._handle_service_exception(e, 'get_event', resource_id=resource_id, tenant_id=tenant_id)

    def get_events_by_organizer(self, organizer_id: str, tenant_id: str, user_id: str,
                               limit: int = 50) -> ServiceResult[List[Event]]:
        """Get events organized by a specific user using GSI1."""
        try:
            # Create a temporary event instance to get the GSI key
            temp_event = Event()
            temp_event.organizer_id = organizer_id

            # Query by GSI1 (events by organizer), most recent first
            projection_attrs = ["pk", "sk", "title", "date", "description", "visibility", "group_id", "invited_guests", "organizer_id", "is_draft", "tenant_id", "deleted_utc_ts"]
            projection_expression, expression_attribute_names = build_projection_with_reserved_keywords(projection_attrs)

            result = self._query_by_index(
                temp_event,
                "gsi1",
                ascending=False,  # Most recent first
                limit=limit,
                projection_expression=projection_expression,
                expression_attribute_names=expression_attribute_names
            )

            if not result.success:
                return result

            # Filter out deleted events and validate tenant access
            active_events = []
            for event in result.data:
                if not event.is_deleted() and event.tenant_id == tenant_id:
                    active_events.append(event)

            return ServiceResult.success_result(active_events)

        except Exception as e:
            return self._handle_service_exception(e, 'get_events_by_organizer',
                                                organizer_id=organizer_id, tenant_id=tenant_id)

    def get_events_by_group(self, group_id: str, tenant_id: str, user_id: str,
                           limit: int = 50) -> ServiceResult[List[Event]]:
        """Get events for a specific group using GSI2."""
        try:
            # Create a temporary event instance to get the GSI key
            temp_event = Event()
            temp_event.group_id = group_id

            # Query by GSI2 (events by group), most recent first
            projection_attrs = ["pk", "sk", "title", "date", "description", "visibility", "group_id", "invited_guests", "organizer_id", "is_draft", "tenant_id", "deleted_utc_ts"]
            projection_expression, expression_attribute_names = build_projection_with_reserved_keywords(projection_attrs)

            result = self._query_by_index(
                temp_event,
                "gsi2",
                ascending=False,  # Most recent first
                limit=limit,
                projection_expression=projection_expression,
                expression_attribute_names=expression_attribute_names
            )

            if not result.success:
                return result

            # Filter out deleted events and validate tenant access
            active_events = []
            for event in result.data:
                if not event.is_deleted() and event.tenant_id == tenant_id:
                    active_events.append(event)

            return ServiceResult.success_result(active_events)

        except Exception as e:
            return self._handle_service_exception(e, 'get_events_by_group',
                                                group_id=group_id, tenant_id=tenant_id)

    def list_by_tenant(self, tenant_id: str, user_id: str, limit: int = 50,
                       filters: Dict[str, Any] = None) -> ServiceResult[List[Event]]:
        """
        Get all events for a tenant with optional filtering using GSI3 or GSI5.

        Args:
            tenant_id: The ID of the tenant.
            user_id: The ID of the user making the request.
            limit: The maximum number of events to return.
            filters: A dictionary of filters to apply, e.g., {'visibility': 'public'}.
        """
        try:
            filters = filters or {}
            visibility_filter = filters.get('visibility')

            if visibility_filter:
                # Use GSI3 to filter by visibility
                temp_event = Event()
                temp_event.visibility = visibility_filter

                result = self._query_by_index(
                    temp_event,
                    "gsi3",
                    ascending=False,  # Most recent first
                    limit=limit
                )
            else:
                # Use GSI5 to get all events for tenant
                temp_event = Event()
                temp_event.tenant_id = tenant_id

                result = self._query_by_index(
                    temp_event,
                    "gsi5",
                    ascending=False,  # Most recent first
                    limit=limit
                )

            if not result.success:
                return result

            # Filter out deleted events and validate tenant access
            active_events = []
            for event in result.data:
                if not event.is_deleted() and event.tenant_id == tenant_id:
                    active_events.append(event)

            return ServiceResult.success_result(active_events)

        except Exception as e:
            return self._handle_service_exception(e, 'list_by_tenant', tenant_id=tenant_id)
    
    def get_upcoming_events(self, tenant_id: str, user_id: str, limit: int = 20) -> ServiceResult[List[Event]]:
        """Get upcoming events across all visibility levels using GSI4."""
        try:
            # Query GSI4 with partition key "event#date" to get all events ordered by date
            result = self._query_by_index(
                Event(),  # Create a dummy event to get GSI4 key
                "gsi4",
                ascending=True,  # Oldest events first (upcoming)
                limit=limit * 2,  # Get more to allow for filtering
            )

            if not result.success:
                return result

            # Filter for upcoming events and tenant access
            now_ts = dt.datetime.now(dt.UTC).timestamp()
            upcoming_events = []
            for event in result.data:
                if (not event.is_deleted() and 
                    event.tenant_id == tenant_id and 
                    event.event_date_timestamp > now_ts):
                    upcoming_events.append(event)
                    if len(upcoming_events) >= limit:
                        break

            return ServiceResult.success_result(upcoming_events)

        except Exception as e:
            return self._handle_service_exception(e, 'get_upcoming_events', tenant_id=tenant_id)

    def update(self, resource_id: str, tenant_id: str, user_id: str,
               updates: Dict[str, Any]) -> ServiceResult[Event]:
        """Update event with access control."""
        try:
            # Get existing event
            event = self._get_model_by_id(resource_id, Event)

            if not event:
                raise NotFoundError(f"Event with ID {resource_id} not found")

            # Validate tenant access
            if hasattr(event, 'tenant_id'):
                self._validate_tenant_access(event.tenant_id, tenant_id)

            # Check permissions (organizer or admin)
            if not (event.organizer_id == user_id or self._is_admin_user(user_id, tenant_id)):
                raise AccessDeniedError("Access denied: insufficient permissions")

            # Validate date if being updated
            if 'date' in updates:
                if not self._is_future_date(updates['date']):
                    raise ValidationError("Event date must be in the future")

            # Prevent changing group_id after creation
            if 'group_id' in updates and event.group_id and updates['group_id'] != event.group_id:
                raise ValidationError("Cannot change group association after creation")

            # Apply updates
            for field, value in updates.items():
                if hasattr(event, field) and field not in ['id', 'created_utc_ts', 'tenant_id', 'organizer_id']:
                    if field == 'title':
                        event.title = value
                    elif field == 'date':
                        event.date = value
                    elif field == 'description':
                        event.description = value
                    elif field == 'visibility':
                        event.visibility = value
                    elif field == 'invited_guests':
                        event.invited_guests = value
                    elif field == 'is_draft':
                        event.is_draft = value

            # Update metadata
            event.updated_by_id = user_id
            event.prep_for_save()  # Updates timestamp

            # Save updated event
            return self._save_model(event)

        except Exception as e:
            return self._handle_service_exception(e, 'update_event', resource_id=resource_id, tenant_id=tenant_id)

    def delete(self, resource_id: str, tenant_id: str, user_id: str) -> ServiceResult[bool]:
        """Soft delete event with access control."""
        try:
            # Get existing event
            event = self._get_model_by_id(resource_id, Event)

            if not event:
                raise NotFoundError(f"Event with ID {resource_id} not found")

            # Check if already deleted
            if event.is_deleted():
                return ServiceResult.success_result(True)

            # Validate tenant access
            if hasattr(event, 'tenant_id'):
                self._validate_tenant_access(event.tenant_id, tenant_id)

            # Check permissions (organizer or admin)
            if not (event.organizer_id == user_id or self._is_admin_user(user_id, tenant_id)):
                raise AccessDeniedError("Access denied: insufficient permissions")

            # Soft delete: set deleted timestamp and metadata
            event.deleted_utc_ts = dt.datetime.now(dt.UTC).timestamp()
            event.deleted_by_id = user_id
            event.prep_for_save()  # Updates timestamp

            # Save the updated event
            save_result = self._save_model(event)
            if save_result.success:
                return ServiceResult.success_result(True)
            else:
                return save_result

        except Exception as e:
            return self._handle_service_exception(e, 'delete_event', resource_id=resource_id, tenant_id=tenant_id)

    def _is_future_date(self, date_str: str) -> bool:
        """Check if the provided date string is in the future."""
        try:
            event_dt = dt.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            now = dt.datetime.now(dt.UTC)
            # Allow events up to 1 year in the future
            max_future = now + dt.timedelta(days=365)
            return now <= event_dt <= max_future
        except:
            return False

    def _is_admin_user(self, user_id: str, tenant_id: str) -> bool:
        """Check if user has admin role (placeholder - will be implemented when UserService is available)."""
        # For now, assume no admin privileges
        # This will be enhanced when we have user service integration
        return False

# Message Thread Service

from typing import Dict, Any, Optional, List
from boto3_assist.dynamodb.dynamodb import DynamoDB
from .database_service import DatabaseService
from ..core.service_result import ServiceResult
from ..core.service_errors import ValidationError, NotFoundError, AccessDeniedError
from ..models.message_thread import MessageThread
import datetime as dt


class MessageThreadService(DatabaseService[MessageThread]):
    """Service for MessageThread database operations."""

    def __init__(self, *, dynamodb: DynamoDB = None, table_name: str = None):
        super().__init__(dynamodb=dynamodb, table_name=table_name)

    def create(self, tenant_id: str, user_id: str, **kwargs) -> ServiceResult[MessageThread]:
        """Create a new message thread."""
        try:
            # Validate required fields
            required_fields = ['subject', 'participants']
            self._validate_required_fields(kwargs, required_fields)

            # Validate participants
            participants = kwargs.get('participants', [])
            if not participants or not isinstance(participants, list):
                raise ValidationError("At least one participant is required")

            # Ensure creator is a participant
            if not any(p.get('id') == user_id for p in participants):
                raise ValidationError("Thread creator must be a participant")

            # Create thread instance
            thread = MessageThread().map(kwargs)            
            thread.tenant_id = tenant_id
            thread.user_id = user_id
            thread.created_by_id = user_id

            # Prepare for save (sets ID and timestamps)
            thread.prep_for_save()

            # Save to database
            return self._save_model(thread)

        except Exception as e:
            return self._handle_service_exception(e, 'create_thread', tenant_id=tenant_id, user_id=user_id)

    def get_by_id(self, resource_id: str, tenant_id: str, user_id: str) -> ServiceResult[MessageThread]:
        """Get thread by ID with access control."""
        try:
            thread = self._get_model_by_id(resource_id, MessageThread)

            if not thread:
                raise NotFoundError(f"Thread with ID {resource_id} not found")

            # Check if deleted
            if thread.is_deleted():
                raise NotFoundError(f"Thread with ID {resource_id} not found")

            # Validate tenant access
            if hasattr(thread, 'tenant_id'):
                self._validate_tenant_access(thread.tenant_id, tenant_id)

            # Check if user can access this thread
            if not thread.can_user_access(user_id):
                raise AccessDeniedError("Access denied to this thread")

            return ServiceResult.success_result(thread)

        except Exception as e:
            return self._handle_service_exception(e, 'get_thread', resource_id=resource_id, tenant_id=tenant_id)

    def get_threads_by_event(self, event_id: str, tenant_id: str, user_id: str,
                            limit: int = 50) -> ServiceResult[List[MessageThread]]:
        """Get threads associated with an event using GSI1."""
        try:
            # Create a temporary thread instance to get the GSI key
            temp_thread = MessageThread().map({"event_id": event_id})

            # Query by GSI1 (threads by event), most recent first
            result = self._query_by_index(
                temp_thread,
                "gsi1",
                ascending=False,  # Most recent first
                limit=limit
            )

            if not result.success:
                return result

            # Filter out deleted threads and validate tenant access
            active_threads = []
            for thread in result.data:
                if (not thread.is_deleted() and 
                    thread.tenant_id == tenant_id and 
                    thread.can_user_access(user_id)):
                    active_threads.append(thread)

            return ServiceResult.success_result(active_threads)

        except Exception as e:
            return self._handle_service_exception(e, 'get_threads_by_event',
                                                event_id=event_id, tenant_id=tenant_id)

    def get_threads_by_type(self, thread_type: str, tenant_id: str, user_id: str,
                           limit: int = 50) -> ServiceResult[List[MessageThread]]:
        """Get threads by type using GSI2."""
        try:
            # Create a temporary thread instance to get the GSI key
            temp_thread = MessageThread()
            temp_thread.type = thread_type

            # Query by GSI2 (threads by type), most recent first
            result = self._query_by_index(
                temp_thread,
                "gsi2",
                ascending=False,  # Most recent first
                limit=limit
            )

            if not result.success:
                return result

            # Filter out deleted threads and validate tenant access
            active_threads = []
            for thread in result.data:
                if (not thread.is_deleted() and 
                    thread.tenant_id == tenant_id and 
                    thread.can_user_access(user_id)):
                    active_threads.append(thread)

            return ServiceResult.success_result(active_threads)

        except Exception as e:
            return self._handle_service_exception(e, 'get_threads_by_type',
                                                thread_type=thread_type, tenant_id=tenant_id)

    def get_user_threads(self, user_id: str, tenant_id: str, limit: int = 50) -> ServiceResult[List[MessageThread]]:
        """Get all threads where user is a participant."""
        try:
            # This is complex - we need to find all threads where user is participant
            # For now, we'll query all threads for the tenant and filter
            # In production, we'd want a GSI for user->threads

            all_threads_result = self.get_all_threads(tenant_id, user_id, limit=limit*3)

            if not all_threads_result.success:
                return all_threads_result

            user_threads = [
                thread for thread in all_threads_result.data
                if thread.is_user_participant(user_id)
            ][:limit]

            return ServiceResult.success_result(user_threads)

        except Exception as e:
            return self._handle_service_exception(e, 'get_user_threads',
                                                user_id=user_id, tenant_id=tenant_id)

    def get_all_threads(self, tenant_id: str, user_id: str, limit: int = 50) -> ServiceResult[List[MessageThread]]:
        """Get all threads for a tenant using GSI3."""
        try:
            # Create a temporary thread instance to get the GSI key
            temp_thread = MessageThread()
            temp_thread.tenant_id = tenant_id

            # Query by GSI3 (threads by tenant), most recent first
            result = self._query_by_index(
                temp_thread,
                "gsi3",
                ascending=False,  # Most recent first
                limit=limit
            )

            if not result.success:
                return result

            # Filter out deleted threads and validate user access
            active_threads = []
            for thread in result.data:
                if not thread.is_deleted() and thread.can_user_access(user_id):
                    active_threads.append(thread)

            return ServiceResult.success_result(active_threads)

        except Exception as e:
            return self._handle_service_exception(e, 'get_all_threads', tenant_id=tenant_id)

    def add_message_to_thread(self, thread_id: str, tenant_id: str, user_id: str,
                             message_data: Dict[str, Any]) -> ServiceResult[MessageThread]:
        """Add a message to an existing thread."""
        try:
            # Get the thread
            thread_result = self.get_by_id(thread_id, tenant_id, user_id)
            if not thread_result.success:
                return thread_result

            thread = thread_result.data

            # Validate user can post to this thread
            if not thread.can_user_access(user_id):
                raise AccessDeniedError("Cannot post to this thread")

            # Add the message
            message = {
                "id": message_data.get("id", f"msg_{dt.datetime.now(dt.UTC).timestamp()}"),
                "content": message_data.get("content", ""),
                "sender": {
                    "id": user_id,
                    "name": message_data.get("sender_name", ""),
                    "avatar": message_data.get("sender_avatar", ""),
                    "role": message_data.get("sender_role", "user")
                },
                "created_at": dt.datetime.now(dt.UTC).timestamp(),
                "type": message_data.get("type", "general")
            }

            thread.add_message(message)

            # Save the updated thread
            return self._save_model(thread)

        except Exception as e:
            return self._handle_service_exception(e, 'add_message_to_thread',
                                                thread_id=thread_id, tenant_id=tenant_id)

    def mark_thread_read(self, thread_id: str, tenant_id: str, user_id: str) -> ServiceResult[bool]:
        """Mark a thread as read for a user."""
        try:
            # Get the thread
            thread_result = self.get_by_id(thread_id, tenant_id, user_id)
            if not thread_result.success:
                return ServiceResult(success=False, error=thread_result.error)

            thread = thread_result.data

            # TODO: Implement read status tracking
            # For now, just return success
            return ServiceResult.success_result(True)

        except Exception as e:
            return self._handle_service_exception(e, 'mark_thread_read',
                                                thread_id=thread_id, tenant_id=tenant_id)

    def update(self, resource_id: str, tenant_id: str, user_id: str,
               updates: Dict[str, Any]) -> ServiceResult[MessageThread]:
        """Update thread with access control."""
        try:
            # Get existing thread
            thread = self._get_model_by_id(resource_id, MessageThread)

            if not thread:
                raise NotFoundError(f"Thread with ID {resource_id} not found")

            # Validate tenant access
            if hasattr(thread, 'tenant_id'):
                self._validate_tenant_access(thread.tenant_id, tenant_id)

            # Check permissions (participant only for basic updates)
            if not thread.can_user_access(user_id):
                raise AccessDeniedError("Access denied: insufficient permissions")

            # Apply updates (limited for regular participants)
            for field, value in updates.items():
                if hasattr(thread, field) and field not in ['id', 'created_utc_ts', 'tenant_id']:
                    if field == 'subject':
                        thread.subject = value
                    elif field == 'participants':
                        thread.participants = value

            # Update metadata
            thread.updated_by_id = user_id
            thread.prep_for_save()  # Updates timestamp

            # Save updated thread
            return self._save_model(thread)

        except Exception as e:
            return self._handle_service_exception(e, 'update_thread', resource_id=resource_id, tenant_id=tenant_id)

    def archive(self, resource_id: str, tenant_id: str, user_id: str) -> ServiceResult[MessageThread]:
        """Archive a message thread."""
        try:
            return self._set_archived_status(resource_id, tenant_id, user_id, is_archived=True)
        except Exception as e:
            return self._handle_service_exception(e, 'archive_thread', resource_id=resource_id, tenant_id=tenant_id)

    def unarchive(self, resource_id: str, tenant_id: str, user_id: str) -> ServiceResult[MessageThread]:
        """Unarchive a message thread."""
        try:
            return self._set_archived_status(resource_id, tenant_id, user_id, is_archived=False)
        except Exception as e:
            return self._handle_service_exception(e, 'unarchive_thread', resource_id=resource_id, tenant_id=tenant_id)

    def list_by_archived_status(self, tenant_id: str, is_archived: bool, ascending: bool = False) -> ServiceResult[list[MessageThread]]:
        """List message threads by archived status."""
        try:
            model = MessageThread()
            model.tenant_id = tenant_id
            model.is_archived = is_archived
            return self._query_by_index(model, "gsi5", ascending=ascending)
        except Exception as e:
            return self._handle_service_exception(e, 'list_threads_by_archived_status', tenant_id=tenant_id)

    def _set_archived_status(self, resource_id: str, tenant_id: str, user_id: str, is_archived: bool) -> ServiceResult[MessageThread]:
        """Set the archived status of a message thread."""
        thread_result = self.get_by_id(resource_id, tenant_id, user_id)
        if not thread_result.success:
            return thread_result

        thread = thread_result.data
        thread.is_archived = is_archived
        thread.updated_by_id = user_id
        thread.prep_for_save()

        return self._save_model(thread)

    def delete(self, resource_id: str, tenant_id: str, user_id: str) -> ServiceResult[bool]:
        """Soft delete thread with access control."""
        try:
            # Get existing thread
            thread = self._get_model_by_id(resource_id, MessageThread)

            if not thread:
                raise NotFoundError(f"Thread with ID {resource_id} not found")

            # Check if already deleted
            if thread.is_deleted():
                return ServiceResult.success_result(True)

            # Validate tenant access
            if hasattr(thread, 'tenant_id'):
                self._validate_tenant_access(thread.tenant_id, tenant_id)

            # For now, allow any participant to delete
            # In production, might want more restrictive permissions
            if not thread.can_user_access(user_id):
                raise AccessDeniedError("Access denied: insufficient permissions")

            # Soft delete: set deleted timestamp and metadata
            thread.deleted_utc_ts = dt.datetime.now(dt.UTC).timestamp()
            thread.deleted_by_id = user_id
            thread.prep_for_save()  # Updates timestamp

            # Save the updated thread
            save_result = self._save_model(thread)
            if save_result.success:
                return ServiceResult.success_result(True)
            else:
                return save_result

        except Exception as e:
            return self._handle_service_exception(e, 'delete_thread', resource_id=resource_id, tenant_id=tenant_id)

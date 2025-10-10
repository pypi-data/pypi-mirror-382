# Group Service

from typing import Dict, Any, Optional, List
from boto3_assist.dynamodb.dynamodb import DynamoDB
from .database_service import DatabaseService
from ..core.service_result import ServiceResult
from ..core.service_errors import ValidationError, NotFoundError, AccessDeniedError
from ..models.group import Group
import datetime as dt


class GroupService(DatabaseService[Group]):
    """Service for Group database operations."""

    def __init__(self, *, dynamodb: DynamoDB = None, table_name: str = None):
        super().__init__(dynamodb=dynamodb, table_name=table_name)

    def create(self, tenant_id: str, user_id: str, **kwargs) -> ServiceResult[Group]:
        """Create a new group."""
        try:
            # Validate required fields
            required_fields = ['name', 'description', 'category']
            self._validate_required_fields(kwargs, required_fields)

            # Validate group name uniqueness per user
            if self._group_name_exists_for_user(kwargs['name'], user_id, tenant_id):
                raise ValidationError("Group name already exists for this user")

            # Validate category
            if not self._is_valid_category(kwargs['category']):
                raise ValidationError("Invalid category")

            # Create group instance using map() approach
            group = Group().map(kwargs)
            group.owner_id = user_id  # Creator is the owner
            group.members = [user_id]  # Owner is automatically a member
            group.tenant_id = tenant_id
            group.user_id = user_id
            group.created_by_id = user_id

            # Prepare for save (sets ID and timestamps)
            group.prep_for_save()

            # Save to database
            return self._save_model(group)

        except Exception as e:
            return self._handle_service_exception(e, 'create_group', tenant_id=tenant_id, user_id=user_id)

    def get_by_id(self, resource_id: str, tenant_id: str, user_id: str) -> ServiceResult[Group]:
        """Get group by ID with access control."""
        try:
            group = self._get_model_by_id(resource_id, Group)

            if not group:
                raise NotFoundError(f"Group with ID {resource_id} not found")

            # Check if deleted
            if group.is_deleted():
                raise NotFoundError(f"Group with ID {resource_id} not found")

            # Validate tenant access
            if hasattr(group, 'tenant_id'):
                self._validate_tenant_access(group.tenant_id, tenant_id)

            return ServiceResult.success_result(group)

        except Exception as e:
            return self._handle_service_exception(e, 'get_group', resource_id=resource_id, tenant_id=tenant_id)

    def get_groups_by_owner(self, owner_id: str, tenant_id: str, user_id: str,
                           limit: int = 50) -> ServiceResult[List[Group]]:
        """Get groups owned by a specific user using GSI1."""
        try:
            # Create a temporary group instance to get the GSI key
            temp_group = Group()
            temp_group.owner_id = owner_id

            # Query by GSI1 (groups by owner), most recent first
            result = self._query_by_index(
                temp_group,
                "gsi1",
                ascending=False,  # Most recent first
                limit=limit
            )

            if not result.success:
                return result

            # Filter out deleted groups and validate tenant access
            active_groups = []
            for group in result.data:
                if not group.is_deleted() and group.tenant_id == tenant_id:
                    active_groups.append(group)

            return ServiceResult.success_result(active_groups)

        except Exception as e:
            return self._handle_service_exception(e, 'get_groups_by_owner',
                                                owner_id=owner_id, tenant_id=tenant_id)

    def get_groups_by_member(self, member_id: str, tenant_id: str, user_id: str,
                            limit: int = 50) -> ServiceResult[List[Group]]:
        """Get groups where a user is a member."""
        try:
            # This is more complex - we'd need a GSI that indexes membership
            # For now, we'll query all groups and filter client-side
            # In production, we'd want a GSI for user->groups membership

            all_groups_result = self.get_all_groups(tenant_id, user_id, limit=limit*2)

            if not all_groups_result.success:
                return all_groups_result

            member_groups = [
                group for group in all_groups_result.data
                if group.is_user_member(member_id)
            ][:limit]

            return ServiceResult.success_result(member_groups)

        except Exception as e:
            return self._handle_service_exception(e, 'get_groups_by_member',
                                                member_id=member_id, tenant_id=tenant_id)

    def get_groups_by_privacy(self, privacy: str, tenant_id: str, user_id: str,
                             limit: int = 50) -> ServiceResult[List[Group]]:
        """Get groups by privacy level using GSI2."""
        try:
            # Create a temporary group instance to get the GSI key
            temp_group = Group()
            temp_group.privacy = privacy

            # Query by GSI2 (groups by privacy), most recent first
            result = self._query_by_index(
                temp_group,
                "gsi2",
                ascending=False,  # Most recent first
                limit=limit
            )

            if not result.success:
                return result

            # Filter out deleted groups and validate tenant access
            active_groups = []
            for group in result.data:
                if not group.is_deleted() and group.tenant_id == tenant_id:
                    active_groups.append(group)

            return ServiceResult.success_result(active_groups)

        except Exception as e:
            return self._handle_service_exception(e, 'get_groups_by_privacy',
                                                privacy=privacy, tenant_id=tenant_id)

    def get_all_groups(self, tenant_id: str, user_id: str, limit: int = 50) -> ServiceResult[List[Group]]:
        """Get all groups for a tenant using GSI4."""
        try:
            # Create a temporary group instance to get the GSI key
            temp_group = Group()
            temp_group.tenant_id = tenant_id

            # Query by GSI4 (groups by tenant), most recent first
            result = self._query_by_index(
                temp_group,
                "gsi4",
                ascending=False,  # Most recent first
                limit=limit
            )

            if not result.success:
                return result

            # Filter out deleted groups
            active_groups = []
            for group in result.data:
                if not group.is_deleted():
                    active_groups.append(group)

            return ServiceResult.success_result(active_groups)

        except Exception as e:
            return self._handle_service_exception(e, 'get_all_groups', tenant_id=tenant_id)

    def get_groups_by_category(self, category: str, tenant_id: str, user_id: str,
                              limit: int = 50) -> ServiceResult[List[Group]]:
        """Get groups by category using GSI3."""
        try:
            # Create a temporary group instance to get the GSI key
            temp_group = Group()
            temp_group.category = category

            # Query by GSI3 (groups by category), most recent first
            result = self._query_by_index(
                temp_group,
                "gsi3",
                ascending=False,  # Most recent first
                limit=limit
            )

            if not result.success:
                return result

            # Filter out deleted groups and validate tenant access
            active_groups = []
            for group in result.data:
                if not group.is_deleted() and group.tenant_id == tenant_id:
                    active_groups.append(group)

            return ServiceResult.success_result(active_groups)

        except Exception as e:
            return self._handle_service_exception(e, 'get_groups_by_category',
                                                category=category, tenant_id=tenant_id)

    def update(self, resource_id: str, tenant_id: str, user_id: str,
               updates: Dict[str, Any]) -> ServiceResult[Group]:
        """Update group with access control."""
        try:
            # Get existing group
            group = self._get_model_by_id(resource_id, Group)

            if not group:
                raise NotFoundError(f"Group with ID {resource_id} not found")

            # Validate tenant access
            if hasattr(group, 'tenant_id'):
                self._validate_tenant_access(group.tenant_id, tenant_id)

            # Check permissions (organizers only)
            if not group.can_user_manage(user_id):
                raise AccessDeniedError("Access denied: insufficient permissions")

            # Cannot change owner
            if 'owner_id' in updates:
                raise ValidationError("Cannot change group owner")

            # Validate category if being updated
            if 'category' in updates and not self._is_valid_category(updates['category']):
                raise ValidationError("Invalid category")

            # Validate group name uniqueness if being updated
            if 'name' in updates:
                existing_group = self._get_group_by_name_and_owner(updates['name'], group.owner_id, tenant_id)
                if existing_group and existing_group.id != resource_id:
                    raise ValidationError("Group name already exists for this user")

            # Apply updates
            for field, value in updates.items():
                if hasattr(group, field) and field not in ['id', 'created_utc_ts', 'tenant_id', 'owner_id']:
                    if field == 'name':
                        group.name = value
                    elif field == 'description':
                        group.description = value
                    elif field == 'category':
                        group.category = value
                    elif field == 'privacy':
                        group.privacy = value
                    elif field == 'tags':
                        group.tags = value
                    elif field == 'joinApproval':
                        group.join_approval = value
                    elif field == 'requiresDues':
                        group.requires_dues = value
                    elif field == 'duesMonthly':
                        group.dues_monthly = value
                    elif field == 'duesYearly':
                        group.dues_yearly = value
                    elif field == 'co_owners':
                        group.co_owners = value
                    elif field == 'moderators':
                        group.moderators = value
                    elif field == 'members':
                        group.members = value

            # Update metadata
            group.updated_by_id = user_id
            group.prep_for_save()  # Updates timestamp

            # Save updated group
            return self._save_model(group)

        except Exception as e:
            return self._handle_service_exception(e, 'update_group', resource_id=resource_id, tenant_id=tenant_id)

    def delete(self, resource_id: str, tenant_id: str, user_id: str) -> ServiceResult[bool]:
        """Soft delete group with access control."""
        try:
            # Get existing group
            group = self._get_model_by_id(resource_id, Group)

            if not group:
                raise NotFoundError(f"Group with ID {resource_id} not found")

            # Check if already deleted
            if group.is_deleted():
                return ServiceResult.success_result(True)

            # Validate tenant access
            if hasattr(group, 'tenant_id'):
                self._validate_tenant_access(group.tenant_id, tenant_id)

            # Check permissions (owner only)
            if group.owner_id != user_id:
                raise AccessDeniedError("Access denied: only group owner can delete")

            # Soft delete: set deleted timestamp and metadata
            group.deleted_utc_ts = dt.datetime.now(dt.UTC).timestamp()
            group.deleted_by_id = user_id
            group.prep_for_save()  # Updates timestamp

            # Save the updated group
            save_result = self._save_model(group)
            if save_result.success:
                return ServiceResult.success_result(True)
            else:
                return save_result

        except Exception as e:
            return self._handle_service_exception(e, 'delete_group', resource_id=resource_id, tenant_id=tenant_id)

    def _group_name_exists_for_user(self, name: str, user_id: str, tenant_id: str) -> bool:
        """Check if group name already exists for this user."""
        try:
            group = self._get_group_by_name_and_owner(name, user_id, tenant_id)
            return group is not None
        except:
            return False

    def _get_group_by_name_and_owner(self, name: str, owner_id: str, tenant_id: str) -> Optional[Group]:
        """Get group by name and owner (helper method)."""
        # This would require a GSI for name+owner
        # For now, we'll query owner's groups and check names
        owner_groups_result = self.get_groups_by_owner(owner_id, tenant_id, owner_id, limit=100)
        if owner_groups_result.success:
            for group in owner_groups_result.data:
                if group.name == name:
                    return group
        return None

    def _is_valid_category(self, category: str) -> bool:
        """Validate group category."""
        # This should come from a predefined list
        valid_categories = [
            "sports", "hobby", "professional", "educational",
            "social", "religious", "political", "charity",
            "entertainment", "other"
        ]
        return category.lower() in valid_categories

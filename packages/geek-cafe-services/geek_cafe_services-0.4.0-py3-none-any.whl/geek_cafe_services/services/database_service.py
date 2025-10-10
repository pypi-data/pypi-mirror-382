# Database Service

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Dict, Any, List, Optional
from boto3_assist.dynamodb.dynamodb import DynamoDB
from ..core.service_result import ServiceResult
from ..core.service_errors import ValidationError, AccessDeniedError, NotFoundError
import os

T = TypeVar("T")


class DatabaseService(ABC, Generic[T]):
    """Base service class for database operations."""

    def __init__(self, *, dynamodb: DynamoDB = None, table_name: str = None):
        self.dynamodb = dynamodb or DynamoDB()
        self.table_name = (
            table_name or os.getenv("DYNAMODB_TABLE_NAME")
        )

        if not self.table_name:
            raise ValueError("Table name is required")

    @abstractmethod
    def create(self, tenant_id: str, user_id: str, **kwargs) -> ServiceResult[T]:
        """Create a new resource."""
        pass

    @abstractmethod
    def get_by_id(
        self, resource_id: str, tenant_id: str, user_id: str
    ) -> ServiceResult[T]:
        """Get resource by ID with access control."""
        pass

    @abstractmethod
    def update(
        self, resource_id: str, tenant_id: str, user_id: str, updates: Dict[str, Any]
    ) -> ServiceResult[T]:
        """Update resource with access control."""
        pass

    @abstractmethod
    def delete(
        self, resource_id: str, tenant_id: str, user_id: str
    ) -> ServiceResult[bool]:
        """Delete resource with access control."""
        pass

    def _validate_required_fields(
        self, data: Dict[str, Any], required_fields: List[str]
    ) -> None:
        """Validate required fields are present."""
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            if len(missing_fields) == 1:
                raise ValidationError(f"Field '{missing_fields[0]}' is required", missing_fields[0])
            else:
                field_list = "', '".join(missing_fields)
                raise ValidationError(f"Fields '{field_list}' are required", missing_fields)

    def _validate_tenant_access(
        self, resource_tenant_id: str, user_tenant_id: str
    ) -> None:
        """Validate user has access to tenant resources."""
        if resource_tenant_id != user_tenant_id:
            raise AccessDeniedError("Access denied to resource in different tenant")

    def _save_model(self, model: T) -> ServiceResult[T]:
        """Save model to database with enhanced error handling."""
        try:
            # The boto3_assist library should handle GSI key population automatically
            # through the model's indexing system, so we don't need to manually set them
            self.dynamodb.save(table_name=self.table_name, item=model)
            return ServiceResult.success_result(model)
        except Exception as e:
            return ServiceResult.exception_result(
                e,
                error_code="DATABASE_SAVE_ERROR",
                context=f"Failed to save model to table {self.table_name}",
            )

    def _get_model_by_id(self, resource_id: str, model_class) -> Optional[T]:
        """Get model by ID from database."""
        try:
            # Create temporary model instance to get the primary key
            temp_model = model_class()
            temp_model.id = resource_id
            key = temp_model.get_key("primary").key()

            result = self.dynamodb.get(table_name=self.table_name, key=key)
            if not result or "Item" not in result:
                return None

            # Create model instance from database result
            model = model_class()
            model.map(result["Item"])

            return model
        except Exception:
            return None

    def _delete_model(self, model: T) -> ServiceResult[bool]:
        """Delete model from database with enhanced error handling."""
        try:
            primary_key = model.get_key("primary").key()
            self.dynamodb.delete(table_name=self.table_name, primary_key=primary_key)
            return ServiceResult.success_result(True)
        except Exception as e:
            return ServiceResult.exception_result(
                e,
                error_code="DATABASE_DELETE_ERROR",
                context=f"Failed to delete model from table {self.table_name}",
            )

    def _query_by_index(
        self,
        model: T,
        index_name: str,
        *,
        ascending: bool = False,
        strongly_consistent: bool = False,
        projection_expression: Optional[str] = None,
        expression_attribute_names: Optional[dict] = None,
        start_key: Optional[dict] = None,
        limit: Optional[int] = None,
    ) -> ServiceResult[List[T]]:
        """
        Generic query method for GSI queries with automatic model mapping.

        Args:
            model: The pre-configured model instance to use for the query
            index_name: The name of the GSI index to query

        Returns:
            ServiceResult containing a list of mapped model instances.
            Pagination info is included in error_details as 'last_evaluated_key' if more results exist.
        """
        try:
            # Get the key for the specified index from the provided model
            key = model.get_key(index_name).key()

            # Execute the query
            response = self.dynamodb.query(
                table_name=self.table_name,
                key=key,
                index_name=index_name,
                ascending=ascending,
                strongly_consistent=strongly_consistent,
                projection_expression=projection_expression,
                expression_attribute_names=expression_attribute_names,
                start_key=start_key,
                limit=limit,
            )

            # Extract items from response
            data = response.get("Items", [])

            # Map each item to a model instance
            model_class = type(model)
            items = [model_class().map(item) for item in data]

            # Include pagination info if present
            result = ServiceResult.success_result(items)
            if "LastEvaluatedKey" in response:
                result.error_details = {"last_evaluated_key": response["LastEvaluatedKey"]}

            return result

        except Exception as e:
            return ServiceResult.exception_result(
                e,
                error_code="DATABASE_QUERY_ERROR",
                context=f"Failed to query index {index_name} on table {self.table_name}",
            )

    def _handle_service_exception(
        self, e: Exception, operation: str, **context
    ) -> ServiceResult[T]:
        """Common exception handler for service operations."""
        if isinstance(e, ValidationError):
            field_info = getattr(e, "field", None)
            # Handle both single field and list of fields
            if isinstance(field_info, list):
                error_details = {"fields": field_info, **context}
            else:
                error_details = {"field": field_info, **context}
            return ServiceResult.error_result(
                f"Validation failed: {str(e)}",
                error_code="VALIDATION_ERROR",
                error_details=error_details,
            )
        elif isinstance(e, AccessDeniedError):
            return ServiceResult.error_result(
                str(e), error_code="ACCESS_DENIED", error_details=context
            )
        elif isinstance(e, NotFoundError):
            return ServiceResult.error_result(
                str(e), error_code="NOT_FOUND", error_details=context
            )
        else:
            return ServiceResult.exception_result(
                e, error_code="INTERNAL_ERROR", context=f"Operation {operation} failed"
            )

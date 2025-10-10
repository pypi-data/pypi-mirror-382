from boto3_assist.dynamodb.dynamodb_index import DynamoDBIndex, DynamoDBKey
from boto3_assist.utilities.string_utility import StringUtility
import datetime as dt
from typing import List, Optional, Dict, Any
from geek_cafe_services.models.base_model import BaseModel


class User(BaseModel):
    """
    User model for event scheduling system.

    Represents users with roles, tenant association, and profile information.
    """

    def __init__(self):
        super().__init__()
        self._email: str | None = None
        self._first_name: str | None = None
        self._last_name: str | None = None
        self._roles: List[str] = ["user"]
        self._avatar: str | None = None

        self._setup_indexes()

    def _setup_indexes(self):
        """Setup DynamoDB indexes for user queries."""

        # Primary index: users by ID
        primary: DynamoDBIndex = DynamoDBIndex()
        primary.name = "primary"
        primary.partition_key.attribute_name = "pk"
        primary.partition_key.value = lambda: DynamoDBKey.build_key(("user", self.id))
        primary.sort_key.attribute_name = "sk"
        primary.sort_key.value = lambda: DynamoDBKey.build_key(("user", self.id))
        self.indexes.add_primary(primary)

        ## GSI: 1 - Users by email (for uniqueness and login)
        gsi1: DynamoDBIndex = DynamoDBIndex()
        gsi1.name = "gsi1"
        gsi1.partition_key.attribute_name = f"{gsi1.name}_pk"
        gsi1.partition_key.value = lambda: DynamoDBKey.build_key(("email", self.email))
        gsi1.sort_key.attribute_name = f"{gsi1.name}_sk"
        gsi1.sort_key.value = lambda: DynamoDBKey.build_key(("email", self.email))
        self.indexes.add_secondary(gsi1)

        ## GSI: 2 - Users by tenant
        gsi2: DynamoDBIndex = DynamoDBIndex()
        gsi2.name = "gsi2"
        gsi2.partition_key.attribute_name = f"{gsi2.name}_pk"
        gsi2.partition_key.value = lambda: DynamoDBKey.build_key(("tenant", self.tenant_id))
        gsi2.sort_key.attribute_name = f"{gsi2.name}_sk"
        gsi2.sort_key.value = lambda: DynamoDBKey.build_key(("ts", self.created_utc_ts))
        self.indexes.add_secondary(gsi2)

        ## GSI: 3 - Users by role (for admin queries)
        gsi3: DynamoDBIndex = DynamoDBIndex()
        gsi3.name = "gsi3"
        gsi3.partition_key.attribute_name = f"{gsi3.name}_pk"
        gsi3.partition_key.value = lambda: DynamoDBKey.build_key(("role", self.primary_role))
        gsi3.sort_key.attribute_name = f"{gsi3.name}_sk"
        gsi3.sort_key.value = lambda: DynamoDBKey.build_key(("tenant", self.tenant_id), ("ts", self.created_utc_ts))
        self.indexes.add_secondary(gsi3)

        ## GSI: 4 - All users (for admin listing)
        gsi4: DynamoDBIndex = DynamoDBIndex()
        gsi4.name = "gsi4"
        gsi4.partition_key.attribute_name = f"{gsi4.name}_pk"
        gsi4.partition_key.value = lambda: DynamoDBKey.build_key(("user", "all"))
        gsi4.sort_key.attribute_name = f"{gsi4.name}_sk"
        gsi4.sort_key.value = lambda: DynamoDBKey.build_key(("ts", self.created_utc_ts))
        self.indexes.add_secondary(gsi4)

    @property
    def email(self) -> str | None:
        """User's email address."""
        return self._email

    @email.setter
    def email(self, value: str | None):
        """Set email and ensure it's lowercase."""
        if value:
            self._email = value.lower()
        else:
            self._email = value

    @property
    def first_name(self) -> str | None:
        """User's first name."""
        return self._first_name

    @first_name.setter
    def first_name(self, value: str | None):
        self._first_name = value

    @property
    def last_name(self) -> str | None:
        """User's last name."""
        return self._last_name

    @last_name.setter
    def last_name(self, value: str | None):
        self._last_name = value

    @property
    def full_name(self) -> str:
        """User's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return ""

    @property
    def roles(self) -> List[str]:
        """User's roles."""
        return self._roles

    @roles.setter
    def roles(self, value: List[str]):
        """Set roles, ensuring it's always a list."""
        if value is None:
            self._roles = ["user"]
        elif isinstance(value, list):
            self._roles = value if value else ["user"]
        else:
            self._roles = ["user"]

    @property
    def primary_role(self) -> str:
        """Primary role (first in the list, or 'user' if empty)."""
        return self._roles[0] if self._roles else "user"

    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return "admin" in self._roles

    @property
    def is_organizer(self) -> bool:
        """Check if user has organizer role."""
        return "organizer" in self._roles

    @property
    def avatar(self) -> str | None:
        """User's avatar URL."""
        return self._avatar

    @avatar.setter
    def avatar(self, value: str | None):
        self._avatar = value

    def has_role(self, role: str) -> bool:
        """Check if user has a specific role."""
        return role in self._roles

    def add_role(self, role: str):
        """Add a role to the user if not already present."""
        if role not in self._roles:
            self._roles.append(role)

    def remove_role(self, role: str):
        """Remove a role from the user."""
        if role in self._roles:
            self._roles.remove(role)
            # Ensure at least 'user' role remains
            if not self._roles:
                self._roles = ["user"]

    
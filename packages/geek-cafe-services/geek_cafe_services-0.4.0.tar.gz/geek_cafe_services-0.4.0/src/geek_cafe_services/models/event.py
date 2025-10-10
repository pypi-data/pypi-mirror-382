from boto3_assist.dynamodb.dynamodb_index import DynamoDBIndex, DynamoDBKey
from boto3_assist.utilities.string_utility import StringUtility
import datetime as dt
from typing import List, Optional, Dict, Any
from geek_cafe_services.models.base_model import BaseModel


class Event(BaseModel):
    """
    Event model for event scheduling system.

    Represents events with visibility controls, guest lists, and group associations.
    """

    def __init__(self):
        super().__init__()
        self._title: str | None = None
        self._date: str | None = None  # ISO8601 date string
        self._description: str | None = None
        self._visibility: str = "public"  # public, private, members_only
        self._group_id: str | None = None
        self._invited_guests: List[str] = []
        self._organizer_id: str | None = None
        self._is_draft: bool = False

        self._setup_indexes()

    def _setup_indexes(self):
        """Setup DynamoDB indexes for event queries."""

        # Primary index: events by ID
        primary: DynamoDBIndex = DynamoDBIndex()
        primary.name = "primary"
        primary.partition_key.attribute_name = "pk"
        primary.partition_key.value = lambda: DynamoDBKey.build_key(("event", self.id))
        primary.sort_key.attribute_name = "sk"
        primary.sort_key.value = lambda: DynamoDBKey.build_key(("event", self.id))
        self.indexes.add_primary(primary)

        ## GSI: 1 - Events by organizer
        gsi: DynamoDBIndex = DynamoDBIndex()
        gsi.name = "gsi1"
        gsi.partition_key.attribute_name = f"{gsi.name}_pk"
        gsi.partition_key.value = lambda: DynamoDBKey.build_key(("user", self.organizer_id))
        gsi.sort_key.attribute_name = f"{gsi.name}_sk"
        gsi.sort_key.value = lambda: DynamoDBKey.build_key(("model", "event"), ("ts", self.created_utc_ts))
        self.indexes.add_secondary(gsi)

        ## GSI: 2 - Events by group
        gsi: DynamoDBIndex = DynamoDBIndex()
        gsi.name = "gsi2"
        gsi.partition_key.attribute_name = f"{gsi.name}_pk"
        gsi.partition_key.value = lambda: DynamoDBKey.build_key(("group", self.group_id))
        gsi.sort_key.attribute_name = f"{gsi.name}_sk"
        gsi.sort_key.value = lambda: DynamoDBKey.build_key(("ts", self.created_utc_ts))
        self.indexes.add_secondary(gsi)

        ## GSI: 3 - Events by visibility
        gsi: DynamoDBIndex = DynamoDBIndex()
        gsi.name = "gsi3"
        gsi.partition_key.attribute_name = f"{gsi.name}_pk"
        gsi.partition_key.value = lambda: DynamoDBKey.build_key(("visibility", self.visibility))
        gsi.sort_key.attribute_name = f"{gsi.name}_sk"
        gsi.sort_key.value = lambda: DynamoDBKey.build_key(("ts", self.created_utc_ts))
        self.indexes.add_secondary(gsi)

        ## GSI: 4 - Events by date (for upcoming events)
        gsi: DynamoDBIndex = DynamoDBIndex()
        gsi.name = "gsi4"
        gsi.partition_key.attribute_name = f"{gsi.name}_pk"
        gsi.partition_key.value = lambda: DynamoDBKey.build_key(("event", "date"))
        gsi.sort_key.attribute_name = f"{gsi.name}_sk"
        gsi.sort_key.value = lambda: DynamoDBKey.build_key(("date", self.event_date_timestamp), ("ts", self.created_utc_ts))
        self.indexes.add_secondary(gsi)

        ## GSI: 5 - Events by tenant
        gsi: DynamoDBIndex = DynamoDBIndex()
        gsi.name = "gsi5"
        gsi.partition_key.attribute_name = f"{gsi.name}_pk"
        gsi.partition_key.value = lambda: DynamoDBKey.build_key(("tenant", self.tenant_id))
        gsi.sort_key.attribute_name = f"{gsi.name}_sk"
        gsi.sort_key.value = lambda: DynamoDBKey.build_key(("model", "event"), ("ts", self.created_utc_ts))
        self.indexes.add_secondary(gsi)

        ## GSI: 6 - All events (for admin queries)
        gsi: DynamoDBIndex = DynamoDBIndex()
        gsi.name = "gsi6"
        gsi.partition_key.attribute_name = f"{gsi.name}_pk"
        gsi.partition_key.value = lambda: DynamoDBKey.build_key(("event", "all"))
        gsi.sort_key.attribute_name = f"{gsi.name}_sk"
        gsi.sort_key.value = lambda: DynamoDBKey.build_key(("ts", self.created_utc_ts))
        self.indexes.add_secondary(gsi)

    @property
    def title(self) -> str | None:
        """Event title."""
        return self._title

    @title.setter
    def title(self, value: str | None):
        self._title = value

    @property
    def date(self) -> str | None:
        """Event date in ISO8601 format."""
        return self._date

    @date.setter
    def date(self, value: str | None):
        self._date = value

    @property
    def event_date_timestamp(self) -> float | None:
        """Event date as timestamp for sorting."""
        if self._date:
            try:
                # Parse ISO8601 date string to timestamp
                dt_obj = dt.datetime.fromisoformat(self._date.replace('Z', '+00:00'))
                return dt_obj.timestamp()
            except:
                return None
        return None

    @property
    def description(self) -> str | None:
        """Event description."""
        return self._description

    @description.setter
    def description(self, value: str | None):
        self._description = value

    @property
    def visibility(self) -> str:
        """Event visibility: public, private, members_only."""
        return self._visibility

    @visibility.setter
    def visibility(self, value: str | None):
        """Set visibility with validation."""
        if value in ["public", "private", "members_only"]:
            self._visibility = value
        else:
            self._visibility = "public"  # default

    @property
    def is_private(self) -> bool:
        """Legacy compatibility - is this a private event."""
        return self._visibility == "private"

    @property
    def is_standalone(self) -> bool:
        """Is this event not associated with a group."""
        return self._group_id is None

    @property
    def group_id(self) -> str | None:
        """Associated group ID."""
        return self._group_id

    @group_id.setter
    def group_id(self, value: str | None):
        self._group_id = value

    @property
    def invited_guests(self) -> List[str]:
        """List of invited guest user IDs."""
        return self._invited_guests

    @invited_guests.setter
    def invited_guests(self, value: List[str] | None):
        """Set invited guests, ensuring it's always a list."""
        if value is None:
            self._invited_guests = []
        elif isinstance(value, list):
            self._invited_guests = value
        else:
            self._invited_guests = []

    @property
    def organizer_id(self) -> str | None:
        """Event organizer user ID."""
        return self._organizer_id

    @organizer_id.setter
    def organizer_id(self, value: str | None):
        self._organizer_id = value

    @property
    def is_draft(self) -> bool:
        """Is this a draft event."""
        return self._is_draft

    @is_draft.setter
    def is_draft(self, value: bool):
        self._is_draft = bool(value)

    def is_user_invited(self, user_id: str) -> bool:
        """Check if a user is invited to this event."""
        return user_id in self._invited_guests

    def add_invited_guest(self, user_id: str):
        """Add a user to the invited guests list."""
        if user_id not in self._invited_guests:
            self._invited_guests.append(user_id)

    def remove_invited_guest(self, user_id: str):
        """Remove a user from the invited guests list."""
        if user_id in self._invited_guests:
            self._invited_guests.remove(user_id)

    def is_upcoming(self) -> bool:
        """Check if the event is in the future."""
        if self._date:
            event_ts = self.event_date_timestamp
            now_ts = dt.datetime.now(dt.UTC).timestamp()
            return event_ts > now_ts
        return False



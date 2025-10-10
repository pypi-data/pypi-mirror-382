from boto3_assist.dynamodb.dynamodb_index import DynamoDBIndex, DynamoDBKey
from boto3_assist.utilities.string_utility import StringUtility
import datetime as dt
from typing import List, Optional, Dict, Any
from geek_cafe_services.models.base_model import BaseModel


class MessageThread(BaseModel):
    """
    MessageThread model for complex message threading.

    Represents threaded conversations with multiple participants,
    associated with events or general discussions.
    """

    def __init__(self):
        super().__init__()
        self._subject: str | None = None
        self._participants: List[Dict[str, Any]] = []
        self._messages: List[Dict[str, Any]] = []
        self._last_message_at: float | None = None
        self._event_id: str | None = None
        self._event_title: str | None = None
        self._type: str = "general"  # general, event, direct
        self._is_archived: bool = False

        self._setup_indexes()

    def _setup_indexes(self):
        """Setup DynamoDB indexes for thread queries."""

        # Primary index: threads by ID
        primary: DynamoDBIndex = DynamoDBIndex()
        primary.name = "primary"
        primary.partition_key.attribute_name = "pk"
        primary.partition_key.value = lambda: DynamoDBKey.build_key(("thread", self.id))
        primary.sort_key.attribute_name = "sk"
        primary.sort_key.value = lambda: DynamoDBKey.build_key(("thread", self.id))
        self.indexes.add_primary(primary)

        ## GSI: 1 - Threads by event
        gsi: DynamoDBIndex = DynamoDBIndex()
        gsi.name = "gsi1"
        gsi.partition_key.attribute_name = f"{gsi.name}_pk"
        gsi.partition_key.value = lambda: DynamoDBKey.build_key(("event", self.event_id))
        gsi.sort_key.attribute_name = f"{gsi.name}_sk"
        gsi.sort_key.value = lambda: DynamoDBKey.build_key(("ts", self.last_message_at or self.created_utc_ts))
        self.indexes.add_secondary(gsi)

        ## GSI: 2 - Threads by type
        gsi: DynamoDBIndex = DynamoDBIndex()
        gsi.name = "gsi2"
        gsi.partition_key.attribute_name = f"{gsi.name}_pk"
        gsi.partition_key.value = lambda: DynamoDBKey.build_key(("model", "thread") ,( "type", self.type))
        gsi.sort_key.attribute_name = f"{gsi.name}_sk"
        gsi.sort_key.value = lambda: DynamoDBKey.build_key(("ts", self.last_message_at or self.created_utc_ts))
        self.indexes.add_secondary(gsi)

        ## GSI: 3 - Threads by tenant
        gsi: DynamoDBIndex = DynamoDBIndex()
        gsi.name = "gsi3"
        gsi.partition_key.attribute_name = f"{gsi.name}_pk"
        gsi.partition_key.value = lambda: DynamoDBKey.build_key(("tenant", self.tenant_id))
        gsi.sort_key.attribute_name = f"{gsi.name}_sk"
        gsi.sort_key.value = lambda: DynamoDBKey.build_key(("model", "thread"), ("ts", self.last_message_at or self.created_utc_ts))
        self.indexes.add_secondary(gsi)

        ## GSI: 4 - All threads (for admin queries)
        gsi: DynamoDBIndex = DynamoDBIndex()
        gsi.name = "gsi4"
        gsi.partition_key.attribute_name = f"{gsi.name}_pk"
        gsi.partition_key.value = lambda: DynamoDBKey.build_key(("model", "thread"), ("all", "all"))
        gsi.sort_key.attribute_name = f"{gsi.name}_sk"
        gsi.sort_key.value = lambda: DynamoDBKey.build_key(("ts", self.last_message_at or self.created_utc_ts))
        self.indexes.add_secondary(gsi)

        ## GSI: 5 - Threads by tenant and archived status
        gsi: DynamoDBIndex = DynamoDBIndex()
        gsi.name = "gsi5"
        gsi.partition_key.attribute_name = f"{gsi.name}_pk"
        gsi.partition_key.value = lambda: DynamoDBKey.build_key(("tenant", self.tenant_id))
        gsi.sort_key.attribute_name = f"{gsi.name}_sk"
        gsi.sort_key.value = lambda: DynamoDBKey.build_key(
            ("archived", "1" if self.is_archived else "0"),
            ("ts", self.last_message_at or self.created_utc_ts)
        )
        self.indexes.add_secondary(gsi)


    @property
    def subject(self) -> str | None:
        """Thread subject."""
        return self._subject

    @subject.setter
    def subject(self, value: str | None):
        self._subject = value

    @property
    def participants(self) -> List[Dict[str, Any]]:
        """Thread participants with their details."""
        return self._participants

    @participants.setter
    def participants(self, value: List[Dict[str, Any]] | None):
        """Set participants, ensuring it's always a list."""
        if value is None:
            self._participants = []
        elif isinstance(value, list):
            self._participants = value
        else:
            self._participants = []

    @property
    def messages(self) -> List[Dict[str, Any]]:
        """Messages in this thread."""
        return self._messages

    @messages.setter
    def messages(self, value: List[Dict[str, Any]] | None):
        """Set messages, ensuring it's always a list."""
        if value is None:
            self._messages = []
        elif isinstance(value, list):
            self._messages = value
        else:
            self._messages = []

    @property
    def last_message_at(self) -> float | None:
        """Timestamp of the last message."""
        return self._last_message_at

    @last_message_at.setter
    def last_message_at(self, value: float | None):
        self._last_message_at = value

    @property
    def event_id(self) -> str | None:
        """Associated event ID."""
        return self._event_id

    @event_id.setter
    def event_id(self, value: str | None):
        self._event_id = value

    @property
    def event_title(self) -> str | None:
        """Associated event title."""
        return self._event_title

    @event_title.setter
    def event_title(self, value: str | None):
        self._event_title = value

    @property
    def type(self) -> str:
        """Thread type: general, event, direct."""
        return self._type

    @type.setter
    def type(self, value: str | None):
        """Set type with validation."""
        if value in ["general", "event", "direct"]:
            self._type = value
        else:
            self._type = "general"  # default

    @property
    def unread_count(self) -> int:
        """Number of unread messages (calculated)."""
        # This would typically be calculated per user
        # For now, return 0 as a placeholder
        return 0

    @property
    def participant_ids(self) -> List[str]:
        """List of participant user IDs."""
        return [p.get('id') for p in self._participants if p.get('id')]

    def is_user_participant(self, user_id: str) -> bool:
        """Check if a user is a participant in this thread."""
        return user_id in self.participant_ids

    def add_participant(self, user_id: str, name: str = "", avatar: str = "", role: str = "guest"):
        """Add a participant to the thread."""
        if not self.is_user_participant(user_id):
            participant = {
                "id": user_id,
                "name": name,
                "avatar": avatar,
                "role": role
            }
            self._participants.append(participant)

    def remove_participant(self, user_id: str):
        """Remove a participant from the thread."""
        self._participants = [
            p for p in self._participants
            if p.get('id') != user_id
        ]

    def add_message(self, message: Dict[str, Any]):
        """Add a message to the thread."""
        if message not in self._messages:
            self._messages.append(message)
            # Update last message timestamp
            if 'created_at' in message:
                self._last_message_at = message['created_at']

    def get_recent_messages(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent messages from the thread."""
        # Sort messages by created_at descending and take limit
        sorted_messages = sorted(
            self._messages,
            key=lambda m: m.get('created_at', 0),
            reverse=True
        )
        return sorted_messages[:limit]

    def get_message_count(self) -> int:
        """Get total number of messages in thread."""
        return len(self._messages)

    def can_user_access(self, user_id: str) -> bool:
        """
        Check if a user can access this thread.

        Basic implementation - access control will be enhanced later.
        """
        # For now, only participants can access
        return self.is_user_participant(user_id)

    @property
    def is_archived(self) -> bool:
        return self._is_archived

    @is_archived.setter
    def is_archived(self, value: bool):
        self._is_archived = value

   
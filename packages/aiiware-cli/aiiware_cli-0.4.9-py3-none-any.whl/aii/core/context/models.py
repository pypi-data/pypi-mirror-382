"""Context-related data models"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ChatMessage:
    """Individual message in a chat"""

    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self) -> None:
        """Validate role"""
        if self.role not in ("user", "assistant", "system"):
            raise ValueError(f"Invalid role: {self.role}")


@dataclass
class ChatContext:
    """Chat conversation context"""

    chat_id: str = field(
        default_factory=lambda: f"chat-{datetime.now().strftime('%Y-%m-%d')}-{uuid.uuid4().hex[:8]}"
    )
    title: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    messages: list[ChatMessage] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    archived: bool = False

    def __post_init__(self) -> None:
        """Set default title if not provided"""
        if not self.title:
            self.title = f"Chat {self.chat_id[-8:]}"

    def add_message(
        self, role: str, content: str, metadata: dict[str, Any] | None = None
    ) -> ChatMessage:
        """Add a message to the conversation"""
        message = ChatMessage(role=role, content=content, metadata=metadata or {})
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message

    def add_user_message(
        self, content: str, metadata: dict[str, Any] | None = None
    ) -> ChatMessage:
        """Add a user message"""
        return self.add_message("user", content, metadata)

    def add_assistant_message(
        self, content: str, metadata: dict[str, Any] | None = None
    ) -> ChatMessage:
        """Add an assistant message"""
        return self.add_message("assistant", content, metadata)

    def add_system_message(
        self, content: str, metadata: dict[str, Any] | None = None
    ) -> ChatMessage:
        """Add a system message"""
        return self.add_message("system", content, metadata)

    def get_recent_messages(self, limit: int = 20) -> list[ChatMessage]:
        """Get recent messages up to limit"""
        return self.messages[-limit:] if limit > 0 else self.messages

    def get_messages_by_role(self, role: str) -> list[ChatMessage]:
        """Get all messages by specific role"""
        return [msg for msg in self.messages if msg.role == role]

    @property
    def message_count(self) -> int:
        """Get total message count"""
        return len(self.messages)

    @property
    def last_message(self) -> ChatMessage | None:
        """Get the last message"""
        return self.messages[-1] if self.messages else None

    @property
    def last_user_message(self) -> ChatMessage | None:
        """Get the last user message"""
        user_messages = self.get_messages_by_role("user")
        return user_messages[-1] if user_messages else None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "chat_id": self.chat_id,
            "title": self.title,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "metadata": msg.metadata,
                    "message_id": msg.message_id,
                }
                for msg in self.messages
            ],
            "metadata": self.metadata,
            "tags": self.tags,
            "archived": self.archived,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ChatContext":
        """Create ChatContext from dictionary"""
        # Parse messages
        messages = []
        for msg_data in data.get("messages", []):
            message = ChatMessage(
                role=msg_data["role"],
                content=msg_data["content"],
                timestamp=datetime.fromisoformat(msg_data["timestamp"]),
                metadata=msg_data.get("metadata", {}),
                message_id=msg_data.get("message_id", str(uuid.uuid4())),
            )
            messages.append(message)

        # Create context
        context = cls(
            chat_id=data["chat_id"],
            title=data.get("title", ""),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            messages=messages,
            metadata=data.get("metadata", {}),
            tags=data.get("tags", []),
            archived=data.get("archived", False),
        )

        return context

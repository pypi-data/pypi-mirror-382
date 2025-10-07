# Auto-generated Python types from Avro schemas
# DO NOT EDIT MANUALLY

from typing import Optional, Any


class EventMetadata:
    """Common metadata for all events"""
    def __init__(self, correlationId: str, causationId: str, traceId: str):
        # Unique identifier for tracking related events
        self.correlationId = correlationId
        # Identifier of the event that caused this event
        self.causationId = causationId
        # Distributed tracing identifier
        self.traceId = traceId


class BaseEvent:
    """Base event structure for all events in the system"""
    def __init__(self, eventId: str, eventType: str, version: str, timestamp: str, source: str, metadata: EventMetadata):
        # Unique identifier for this event
        self.eventId = eventId
        # Type of event (e.g., user.created, user.updated)
        self.eventType = eventType
        # Schema version for this event
        self.version = version
        # ISO 8601 timestamp when the event occurred
        self.timestamp = timestamp
        # Service that generated this event
        self.source = source
        # Event metadata for tracing and correlation
        self.metadata = metadata


class PromoCodeUsePayload:
    """Payload for using promo code"""
    def __init__(self, promoCode: str, success: bool):
        # Promo code for use
        self.promoCode = promoCode
        # Is successfull promo code usage
        self.success = success


class PromoCodeUsedEvent:
    """Event emitted when a promo code used"""
    def __init__(self, eventId: str, eventType: str, version: str, timestamp: str, source: str, metadata: EventMetadata, data: PromoCodeUsePayload):
        # Unique identifier for this event
        self.eventId = eventId
        # Type of event
        self.eventType = eventType
        # Schema version for this event
        self.version = version
        # ISO 8601 timestamp when the event occurred
        self.timestamp = timestamp
        # Service that generated this event
        self.source = source
        # Event metadata for tracing and correlation
        self.metadata = metadata
        # Promo code data
        self.data = data


class UserPayload:
    """User data payload"""
    def __init__(self, id: str, login: str, phone: str, email: Optional[str] = None, name: Optional[str] = None, surname: Optional[str] = None, patronymic: Optional[str] = None, birthday: Optional[str] = None, gender: Optional[str] = None, avatarUrl: Optional[str] = None, photoUrl: Optional[str] = None, clubId: Optional[int] = None, rankId: Optional[int] = None):
        # Unique identifier for the user
        self.id = id
        # User login
        self.login = login
        # User phone number
        self.phone = phone
        # User email address
        self.email = email
        # User first name
        self.name = name
        # User surname
        self.surname = surname
        # User patronymic
        self.patronymic = patronymic
        # User birthday
        self.birthday = birthday
        # User gender
        self.gender = gender
        # User avatar URL
        self.avatarUrl = avatarUrl
        # User photo URL
        self.photoUrl = photoUrl
        # User club ID
        self.clubId = clubId
        # User rank ID
        self.rankId = rankId


class UserCreatedEvent:
    """Event emitted when a new user is created"""
    def __init__(self, eventId: str, eventType: str, version: str, timestamp: str, source: str, metadata: EventMetadata, data: UserPayload):
        # Unique identifier for this event
        self.eventId = eventId
        # Type of event
        self.eventType = eventType
        # Schema version for this event
        self.version = version
        # ISO 8601 timestamp when the event occurred
        self.timestamp = timestamp
        # Service that generated this event
        self.source = source
        # Event metadata for tracing and correlation
        self.metadata = metadata
        # User data
        self.data = data


class UpdateUserPayload:
    """User update payload"""
    def __init__(self, userId: str, login: Optional[str] = None, phone: Optional[str] = None, email: Optional[str] = None, name: Optional[str] = None, surname: Optional[str] = None, patronymic: Optional[str] = None, birthday: Optional[str] = None, gender: Optional[str] = None, avatarUrl: Optional[str] = None, photoUrl: Optional[str] = None, rankId: Optional[int] = None):
        # Unique identifier for the user being updated
        self.userId = userId
        # User login
        self.login = login
        # User phone number
        self.phone = phone
        # User email address
        self.email = email
        # User first name
        self.name = name
        # User surname
        self.surname = surname
        # User patronymic
        self.patronymic = patronymic
        # User birthday
        self.birthday = birthday
        # User gender
        self.gender = gender
        # User avatar URL
        self.avatarUrl = avatarUrl
        # User photo URL
        self.photoUrl = photoUrl
        # User rank ID
        self.rankId = rankId


class UserUpdatedEvent:
    """Event emitted when a user is updated"""
    def __init__(self, eventId: str, eventType: str, version: str, timestamp: str, source: str, metadata: EventMetadata, data: UpdateUserPayload):
        # Unique identifier for this event
        self.eventId = eventId
        # Type of event
        self.eventType = eventType
        # Schema version for this event
        self.version = version
        # ISO 8601 timestamp when the event occurred
        self.timestamp = timestamp
        # Service that generated this event
        self.source = source
        # Event metadata for tracing and correlation
        self.metadata = metadata
        # Updated user data
        self.data = data


class DeletedUserPayload:
    """Deleted user data payload"""
    def __init__(self, userId: str):
        # Unique identifier for the deleted user
        self.userId = userId


class UserDeletedEvent:
    """Event emitted when a user is deleted"""
    def __init__(self, eventId: str, eventType: str, version: str, timestamp: str, source: str, metadata: EventMetadata, data: DeletedUserPayload):
        # Unique identifier for this event
        self.eventId = eventId
        # Type of event
        self.eventType = eventType
        # Schema version for this event
        self.version = version
        # ISO 8601 timestamp when the event occurred
        self.timestamp = timestamp
        # Service that generated this event
        self.source = source
        # Event metadata for tracing and correlation
        self.metadata = metadata
        # Deleted user data
        self.data = data


# Export all classes
__all__ = [
        "EventMetadata",
    "BaseEvent",
    "PromoCodeUsePayload",
    "PromoCodeUsedEvent",
    "UserPayload",
    "UserCreatedEvent",
    "UpdateUserPayload",
    "UserUpdatedEvent",
    "DeletedUserPayload",
    "UserDeletedEvent",
]

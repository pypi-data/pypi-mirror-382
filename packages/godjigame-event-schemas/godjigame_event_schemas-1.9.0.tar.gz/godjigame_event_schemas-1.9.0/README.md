# Event Schemas

> Avro-based event schemas for TypeScript and Python services

This repository contains Apache Avro schemas for event-driven communication between services, with auto-generated TypeScript and Python types.

## 📦 Installation

### TypeScript / JavaScript

```bash
npm install @godjigame/event-schemas
```

### Python

```bash
pip install godjigame-event-schemas
```

## 🚀 Usage

### TypeScript

```typescript
import { UserCreatedEvent, UserUpdatedEvent, EventMetadata } from '@godjigame/event-schemas';

// Create event metadata
const metadata: EventMetadata = {
  correlationId: '123e4567-e89b-12d3-a456-426614174000',
  causationId: '456e7890-e89b-12d3-a456-426614174001',
  traceId: '789e1234-e89b-12d3-a456-426614174002'
};

// Create user created event
const userCreatedEvent: UserCreatedEvent = {
  eventId: '550e8400-e29b-41d4-a716-446655440000',
  eventType: 'user.created',
  version: '1.0.0',
  timestamp: new Date().toISOString(),
  source: 'gamer-id',
  metadata,
  data: {
    userId: 'user123',
    email: 'user@example.com',
    username: 'johndoe',
    displayName: 'John Doe',
    createdAt: new Date().toISOString(),
    updatedAt: null
  }
};

// Use in Kafka consumer
async function handleUserCreated(event: UserCreatedEvent) {
  console.log(`User created: ${event.data.userId}`);
  // Process event...
}
```

### Python

```python
from event_types import UserCreatedEvent, UserUpdatedEvent, EventMetadata
from datetime import datetime
import uuid

# Create event metadata
metadata = EventMetadata(
    correlationId=str(uuid.uuid4()),
    causationId=str(uuid.uuid4()),
    traceId=str(uuid.uuid4())
)

# Create user created event
user_created_event = UserCreatedEvent(
    eventId=str(uuid.uuid4()),
    eventType="user.created",
    version="1.0.0",
    timestamp=datetime.utcnow().isoformat(),
    source="gamer-id",
    metadata=metadata,
    data=UserPayload(
        userId="user123",
        email="user@example.com",
        username="johndoe",
        displayName="John Doe",
        createdAt=datetime.utcnow().isoformat(),
        updatedAt=None
    )
)

# Use in Kafka producer
def publish_user_created(user_data):
    event = UserCreatedEvent(
        eventId=str(uuid.uuid4()),
        eventType="user.created",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat(),
        source="gamer-id",
        metadata=create_metadata(),
        data=user_data
    )
    # Send to Kafka...
```

## 📋 Available Types

### Event Types

- `UserCreatedEvent` - Emitted when a new user is created
- `UserUpdatedEvent` - Emitted when a user is updated
- `UserDeletedEvent` - Emitted when a user is deleted

### Common Types

- `EventMetadata` - Common metadata for all events
- `BaseEvent` - Base event structure
- `UserPayload` - User data payload
- `DeletedUserPayload` - Payload for deleted user events

## 🔧 Development

### Prerequisites

- Node.js 20+
- Python 3.8+

### Setup

```bash
# Clone the repository
git clone https://github.com/goodgameteamit/event-schemas.git
cd event-schemas

# Install dependencies
npm install

# Generate types
npm run generate
```

### Commands

```bash
# Generate TypeScript and Python types
npm run generate

# Validate schemas
npm run test:schemas

# Validate generated types
npm run test:types

# Run all tests
npm test

# Bump version
npm run version:bump
```

### Schema Development

1. **Add new schemas** in the `schemas/` directory
2. **Follow naming conventions**: Use kebab-case for file names
3. **Update dependencies**: Add new schema files to the generation script
4. **Test thoroughly**: Run validation and generation after changes

### Schema Evolution

When evolving schemas:

- ✅ **Add new optional fields** with default values
- ✅ **Add new event types**
- ✅ **Update documentation**
- ❌ **Don't remove existing fields**
- ❌ **Don't rename existing fields**
- ❌ **Don't change field types**

## 📁 Repository Structure

```
event-schemas/
├── schemas/                    # Avro schema definitions
│   ├── metadata.avsc
│   ├── base-event.avsc
│   └── user-events.avsc
├── generated/                  # Generated types
│   ├── typescript/
│   │   └── index.ts
│   └── python/
│       └── __init__.py
├── scripts/                    # Build scripts
│   ├── generate-types.sh
│   └── validate-schemas.js
├── .github/workflows/          # CI/CD pipeline
│   └── release.yml
├── package.json               # NPM package config
├── setup.py                   # Python package config
└── pyproject.toml             # Modern Python config
```

## 🔄 CI/CD Pipeline

The repository includes automated CI/CD with GitHub Actions:

- **Pull Requests**: Schema validation and type generation checks
- **Main Branch**: Automatic NPM publishing and continuous validation

### Publishing

To publish a new version:

```bash
# Bump version in package.json and pyproject.toml
npm run version:bump

# Commit and push changes
git add package.json pyproject.toml
git commit -m "Bump version to x.x.x"
git push
```

## 📖 Schema Documentation

### Event Metadata

All events include common metadata for tracing and correlation:

```json
{
  "correlationId": "Unique identifier for tracking related events",
  "causationId": "Identifier of the event that caused this event",
  "traceId": "Distributed tracing identifier"
}
```

### Base Event Structure

All events extend the base event structure:

```json
{
  "eventId": "Unique identifier for this event",
  "eventType": "Type of event (e.g., user.created)",
  "version": "Schema version",
  "timestamp": "ISO 8601 timestamp",
  "source": "Service that generated the event",
  "metadata": "Event metadata object",
  "data": "Event-specific data"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new schemas
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [Apache Avro](https://avro.apache.org/) - Data serialization system
- [Confluent Schema Registry](https://docs.confluent.io/platform/current/schema-registry/) - Schema management
- [Kafka](https://kafka.apache.org/) - Event streaming platform
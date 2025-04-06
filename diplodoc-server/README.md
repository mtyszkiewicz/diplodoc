# Server Components

## `server.py`
Manages WebSocket connections, processes messages, and handles paragraph operations. Uses aiohttp library and an Application class to maintain client connections and dispatch messages.

## `session.py`
Contains Paragraph and Session classes. Manages collaborative editing sessions with functions to join/leave sessions and create/update/delete paragraphs.

## `lock.py`
Implements the custom locking mechanism to control concurrent paragraph access. The Lock class handles requests to acquire/release locks and maintains client connection states.

## `message.py`
Defines message types for client-server communication:
- Client-to-server: Free, Try, CreateParagraph, UpdateParagraph, DeleteParagraph
- Server-to-client: Init, Ready, Busy, Freed, InitSession, UpdatedParagraph, ParagraphGone

Includes wrapper classes for message serialization/deserialization.

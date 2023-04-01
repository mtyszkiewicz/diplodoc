<img src="./diplodoc-client/public/diplodocus.png">

# Diplodoc is a document editor
Diplodoc is a collaborative text document editor created to solidify our academic knowledge and demonstrate the fundamentals of asynchronous applications.

The solution features a client-server architecture, utilizing the Svelte JavaScript framework for the client and Python for the server. The server handles basic locking mechanisms and manages the event loop, ensuring smooth operation. Communication between the front-end and server is achieved through the exchange of serialized messages via WebSockets, enabling a basic level of asynchronous interaction between the components.

# Setup

## diplodoc-server
```bash
cd diplodoc-server
poetry install
poetry run python3 diplodoc/server.py
```

## diplodoc-client

Update `SERVER_URL` in `diplodoc-client/src/App.svelte` to match your server's ip.
```bash
cd diplodoc-client
npm install
HOST=0.0.0.0 npm run dev
```
# Server API reference

## `server.py`
The server.py module is responsible for managing the core functionality of the Diplodoc server. It utilizes the aiohttp library to handle WebSocket communication with connected clients, process incoming messages, and coordinate operations such as creating, updating, and deleting paragraphs. Furthermore, it manages paragraph locking and unlocking mechanisms.

The primary component of the server.py module is the Application class, which encapsulates the server's core functionality. The class maintains WebSocket connections and client information, dispatches messages to clients, and delegates message handling to corresponding methods based on message types.

The module also provides a main function, which serves as the entry point for the Diplodoc server. It initializes the server, configures command-line arguments for specifying host and port, and starts the aiohttp web application to listen for incoming connections.

## `session.py`
The session.py module is responsible for managing the collaborative editing sessions in the Diplodoc application. It provides two main data classes: Paragraph and Session.

The Paragraph class represents a single paragraph within a collaborative editing session. Each paragraph has a unique identifier, content, and an associated lock for controlling concurrent access.

The Session class represents a collaborative editing session containing multiple paragraphs. It maintains a collection of paragraphs, as well as the set of connected clients. Key functionalities include:

 - `join()`: Allows a client to join the session and initializes necessary messages for the client.
 - `update_paragraph()`: Updates the content of a paragraph and broadcasts the update to all clients in the session.
 - `create_paragraph()`: Creates a new paragraph and sends the initial state to all clients in the session.
 - `delete_paragraph()`: Deletes a paragraph and notifies all clients in the session of the removal.
 - `leave()`: Handles a client leaving the session, releasing any locks held by the client.

## lock.py
The lock.py module is responsible for managing the locking mechanism in the Diplodoc application, which is essential for controlling concurrent access to paragraphs in a collaborative editing session. The module provides a `Lock` class that represents a lock associated with a paragraph.

The `Lock` class has a unique identifier, a reference to the client holding the lock (if any), and a set of connected clients. Key functionalities include:

 - `_try_handler()`: Handles a lock request from a client. If the lock is available, the requesting client is granted the lock, and other clients are notified of the lock status.
 - `_free_handler()`: Releases a lock held by a client and notifies all other clients that the lock is available.
 - `_join_handler()`: Adds a client to the set of connected clients and sends the current lock state to the joining client.
 - `_leave_handler()`: Removes a client from the set of connected clients and releases any locks held by the leaving client.
The `handle()` method serves as a dispatcher that directs incoming messages to the appropriate handler based on the message type.

## message.py

The message.py module is responsible for defining the various message types used for communication between clients and the server in the Diplodoc application. The messages facilitate collaboration on documents and help manage the locking mechanism for paragraphs.

The module defines two sets of message types:

1. **Client-to-server messages:** These messages are sent from clients to the server and include:
   - `FreeMessage`: A request to release a lock on a paragraph.
   - `TryMessage`: A request to acquire a lock on a paragraph.
   - `CreateParagraphSessionMessage`: A request to create a new paragraph in a session.
   - `UpdateParagraphSessionMessage`: A request to update the content of a paragraph in a session.
   - `DeleteParagraphSessionMessage`: A request to delete a paragraph in a session.

2. **Server-to-client messages:** These messages are sent from the server to clients and include:
   - `InitMessage`: A message containing the initial state of a lock.
   - `ReadyMessage`: A message indicating that a lock is ready for a client.
   - `BusyMessage`: A message indicating that a lock is currently held by another client.
   - `FreedMessage`: A message indicating that a lock has been released.
   - `InitSessionMessage`: A message containing the initial state of a session.
   - `UpdatedParagraphSessionMessage`: A message indicating that a paragraph has been updated.
   - `ParagraphGoneSessionMessage`: A message indicating that a paragraph has been deleted.

The module also defines two dummy messages, `JoinMessage` and `LeaveMessage`, used internally for managing locks.

The `ClientToServerMessageWrapper` and `ServerToClientMessageWrapper` classes are provided to facilitate serialization and deserialization of messages using the `serde` library.

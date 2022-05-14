from dataclasses import dataclass
from typing import Optional, Union
from uuid import UUID

from serde import AdjacentTagging, serde

# Server-to-client messages
@serde
@dataclass
class InitMessage:
    lock_id: UUID
    client_id: UUID
    locked_by: Optional[UUID] = None


@serde
@dataclass
class ReadyMessage:
    lock_id: UUID
    client_id: UUID


@serde
@dataclass
class BusyMessage:
    lock_id: UUID
    client_id: UUID
    locked_by: UUID


@serde
@dataclass
class FreedMessage:
    lock_id: UUID
    client_id: UUID


# Client-to-server messages
@serde
@dataclass
class FreeMessage:
    lock_id: UUID
    client_id: UUID


@serde
@dataclass
class TryMessage:
    lock_id: UUID
    client_id: UUID

# Dummy messages
@dataclass
class JoinMessage:
    lock_id: UUID
    client_id: UUID

@dataclass
class LeaveMessage:
    lock_id: UUID
    client_id: UUID


@serde(tagging=AdjacentTagging("type", "content"))
@dataclass
class ClientToServerMessage:
    inner: Union[FreeMessage, TryMessage]


@serde(tagging=AdjacentTagging("type", "content"))
@dataclass
class ServerToClientMessage:
    inner: Union[InitMessage, ReadyMessage, BusyMessage, FreedMessage]


Message = ClientToServerMessage | ServerToClientMessage
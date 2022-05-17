from dataclasses import dataclass
from typing import Optional, Protocol, Union


from serde import AdjacentTagging, serde
from uuid import UUID


## Client-to-server messages
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


@serde
@dataclass
class CreateParagraphSessionMessage:
    session_id: UUID
    client_id: UUID


@serde
@dataclass
class UpdateParagraphSessionMessage:
    session_id: UUID
    paragraph_id: UUID
    content: str
    client_id: UUID


@serde
@dataclass
class DeleteParagraphSessionMessage:
    session_id: UUID
    paragraph_id: UUID
    client_id: UUID


@serde
@dataclass
class ParagraphGoneSessionMessage:
    session_id: UUID
    paragraph_id: UUID
    client_id: UUID
    deleted_by: UUID


## Server-to-client messages
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


@serde
@dataclass
class InitSessionMessage:
    session_id: UUID
    client_id: UUID


@serde
@dataclass
class UpdatedParagraphSessionMessage:
    session_id: UUID
    paragraph_id: UUID
    content: str
    client_id: UUID
    updated_by: UUID


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
    inner: Union[
        FreeMessage,
        TryMessage,
        CreateParagraphSessionMessage,
        UpdateParagraphSessionMessage,
        DeleteParagraphSessionMessage,
    ]


@serde(tagging=AdjacentTagging("type", "content"))
@dataclass
class ServerToClientMessage:
    inner: Union[
        InitMessage,
        ReadyMessage,
        BusyMessage,
        FreedMessage,
        InitSessionMessage, 
        UpdatedParagraphSessionMessage, 
        ParagraphGoneSessionMessage,
    ]


Message = ClientToServerMessage | ServerToClientMessage


class ClientDispachableMessage(Protocol):
    client_id: UUID

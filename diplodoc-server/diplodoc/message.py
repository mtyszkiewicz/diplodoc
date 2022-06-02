from dataclasses import dataclass
from typing import Optional, Union


from serde import serde
from serde.core import AdjacentTagging
from uuid import UUID


## Client-to-server messages
@serde(rename_all="camelcase")
@dataclass
class FreeMessage:
    lock_id: UUID
    client_id: UUID


@serde(rename_all="camelcase")
@dataclass
class TryMessage:
    lock_id: UUID
    client_id: UUID


@serde(rename_all="camelcase")
@dataclass
class CreateParagraphSessionMessage:
    session_id: UUID
    client_id: UUID


@serde(rename_all="camelcase")
@dataclass
class UpdateParagraphSessionMessage:
    session_id: UUID
    paragraph_id: UUID
    content: str
    client_id: UUID


@serde(rename_all="camelcase")
@dataclass
class DeleteParagraphSessionMessage:
    session_id: UUID
    paragraph_id: UUID
    client_id: UUID


@serde(rename_all="camelcase")
@dataclass
class ParagraphGoneSessionMessage:
    session_id: UUID
    paragraph_id: UUID
    client_id: UUID
    deleted_by: UUID


@serde(rename_all="camelcase")
@dataclass
class ReorderParagraphsSessionMessage:
    session_id: UUID
    paragraphs_order: list[UUID]
    client_id: UUID


@serde(rename_all="camelcase")
@dataclass
class ReorderedParagraphsSessionMessage:
    session_id: UUID
    paragraphs_order: list[UUID]
    client_id: UUID
    reordered_by: UUID


## Server-to-client messages
@serde(rename_all="camelcase")
@dataclass
class InitMessage:
    lock_id: UUID
    client_id: UUID
    locked_by: Optional[UUID] = None


@serde(rename_all="camelcase")
@dataclass
class ReadyMessage:
    lock_id: UUID
    client_id: UUID


@serde(rename_all="camelcase")
@dataclass
class BusyMessage:
    lock_id: UUID
    client_id: UUID
    locked_by: UUID


@serde(rename_all="camelcase")
@dataclass
class FreedMessage:
    lock_id: UUID
    client_id: UUID


@serde(rename_all="camelcase")
@dataclass
class InitSessionMessage:
    session_id: UUID
    client_id: UUID


@serde(rename_all="camelcase")
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


ClientToServerMessage = Union[
    FreeMessage,
    TryMessage,
    CreateParagraphSessionMessage,
    UpdateParagraphSessionMessage,
    DeleteParagraphSessionMessage,
    ReorderParagraphsSessionMessage,
]


@serde(
    tagging=AdjacentTagging("@type", "@content"),
    rename_all="camelcase",
)
@dataclass
class ClientToServerMessageWrapper:
    inner: ClientToServerMessage


ServerToClientMessage = Union[
    InitMessage,
    ReadyMessage,
    BusyMessage,
    FreedMessage,
    InitSessionMessage,
    UpdatedParagraphSessionMessage,
    ParagraphGoneSessionMessage,
    ReorderedParagraphsSessionMessage,
]


@serde(
    tagging=AdjacentTagging("@type", "@content"),
    rename_all="camelcase",
)
@dataclass
class ServerToClientMessageWrapper:
    inner: ServerToClientMessage

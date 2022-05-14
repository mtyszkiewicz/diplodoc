from dataclasses import dataclass
from typing import Protocol, Union


from serde import AdjacentTagging, serde
from uuid import uuid4, UUID

# Server-side messages
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


# Client-side messages
@serde
@dataclass
class UpdateParagraphSessionMessage:
    session_id: UUID
    paragraph_id: UUID
    content: str
    client_id: UUID


@serde
@dataclass
class CreateParagraphSessionMessage:
    session_id: UUID
    client_id: UUID


@serde
@dataclass
class ParagraphGoneSessionMessage:
    session_id: UUID
    paragraph_id: UUID
    client_id: UUID
    deleted_by: UUID

@serde
@dataclass
class DeleteParagraphSessionMessage:
    session_id: UUID
    paragraph_id: UUID
    client_id: UUID


@serde(tagging=AdjacentTagging("type", "content"))
@dataclass
class ClientToServerSessionMessage:
    inner: Union[UpdateParagraphSessionMessage, CreateParagraphSessionMessage, DeleteParagraphSessionMessage]


@serde(tagging=AdjacentTagging("type", "content"))
@dataclass
class ServerToClientSessionMessage:
    inner: Union[InitSessionMessage, UpdatedParagraphSessionMessage, ParagraphGoneSessionMessage]


SessionMessage = ClientToServerSessionMessage | ServerToClientSessionMessage


class ClientDispachableMessage(Protocol):
    client_id: UUID

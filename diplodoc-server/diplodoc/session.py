import asyncio
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from diplodoc.lock import Lock
from diplodoc.message import (
    InitMessage, 
    JoinMessage, 
    FreedMessage, 
    LeaveMessage,
    InitSessionMessage,
    ParagraphGoneSessionMessage,
    UpdatedParagraphSessionMessage,
)


@dataclass
class Paragraph:
    last_updated_by: UUID
    paragraph_id: UUID = field(default_factory=uuid4)
    lock: Lock = field(default_factory=Lock)
    content: str = str()


@dataclass
class Session:
    session_id: UUID = field(default_factory=uuid4)
    paragraphs: dict[UUID, Paragraph] = field(default_factory=dict)
    client_ids: set[UUID] = field(default_factory=set)

    async def join(
        self, client_id: UUID
    ) -> list[InitSessionMessage | UpdatedParagraphSessionMessage | InitMessage]:
        """Creates all messages required to initialize the session."""
        result = []

        result.append(
            InitSessionMessage(session_id=self.session_id, client_id=client_id)
        )
        self.client_ids.add(client_id)

        for paragraph in self.paragraphs.values():
            result.extend(
                paragraph.lock.handle(
                    JoinMessage(lock_id=paragraph.lock.lock_id, client_id=client_id)
                )
            )
            result.append(
                UpdatedParagraphSessionMessage(
                    session_id=self.session_id,
                    paragraph_id=paragraph.paragraph_id,
                    content=paragraph.content,
                    client_id=client_id,
                    updated_by=paragraph.last_updated_by,
                )
            )

        return result

    def update_paragraph(
        self, paragraph_id: UUID, content: str, client_id: UUID
    ) -> list[UpdatedParagraphSessionMessage]:
        if self.paragraphs[paragraph_id].lock.locked_by != client_id:
            raise RuntimeError("Inconsistent state.")

        self.paragraphs[paragraph_id].content = content
        self.paragraphs[paragraph_id].last_updated_by = client_id
        return [
            UpdatedParagraphSessionMessage(
                session_id=self.session_id,
                paragraph_id=paragraph_id,
                content=content,
                client_id=cid,
                updated_by=client_id,
            )
            for cid in self.client_ids
        ]

    async def create_paragraph(
        self, client_id: UUID
    ) -> list[UpdatedParagraphSessionMessage | InitMessage]:
        lock = Lock(locked_by=client_id)
        paragraph = Paragraph(
            paragraph_id=lock.lock_id,
            lock=lock,
            last_updated_by=client_id,
        )
        self.paragraphs[paragraph.paragraph_id] = paragraph

        result = []
        for cid in self.client_ids:
            result.extend(
                lock.handle(JoinMessage(lock_id=lock.lock_id, client_id=cid))
            )
            result.append(
                UpdatedParagraphSessionMessage(
                    session_id=self.session_id,
                    paragraph_id=paragraph.paragraph_id,
                    content=paragraph.content,
                    client_id=cid,
                    updated_by=client_id,
                )
            )
        return result

    async def delete_paragraph(
        self, paragraph_id: UUID, client_id: UUID
    ) -> list[ParagraphGoneSessionMessage]:
        if paragraph_id not in self.paragraphs:
            return []
        del self.paragraphs[paragraph_id]
        return [
            ParagraphGoneSessionMessage(
                session_id=self.session_id,
                paragraph_id=paragraph_id,
                client_id=cid,
                deleted_by=client_id,
            )
            for cid in self.client_ids
        ]

    async def leave(self, client_id: UUID) -> list[FreedMessage]:
        try:
            self.client_ids.remove(client_id)
        except KeyError:
            pass
        result = []
        for paragraph in self.paragraphs.values():
            result.extend(
                paragraph.lock.handle(
                    LeaveMessage(lock_id=paragraph.paragraph_id, client_id=client_id)
                )
            )
        return result

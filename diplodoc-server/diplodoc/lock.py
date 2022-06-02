from asyncio import Event
from dataclasses import dataclass, field
from typing import Awaitable, Optional
from uuid import UUID, uuid4

from diplodoc.message import (
    BusyMessage,
    FreedMessage,
    FreeMessage,
    InitMessage,
    JoinMessage,
    LeaveMessage,
    ReadyMessage,
    TryMessage,
)


@dataclass
class Lock:
    lock_id: UUID = field(default_factory=uuid4)
    locked_by: Optional[UUID] = None
    _client_ids: set[UUID] = field(default_factory=set)

    def _try_handler(self, msg: TryMessage) -> list[ReadyMessage | BusyMessage]:
        """Handle the locking for both busy and free lock.

        If the lock is already busy, only the trying client will be notified.
        If the lock is free, the lock will be locked by the trying client,
        and all other clients will be notified.
        """
        result = []
        if self.locked_by is None:
            self.locked_by = msg.client_id
            result.append(ReadyMessage(lock_id=self.lock_id, client_id=msg.client_id))
            for client_id in self._client_ids:
                if client_id == msg.client_id:
                    continue
                result.append(
                    BusyMessage(
                        lock_id=self.lock_id,
                        client_id=client_id,
                        locked_by=self.locked_by,
                    )
                )
        elif self.locked_by != msg.client_id:
            result.append(
                BusyMessage(
                    lock_id=self.lock_id,
                    client_id=msg.client_id,
                    locked_by=self.locked_by,
                )
            )

        return result

    def _free_handler(self, msg: FreeMessage) -> list[FreedMessage]:
        result = []
        if self.locked_by == msg.client_id:
            self.locked_by = None
            for client_id in self._client_ids:
                result.append(
                    FreedMessage(
                        lock_id=self.lock_id,
                        client_id=client_id,
                    )
                )
        return result

    def _join_handler(self, msg: JoinMessage) -> list[InitMessage]:
        self._client_ids.add(msg.client_id)
        return [
            InitMessage(
                lock_id=self.lock_id,
                client_id=msg.client_id,
                locked_by=self.locked_by,
            )
        ]

    def _leave_handler(self, msg: LeaveMessage) -> list[FreedMessage]:
        result = []
        if msg.client_id in self._client_ids:
            self._client_ids.remove(msg.client_id)
        if self.locked_by == msg.client_id:
            self.locked_by = None
            result.extend(
                [
                    FreedMessage(
                        lock_id=self.lock_id,
                        client_id=cid,
                    )
                    for cid in self._client_ids
                ]
            )
        return result

    def handle(
        self, msg: TryMessage | FreeMessage | JoinMessage | LeaveMessage
    ) -> list[ReadyMessage | BusyMessage] | list[InitMessage] | list[FreedMessage]:
        """Dispatch a message to the appropriate handler."""

        match msg:
            case TryMessage():
                result = self._try_handler(msg)
            case FreeMessage():
                result = self._free_handler(msg)
            case JoinMessage():
                result = self._join_handler(msg)
            case LeaveMessage():
                result = self._leave_handler(msg)
            case _:
                assert False, "unreachable"
        
        return result

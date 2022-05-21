from asyncio import Event, Queue
from dataclasses import dataclass, field
from typing import Awaitable, Optional
from uuid import UUID, uuid4

from diplodoc.message import (
    BusyMessage,
    ClientToServerMessageWrapper,
    FreedMessage,
    FreeMessage,
    InitMessage,
    JoinMessage,
    LeaveMessage,
    ReadyMessage,
    ServerToClientMessageWrapper,
    TryMessage,
)


@dataclass
class Lock:
    lock_id: UUID = field(default_factory=uuid4)
    locked_by: Optional[UUID] = None
    _client_ids: set[UUID] = field(default_factory=set)
    _queue_c2s: Queue[tuple[Event, Event]] = field(default_factory=Queue)

    async def _try_handler(
        self, msg: TryMessage, start_event: Event, end_event: Event
    ) -> list[FreedMessage]:
        """Handle the locking for both busy and free lock.

        If the lock is already busy, only the trying client will be notified.
        If the lock is free, the lock will be locked by the trying client,
        and all other clients will be notified.
        """
        await start_event.wait()
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
        else:
            result.append(
                BusyMessage(
                    lock_id=self.lock_id,
                    client_id=msg.client_id,
                    locked_by=self.locked_by,
                )
            )

        end_event.set()
        return result

    async def _free_handler(
        self, msg: FreeMessage, start_event: Event, end_event: Event
    ) -> list[FreedMessage]:
        await start_event.wait()
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
        end_event.set()
        return result

    async def _join_handler(
        self, msg: JoinMessage, start_event: Event, end_event: Event
    ) -> list[InitMessage]:
        await start_event.wait()
        result = [
            InitMessage(
                lock_id=self.lock_id,
                client_id=msg.client_id,
                locked_by=self.locked_by,
            )
        ]
        self._client_ids.add(msg.client_id)
        end_event.set()
        return result

    async def _leave_handler(
        self, msg: LeaveMessage, start_event: Event, end_event: Event
    ) -> list[FreedMessage]:
        await start_event.wait()
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
        end_event.set()
        return result

    def _schedule_handle(
        self, msg: ClientToServerMessageWrapperWrapper | JoinMessage | LeaveMessage
    ) -> Awaitable[list[ServerToClientMessageWrapper]]:
        """Dispatch a message to the appropriate handler."""
        start_ev = Event()
        end_ev = Event()
        match msg:
            case TryMessage():
                task = self._try_handler(msg, start_ev, end_ev)
            case FreeMessage():
                task = self._free_handler(msg, start_ev, end_ev)
            case JoinMessage():
                task = self._join_handler(msg, start_ev, end_ev)
            case LeaveMessage():
                task = self._leave_handler(msg, start_ev, end_ev)
            case _:
                assert False, "unreachable"
        self._queue_c2s.put_nowait((start_ev, end_ev))
        return task

    async def run(self):
        while True:
            start_ev, end_ev = await self._queue_c2s.get()
            start_ev.set()
            await end_ev.wait()

    async def handle(
        self, msg: ClientToServerMessageWrapperWrapper | JoinMessage | LeaveMessage
    ) -> list[ServerToClientMessageWrapper]:
        return await self._schedule_handle(msg)

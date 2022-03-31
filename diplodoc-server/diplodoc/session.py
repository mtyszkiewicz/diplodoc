from asyncio import Event, Queue
from dataclasses import dataclass, field
from typing import Awaitable, Optional

from diplodoc.message import (
    AckMessage,
    ClientToServerMessage,
    PopMessage,
    PushMessage,
    ServerToClientMessage,
)
from diplodoc.state import TextState


@dataclass
class Session:
    _text: TextState = field(default_factory=TextState)
    _queue_c2s: Queue[tuple[Event, Event]] = field(default_factory=Queue)
    # _timestamp: int = 0
    # _last_seen: dict[int, int] = field(default_factory=dict)

    async def _push_handler(
        self, msg: PushMessage, start_event: Event, end_event: Event
    ) -> AckMessage:
        await start_event.wait()
        self._text.push(msg.pos, msg.c)
        end_event.set()
        return AckMessage(
            buf=str(self._text),
            timestamp=0,  # TODO
        )

    async def _pop_handler(
        self, msg: PopMessage, start_event: Event, end_event: Event
    ) -> AckMessage:
        await start_event.wait()
        self._text.pop(msg.pos)
        end_event.set()
        return AckMessage(
            buf=str(self._text),
            timestamp=0,  # TODO
        )

    def _schedule_handle(
        self, msg: ClientToServerMessage
    ) -> Awaitable[Optional[ClientToServerMessage]]:
        start_ev = Event()
        end_ev = Event()
        match msg:
            case PushMessage():
                task = self._push_handler(msg, start_ev, end_ev)
            case PopMessage():
                task = self._pop_handler(msg, start_ev, end_ev)
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
        self, msg: ClientToServerMessage
    ) -> Optional[ServerToClientMessage]:
        return await self._schedule_handle(msg)

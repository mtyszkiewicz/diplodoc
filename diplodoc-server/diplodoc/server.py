import logging
import sys
from argparse import ArgumentParser
from dataclasses import dataclass, field
from typing import Iterable
from uuid import UUID, uuid4

import aiohttp
import aiohttp.web
from rich import print
from serde.compat import SerdeError
from serde.json import from_json, to_json

from diplodoc.message import (
    ClientToServerMessageWrapper,
    CreateParagraphSessionMessage,
    DeleteParagraphSessionMessage,
    FreeMessage,
    ServerToClientMessage,
    ServerToClientMessageWrapper,
    TryMessage,
    UpdateParagraphSessionMessage,
)
from diplodoc.session import Session

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


@dataclass
class Application:
    _app: aiohttp.web.Application
    _session: Session = field(default_factory=Session)
    _client_sockets: dict[UUID, aiohttp.web.WebSocketResponse] = field(
        default_factory=dict
    )

    async def handler(self, request: aiohttp.web.Request) -> aiohttp.web.StreamResponse:
        ws = aiohttp.web.WebSocketResponse()
        await ws.prepare(request)

        client_id = uuid4()
        init_messages = await self._session.join(client_id)
        self._client_sockets[client_id] = ws
        await self._send_messages(ws, init_messages)

        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        message = from_json(ClientToServerMessageWrapper, msg.data).inner
                    except SerdeError:
                        print(f"Error: Could not parse message: {msg.data}")
                        continue

                    if isinstance(message, CreateParagraphSessionMessage):
                        await self._create_paragraph_handler(message)

                    elif isinstance(message, UpdateParagraphSessionMessage):
                        await self._update_paragraph_handler(message)

                    elif isinstance(message, (TryMessage, FreeMessage)):
                        await self._lock_message_handler(message)

                    elif isinstance(message, DeleteParagraphSessionMessage):
                        await self._delete_paragraph_handler(message)

                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logging.info(
                        f"WebSocket connection closed with exception {ws.exception()}"
                    )
        finally:
            del self._client_sockets[client_id]
            await ws.close()
            await self._dispatch_and_send_messages(await self._session.leave(client_id))
            print(f"Disconnected client {client_id}")

        logging.info("WebSocket connection closed")
        return ws

    @staticmethod
    async def _send_messages(
        ws: aiohttp.web.WebSocketResponse,
        messages: Iterable[ServerToClientMessage],
    ):
        for message in messages:
            await ws.send_str(to_json(ServerToClientMessageWrapper(message)))

    async def _dispatch_and_send_messages(
        self, messages: Iterable[ServerToClientMessage]
    ):
        for message in messages:
            try:
                ws = self._client_sockets[message.client_id]
            except KeyError:
                continue
            await self._send_messages(ws, [message])

    async def _create_paragraph_handler(self, message: CreateParagraphSessionMessage):
        messages = await self._session.create_paragraph(message.client_id)
        await self._dispatch_and_send_messages(messages)

    async def _update_paragraph_handler(self, message: UpdateParagraphSessionMessage):
        messages = self._session.update_paragraph(
            message.paragraph_id, message.content, message.client_id
        )
        await self._dispatch_and_send_messages(messages)

    async def _lock_message_handler(self, message: TryMessage | FreeMessage):
        messages = self._session.paragraphs[message.lock_id].lock.handle(message)
        await self._dispatch_and_send_messages(messages)

    async def _delete_paragraph_handler(self, message: DeleteParagraphSessionMessage):
        messages = await self._session.delete_paragraph(
            message.paragraph_id, message.client_id
        )
        await self._dispatch_and_send_messages(messages)


def main() -> None:
    argparser = ArgumentParser(__name__)
    argparser.add_argument("--host", type=str, default="0.0.0.0")
    argparser.add_argument("--port", type=int, default=8887)
    args = argparser.parse_args()
    app = aiohttp.web.Application()
    diplodoc_app = Application(app)
    app.add_routes([aiohttp.web.get("/", diplodoc_app.handler)])
    aiohttp.web.run_app(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()

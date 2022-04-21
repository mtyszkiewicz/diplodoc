import aiohttp
import aiohttp.web
import asyncio
import logging
import sys
from serde.json import from_json, to_json
from diplodoc.message import (
    AckMessage,
    ClientToServerMessage,
    HelloMessage,
    PushMessage,
    ServerToClientMessage,
    YoMessage,
)
from serde.compat import SerdeError
from diplodoc.session import Session

session = Session()
next_client_id = 0

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


async def handler(request: aiohttp.web.Request) -> aiohttp.web.StreamResponse:
    global next_client_id
    global session
    ws = aiohttp.web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        print(f"Received message from mikolaj: {msg}")
        if msg.type == aiohttp.WSMsgType.TEXT:
            message = from_json(ClientToServerMessage, msg.data).inner

            if isinstance(message, YoMessage):
                client_id = next_client_id
                next_client_id += 69
                response = ServerToClientMessage(HelloMessage(client_token=str(client_id)))
                await ws.send_str(to_json(response))
                response = ServerToClientMessage(AckMessage(buf=str(session._text._buf), timestamp=0))
                await ws.send_str(to_json(response))

            elif isinstance(message, PushMessage):
                ack = await session.handle(message)
                response = ServerToClientMessage(ack)
                await ws.send_str(to_json(response))

        elif msg.type == aiohttp.WSMsgType.ERROR:
            logging.info(f"WebSocket connection closed with exception {ws.exception()}")

    logging.info("WebSocket connection closed")
    return ws


async def main():
    global session
    asyncio.create_task(session.run())


if __name__ == "__main__":
    app = aiohttp.web.Application()

    app.add_routes([aiohttp.web.get("/", handler)])

    app.startup = main
    aiohttp.web.run_app(app, host="10.0.0.3", port=8887)

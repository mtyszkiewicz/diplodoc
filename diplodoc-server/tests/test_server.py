from asyncio import create_task

import pytest
import pytest_asyncio.plugin

from diplodoc.message import AckMessage, PopMessage, PushMessage
from diplodoc.session import Session


@pytest.mark.asyncio
async def test_push():
    server = Session()
    run_task = create_task(server.run())
    c2s = PushMessage(c="diplodoc", pos=0, timestamp=0)
    s2c = await server.handle(c2s)
    assert isinstance(s2c, AckMessage)
    assert s2c.buf == "diplodoc"
    run_task.cancel()


@pytest.mark.asyncio
async def test_pop():
    server = Session()
    run_task = create_task(server.run())
    c2s = PushMessage(c="diplodoc", pos=0, timestamp=0)
    s2c = await server.handle(c2s)
    c2s = PopMessage(pos=0, timestamp=1)
    s2c = await server.handle(c2s)
    assert s2c.buf == "iplodoc"
    run_task.cancel()

from dataclasses import dataclass
from typing import Union

from serde import AdjacentTagging, serde


@serde
@dataclass
class PushMessage:
    c: str
    pos: int
    timestamp: int


@serde
@dataclass
class PopMessage:
    pos: int
    timestamp: int


@serde
@dataclass
class YoMessage:
    pass


@serde
@dataclass
class AckMessage:
    buf: str
    timestamp: int


@serde
@dataclass
class HelloMessage:
    client_token: str


@serde
@dataclass
class HellAck:
    pass  # TODO


@serde
@dataclass
class LogMessage:
    message: str


@serde(tagging=AdjacentTagging("type", "content"))
@dataclass
class ClientToServerMessage:
    inner: Union[PushMessage, PopMessage, YoMessage]


@serde(tagging=AdjacentTagging("type", "content"))
@dataclass
class ServerToClientMessage:
    inner: Union[AckMessage, HelloMessage, LogMessage]


Message = ClientToServerMessage | ServerToClientMessage
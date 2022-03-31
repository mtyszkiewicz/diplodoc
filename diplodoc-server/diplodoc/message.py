from dataclasses import dataclass


@dataclass
class PushMessage:
    c: str
    pos: int
    timestamp: int


@dataclass
class PopMessage:
    pos: int
    timestamp: int


@dataclass
class YoMessage:
    pass


@dataclass
class AckMessage:
    buf: str
    timestamp: int


@dataclass
class HelloMessage:
    client_token: str


@dataclass
class LogMessage:
    message: str


ClientToServerMessage = PushMessage | PopMessage

ServerToClientMessage = AckMessage | HelloMessage | LogMessage

Message = ClientToServerMessage | ServerToClientMessage

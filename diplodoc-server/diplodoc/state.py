from dataclasses import dataclass


@dataclass
class TextState:
    _buf: str = str()

    def push(self, pos: int, c: str) -> None:
        if pos < 0 or pos > len(self._buf):
            raise ValueError("position out of range")
        if not c:
            raise ValueError("cannot push empty string")
        self._buf = "".join(
            (
                self._buf[:pos],
                c,
                self._buf[pos:],
            )
        )

    def pop(self, pos: int) -> str:
        if pos < 0 or pos >= len(self._buf):
            raise ValueError("position out of range")
        result = self._buf[pos]
        self._buf = self._buf[:pos] + self._buf[pos + 1 :]
        return result

    def __str__(self) -> str:
        return self._buf

from blissdata.redis_engine.exceptions import EndOfStream
from blissdata.redis_engine.scan import ScanState
from unittest.mock import MagicMock
import numpy as np


class FakeCursor:
    def __init__(self, arrays):
        self._arrays = arrays
        self._i = 0

    def read(self):
        if self._i >= len(self._arrays):
            raise EndOfStream()
        arr = np.array(self._arrays[self._i])
        self._i += 1
        return MagicMock(get_data=lambda: arr)


class FakeStream:
    def __init__(self, arrays):
        self._arrays = arrays

    def cursor(self):
        return FakeCursor(self._arrays)


class FakeScan:
    def __init__(self, arrays, title):
        self.info = {"title": title}
        self.streams = {f"{title}:image": FakeStream(arrays)}
        self.state = ScanState.CLOSED

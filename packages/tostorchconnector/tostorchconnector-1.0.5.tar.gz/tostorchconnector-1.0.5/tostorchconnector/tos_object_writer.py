import io
import logging
import threading
from typing import Callable, Any, Union

from tos.models2 import PutObjectOutput

log = logging.getLogger(__name__)


class PutObjectStream(object):
    def __init__(self, put_object: Callable[[io.BytesIO], PutObjectOutput]):
        self._put_object = put_object
        self._buffer = io.BytesIO()
        self._closed = False

    def write(self, data) -> int:
        if self._closed:
            raise RuntimeError('write on closed PutObjectStream')
        self._buffer.write(data)
        return len(data)

    def close(self):
        self._closed = True
        self._buffer.seek(0)
        _ = self._put_object(self._buffer)


class TosObjectWriter(io.BufferedIOBase):

    def __init__(self, bucket: str, key: str, put_object_stream: Any):
        if not bucket:
            raise ValueError('bucket is empty')
        self._bucket = bucket
        self._key = key
        self._put_object_stream = put_object_stream
        self._write_offset = 0
        self._closed = False
        self._lock = threading.Lock()

    @property
    def bucket(self) -> str:
        return self._bucket

    @property
    def key(self) -> str:
        return self._key

    @property
    def closed(self) -> bool:
        return self._closed

    def __enter__(self):
        self._write_offset = 0
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            try:
                log.info(f'Exception occurred before closing stream: {exc_type.__name__}: {exc_val}')
            except:
                pass
        else:
            self.close()

    def write(self, data: Union[bytes, memoryview]) -> int:
        if isinstance(data, memoryview):
            data = data.tobytes()
        written = self._put_object_stream.write(data)
        assert written == len(data)
        self._write_offset += written
        return written

    def close(self) -> None:
        if self._closed:
            return

        with self._lock:
            if not self._closed:
                self._closed = True
                self._put_object_stream.close()

    def tell(self) -> int:
        return self._write_offset

    def flush(self) -> None:
        pass

    def readable(self) -> bool:
        return False

    def writable(self) -> bool:
        return not self.closed

    def seekable(self) -> bool:
        return False

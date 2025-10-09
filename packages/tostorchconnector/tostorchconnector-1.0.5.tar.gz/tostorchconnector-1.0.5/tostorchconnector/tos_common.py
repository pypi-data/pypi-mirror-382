import logging
from typing import Union, Iterator, Tuple, Optional

from . import TosObjectReader
from .tos_client import TosClient
from .tos_object_meta import TosObjectMeta

log = logging.getLogger(__name__)


class TosObjectIterator(object):
    def __init__(self, bucket: str, prefix: str, client: TosClient):
        self._bucket = bucket
        self._prefix = prefix
        self._client = client
        self._delimiter: Optional[str] = None
        self._list_stream = None

        self._object_metas = None
        self._index = 0

        self._is_truncated = True
        self._continuation_token = None

    def close(self) -> None:
        if self._list_stream is not None:
            self._list_stream.close()

    def __iter__(self) -> Iterator[TosObjectMeta]:
        return self

    def __next__(self) -> TosObjectMeta:
        if self._client.use_native_client:
            if self._list_stream is None:
                self._list_stream = self._client.gen_list_stream(self._bucket, self._prefix, max_keys=1000,
                                                                 delimiter=self._delimiter)

            if self._object_metas is None or self._index >= len(self._object_metas):
                self._object_metas = []
                self._index = 0
                while 1:
                    objects = next(self._list_stream)
                    for content in objects.contents:
                        self._object_metas.append(
                            TosObjectMeta(content.bucket, content.key, content.size, content.etag))
                    if len(self._object_metas) > 0:
                        break

            object_meta = self._object_metas[self._index]
            self._index += 1
            return object_meta

        while self._object_metas is None or self._index >= len(self._object_metas):
            if not self._is_truncated:
                raise StopIteration
            self._object_metas, self._is_truncated, self._continuation_token = self._client.list_objects(
                self._bucket,
                self._prefix,
                max_keys=1000,
                continuation_token=self._continuation_token,
                delimiter=self._delimiter)
            self._index = 0

        object_meta = self._object_metas[self._index]
        self._index += 1
        return object_meta


def parse_tos_url(url: str) -> Tuple[str, str]:
    if not url:
        raise ValueError('url is empty')

    if url.startswith('tos://'):
        url = url[len('tos://'):]

    if not url:
        raise ValueError('bucket is empty')

    url = url.split('/', maxsplit=1)
    if len(url) == 1:
        bucket = url[0]
        prefix = ''
    else:
        bucket = url[0]
        prefix = url[1]

    if not bucket:
        raise ValueError('bucket is empty')
    return bucket, prefix


def default_trans(obj: TosObjectReader) -> TosObjectReader:
    return obj


def gen_dataset_from_urls(urls: Union[str, Iterator[str]], _: TosClient) -> Iterator[TosObjectMeta]:
    if isinstance(urls, str):
        urls = [urls]
    return (TosObjectMeta(bucket, key) for bucket, key in [parse_tos_url(url) for url in urls])


def gen_dataset_from_prefix(prefix: str, client: TosClient) -> Iterator[TosObjectMeta]:
    bucket, prefix = parse_tos_url(prefix)
    return iter(TosObjectIterator(bucket, prefix, client))

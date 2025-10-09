import enum
import logging
import os
from functools import partial
from typing import Optional, List, Tuple

import tos

import tosnativeclient

from . import SequentialTosObjectReader, TosObjectWriter, TosObjectReader
from .tos_object_meta import TosObjectMeta
from .tos_object_reader import TosObjectStream, RangedTosObjectReader
from .tos_object_writer import PutObjectStream

log = logging.getLogger(__name__)


class ReaderType(enum.Enum):
    SEQUENTIAL = 'Sequential'
    RANGED = 'Ranged'


class CredentialProvider(object):
    def __init__(self, ak: str, sk: str):
        self._ak = ak
        self._sk = sk

    @property
    def ak(self) -> str:
        return self._ak

    @property
    def sk(self) -> str:
        return self._sk


class TosClientConfig(object):
    def __init__(self, part_size: int = 8 * 1024 * 1024,
                 max_retry_count: int = 3, shared_prefetch_tasks: int = 20):
        self._part_size = part_size
        self._max_retry_count = max_retry_count
        self._shared_prefetch_tasks = shared_prefetch_tasks

    @property
    def part_size(self) -> int:
        return self._part_size

    @property
    def max_retry_count(self) -> int:
        return self._max_retry_count

    @property
    def shared_prefetch_tasks(self) -> int:
        return self._shared_prefetch_tasks


class TosLogConfig(object):
    def __init__(self, log_dir: str = '',
                 log_file_name: str = '', log_level: Optional[int] = logging.INFO):
        self._log_dir = log_dir
        self._log_file_name = log_file_name
        self._log_level = log_level

    @property
    def log_level(self) -> Optional[int]:
        return self._log_level

    @property
    def log_dir(self) -> str:
        return self._log_dir

    @property
    def log_file_name(self) -> str:
        return self._log_file_name


class TosClient(object):
    def __init__(self, region: str, endpoint: Optional[str] = None, cred: Optional[CredentialProvider] = None,
                 client_conf: Optional[TosClientConfig] = None, log_conf: Optional[TosLogConfig] = None,
                 use_native_client: bool = True):
        cred = CredentialProvider('', '') if cred is None else cred
        client_conf = TosClientConfig() if client_conf is None else client_conf
        log_conf = TosLogConfig() if log_conf is None else log_conf
        self._part_size = client_conf.part_size
        self._use_native_client = use_native_client
        if use_native_client:
            directives = ''
            directory = ''
            file_name_prefix = ''
            if log_conf.log_dir and log_conf.log_file_name:
                if log_conf.log_level:
                    if log_conf.log_level == logging.DEBUG:
                        directives = 'debug'
                    elif log_conf.log_level == logging.INFO:
                        directives = 'info'
                    elif log_conf.log_level == logging.WARN:
                        directives = 'warn'
                    elif log_conf.log_level == logging.ERROR:
                        directives = 'error'
                    else:
                        directives = 'info'
                directory = log_conf.log_dir
                file_name_prefix = log_conf.log_file_name
            self._client = tosnativeclient.TosClient(region, endpoint, cred.ak, cred.sk, client_conf.part_size,
                                                     client_conf.max_retry_count, directives=directives,
                                                     directory=directory,
                                                     file_name_prefix=file_name_prefix)
        else:
            self._client = tos.TosClientV2(cred.ak, cred.sk, endpoint=endpoint, region=region,
                                           max_retry_count=client_conf.max_retry_count)
            if log_conf.log_dir and log_conf.log_file_name:
                file_path = os.path.join(log_conf.log_dir, log_conf.log_file_name)
                log_level = log_conf.log_level if log_conf.log_level else logging.INFO
                tos.set_logger(file_path=file_path, level=log_level)

    @property
    def use_native_client(self) -> bool:
        return self._use_native_client

    def get_object(self, bucket: str, key: str, etag: Optional[str] = None,
                   size: Optional[int] = None, reader_type: Optional[ReaderType] = None,
                   buffer_size: Optional[int] = None) -> TosObjectReader:
        log.debug(f'get_object tos://{bucket}/{key}')

        if size is None or etag is None:
            get_object_meta = partial(self.head_object, bucket, key)
        else:
            get_object_meta = lambda: TosObjectMeta(bucket, key, size, etag)

        object_stream = TosObjectStream(bucket, key, get_object_meta, self._client)
        if reader_type is not None and reader_type == ReaderType.RANGED:
            return RangedTosObjectReader(bucket, key, object_stream, buffer_size)
        return SequentialTosObjectReader(bucket, key, object_stream)

    def put_object(self, bucket: str, key: str, storage_class: Optional[str] = None) -> TosObjectWriter:
        log.debug(f'put_object tos://{bucket}/{key}')

        if isinstance(self._client, tosnativeclient.TosClient):
            put_object_stream = self._client.put_object(bucket, key, storage_class=storage_class)
        else:
            put_object_stream = PutObjectStream(
                lambda content: self._client.put_object(bucket, key, storage_class=storage_class, content=content))

        return TosObjectWriter(bucket, key, put_object_stream)

    def head_object(self, bucket: str, key: str) -> TosObjectMeta:
        log.debug(f'head_object tos://{bucket}/{key}')

        if isinstance(self._client, tosnativeclient.TosClient):
            resp = self._client.head_object(bucket, key)
            return TosObjectMeta(resp.bucket, resp.key, resp.size, resp.etag)

        resp = self._client.head_object(bucket, key)
        return TosObjectMeta(bucket, key, resp.content_length, resp.etag)

    def gen_list_stream(self, bucket: str, prefix: str, max_keys: int = 1000,
                        delimiter: Optional[str] = None) -> tosnativeclient.ListStream:
        log.debug(f'gen_list_stream tos://{bucket}/{prefix}')

        if isinstance(self._client, tosnativeclient.TosClient):
            delimiter = delimiter if delimiter is not None else ''
            return self._client.list_objects(bucket, prefix, max_keys=max_keys, delimiter=delimiter)
        raise NotImplementedError()

    def list_objects(self, bucket: str, prefix: str, max_keys: int = 1000,
                     continuation_token: Optional[str] = None, delimiter: Optional[str] = None) -> Tuple[
        List[TosObjectMeta], bool, Optional[str]]:
        log.debug(f'list_objects tos://{bucket}/{prefix}')

        if isinstance(self._client, tosnativeclient.TosClient):
            raise NotImplementedError()

        resp = self._client.list_objects_type2(bucket, prefix, max_keys=max_keys, continuation_token=continuation_token,
                                               delimiter=delimiter)
        object_metas = []
        for obj in resp.contents:
            object_metas.append(TosObjectMeta(bucket, obj.key, obj.size, obj.etag))
        return object_metas, resp.is_truncated, resp.next_continuation_token

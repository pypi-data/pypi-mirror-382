import logging
from functools import partial
from typing import Iterator, Any, Optional, Callable, Union

import torch

from . import TosObjectReader
from .tos_client import CredentialProvider, TosClientConfig, TosClient, TosLogConfig, ReaderType
from .tos_common import default_trans, gen_dataset_from_urls, gen_dataset_from_prefix
from .tos_object_meta import TosObjectMeta

log = logging.getLogger(__name__)


class TosIterableDataset(torch.utils.data.IterableDataset):
    def __init__(self, region: str,
                 gen_dataset: Callable[[TosClient], Iterator[TosObjectMeta]],
                 endpoint: Optional[str] = None,
                 trans: Callable[[TosObjectReader], Any] = default_trans,
                 cred: Optional[CredentialProvider] = None,
                 client_conf: Optional[TosClientConfig] = None,
                 log_conf: Optional[TosLogConfig] = None,
                 sharding: bool = False,
                 use_native_client: bool = True,
                 reader_type: Optional[ReaderType] = None,
                 buffer_size: Optional[int] = None):
        self._gen_dataset = gen_dataset
        self._region = region
        self._endpoint = endpoint
        self._trans = trans
        self._cred = cred
        self._client_conf = client_conf
        self._log_conf = log_conf
        self._sharding = sharding
        if torch.distributed.is_initialized():
            self._rank = torch.distributed.get_rank()
            self._world_size = torch.distributed.get_world_size()
        else:
            self._rank = 0
            self._world_size = 1
        self._reader_type = reader_type
        self._buffer_size = buffer_size
        self._client = TosClient(self._region, self._endpoint, self._cred, self._client_conf, self._log_conf,
                                 use_native_client)
        log.info('TosIterableDataset init tos client succeed')

    @classmethod
    def from_urls(cls, urls: Union[str, Iterator[str]], *, region: str, endpoint: Optional[str] = None,
                  transform: Callable[[TosObjectReader], Any] = default_trans,
                  cred: Optional[CredentialProvider] = None,
                  client_conf: Optional[TosClientConfig] = None,
                  log_conf: Optional[TosLogConfig] = None,
                  sharding: bool = False,
                  use_native_client: bool = True,
                  reader_type: Optional[ReaderType] = None,
                  buffer_size: Optional[int] = None):
        log.info(f'building {cls.__name__} from_urls')
        return cls(region, partial(gen_dataset_from_urls, urls), endpoint, transform, cred, client_conf, log_conf,
                   sharding, use_native_client, reader_type, buffer_size)

    @classmethod
    def from_prefix(cls, prefix: str, *, region: str, endpoint: Optional[str] = None,
                    transform: Callable[[TosObjectReader], Any] = default_trans,
                    cred: Optional[CredentialProvider] = None,
                    client_conf: Optional[TosClientConfig] = None,
                    log_conf: Optional[TosLogConfig] = None,
                    sharding: bool = False,
                    use_native_client: bool = True,
                    reader_type: Optional[ReaderType] = None,
                    buffer_size: Optional[int] = None):
        log.info(f'building {cls.__name__} from_prefix')
        return cls(region, partial(gen_dataset_from_prefix, prefix), endpoint, transform, cred, client_conf, log_conf,
                   sharding, use_native_client, reader_type, buffer_size)

    def __iter__(self) -> Iterator[Any]:
        worker_id = 0
        num_workers = 1
        if self._sharding:
            worker_info = torch.utils.data.get_worker_info()
            if worker_info is not None:
                worker_id = worker_info.id
                num_workers = worker_info.num_workers

        if not self._sharding or (self._world_size == 1 and num_workers == 1):
            return map(
                self._trans_tos_object,
                self._gen_dataset(self._client),
            )

        part_dataset = (
            obj
            for idx, obj in enumerate(self._gen_dataset(self._client))
            if idx % self._world_size == self._rank
        )

        part_dataset = (
            obj
            for idx, obj in enumerate(part_dataset)
            if idx % num_workers == worker_id
        )
        return map(self._trans_tos_object, part_dataset)

    def _trans_tos_object(self, object_meta: TosObjectMeta) -> Any:
        obj = self._client.get_object(object_meta.bucket, object_meta.key, object_meta.etag, object_meta.size,
                                      reader_type=self._reader_type, buffer_size=self._buffer_size)
        return self._trans(obj)

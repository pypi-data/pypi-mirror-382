import logging
from functools import partial
from typing import Any, Callable, Iterator, Optional, List, Union

import torch

from . import TosObjectReader
from .tos_client import CredentialProvider, TosClientConfig, TosClient, TosLogConfig, ReaderType
from .tos_common import default_trans, gen_dataset_from_prefix, \
    gen_dataset_from_urls
from .tos_object_meta import TosObjectMeta

log = logging.getLogger(__name__)


class TosMapDataset(torch.utils.data.Dataset):
    def __init__(self, region: str,
                 gen_dataset: Callable[[TosClient], Iterator[TosObjectMeta]],
                 endpoint: Optional[str] = None,
                 trans: Callable[[TosObjectReader], Any] = default_trans,
                 cred: Optional[CredentialProvider] = None,
                 client_conf: Optional[TosClientConfig] = None,
                 log_conf: Optional[TosLogConfig] = None,
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
        self._dataset: Optional[List[TosObjectMeta]] = None
        self._reader_type = reader_type
        self._buffer_size = buffer_size
        self._client = TosClient(self._region, self._endpoint, self._cred, self._client_conf, self._log_conf,
                                 use_native_client)
        log.info('TosMapDataset init tos client succeed')

    @classmethod
    def from_urls(cls, urls: Union[str, Iterator[str]], *, region: str, endpoint: Optional[str] = None,
                  trans: Callable[[TosObjectReader], Any] = default_trans,
                  cred: Optional[CredentialProvider] = None,
                  client_conf: Optional[TosClientConfig] = None,
                  log_conf: Optional[TosLogConfig] = None,
                  use_native_client: bool = True,
                  reader_type: Optional[ReaderType] = None,
                  buffer_size: Optional[int] = None):
        log.info(f'building {cls.__name__} from_urls')
        return cls(region, partial(gen_dataset_from_urls, urls), endpoint, trans, cred, client_conf, log_conf,
                   use_native_client, reader_type, buffer_size)

    @classmethod
    def from_prefix(cls, prefix: str, *, region: str, endpoint: Optional[str] = None,
                    trans: Callable[[TosObjectReader], Any] = default_trans,
                    cred: Optional[CredentialProvider] = None,
                    client_conf: Optional[TosClientConfig] = None,
                    log_conf: Optional[TosLogConfig] = None,
                    use_native_client: bool = True,
                    reader_type: Optional[ReaderType] = None,
                    buffer_size: Optional[int] = None):
        log.info(f'building {cls.__name__} from_prefix')
        return cls(region, partial(gen_dataset_from_prefix, prefix), endpoint, trans, cred, client_conf, log_conf,
                   use_native_client, reader_type, buffer_size)

    def __getitem__(self, i: int) -> Any:
        return self._trans_tos_object(i)

    def __len__(self) -> int:
        return len(self._data_set)

    @property
    def _data_set(self) -> List[TosObjectMeta]:
        if self._dataset is None:
            self._dataset = list(self._gen_dataset(self._client))
        assert self._dataset is not None
        return self._dataset

    def _trans_tos_object(self, i: int) -> Any:
        object_meta = self._data_set[i]
        obj = self._client.get_object(object_meta.bucket, object_meta.key, object_meta.etag, object_meta.size,
                                      reader_type=self._reader_type, buffer_size=self._buffer_size)
        return self._trans(obj)

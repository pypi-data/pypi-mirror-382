import logging
from typing import Optional

from . import TosObjectReader, TosObjectWriter
from .tos_client import CredentialProvider, TosClientConfig, TosClient, TosLogConfig, ReaderType
from .tos_common import parse_tos_url

log = logging.getLogger(__name__)


class TosCheckpoint(object):
    def __init__(self, region: str,
                 endpoint: Optional[str] = None,
                 cred: Optional[CredentialProvider] = None,
                 client_conf: Optional[TosClientConfig] = None,
                 log_conf: Optional[TosLogConfig] = None, use_native_client=True):
        self._region = region
        self._endpoint = endpoint
        self._cred = cred
        self._client_conf = client_conf
        self._log_conf = log_conf
        self._client = TosClient(self._region, self._endpoint, self._cred, self._client_conf, self._log_conf,
                                 use_native_client)
        log.info('TosCheckpoint init tos client succeed')

    def reader(self, url: str, reader_type: Optional[ReaderType] = None,
               buffer_size: Optional[int] = None) -> TosObjectReader:
        bucket, key = parse_tos_url(url)
        return self._client.get_object(bucket, key, reader_type=reader_type, buffer_size=buffer_size)

    def writer(self, url: str) -> TosObjectWriter:
        bucket, key = parse_tos_url(url)
        return self._client.put_object(bucket, key)

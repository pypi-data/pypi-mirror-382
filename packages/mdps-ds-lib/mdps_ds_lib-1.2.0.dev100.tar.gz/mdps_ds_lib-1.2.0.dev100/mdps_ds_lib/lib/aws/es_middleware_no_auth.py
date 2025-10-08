import logging

from elasticsearch import Elasticsearch
from mdps_ds_lib.lib.aws.es_middleware_abstract import ESMiddlewareAbstract

LOGGER = logging.getLogger(__name__)


class ESMiddlewareNoAuth(ESMiddlewareAbstract):

    def __init__(self, index, base_url, port=443, use_ssl=True) -> None:
        super().__init__(index, base_url, port)
        base_url = base_url.replace('https://', '')  # hide https
        self._engine = Elasticsearch(hosts=[{'host': base_url, 'port': port}])

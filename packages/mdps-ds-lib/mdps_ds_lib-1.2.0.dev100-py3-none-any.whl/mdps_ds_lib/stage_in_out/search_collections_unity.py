import json
import logging
import os

from mdps_ds_lib.stage_in_out.dapa_client import DapaClient
from mdps_ds_lib.stage_in_out.search_collections_abstract import SearchCollectionsAbstract

LOGGER = logging.getLogger(__name__)


class SearchCollectionsUnity(SearchCollectionsAbstract):
    COLLECTION_ID_KEY = 'COLLECTION_ID'
    DOWNLOAD_DIR_KEY = 'DOWNLOAD_DIR'

    LIMITS_KEY = 'LIMITS'
    DATE_FROM_KEY = 'DATE_FROM'
    DATE_TO_KEY = 'DATE_TO'
    VERIFY_SSL_KEY = 'VERIFY_SSL'

    def __init__(self) -> None:
        super().__init__()
        self.__collection_id = ''
        self.__date_from = ''
        self.__date_to = ''
        self.__limit = 1000
        self.__verify_ssl = True

    def __set_props_from_env(self):
        missing_keys = [k for k in [self.COLLECTION_ID_KEY] if k not in os.environ]
        if len(missing_keys) > 0:
            raise ValueError(f'missing environment keys: {missing_keys}')

        self.__collection_id = os.environ.get(self.COLLECTION_ID_KEY)
        if self.LIMITS_KEY not in os.environ:
            LOGGER.warning(f'missing {self.LIMITS_KEY}. using default: {self.__limit}')
        else:
            self.__limit = int(os.environ.get(self.LIMITS_KEY))

        self.__date_from = os.environ.get(self.DATE_FROM_KEY, '')
        self.__date_to = os.environ.get(self.DATE_TO_KEY, '')
        self.__verify_ssl = os.environ.get(self.VERIFY_SSL_KEY, 'TRUE').strip().upper() == 'TRUE'
        return self

    def search(self, **kwargs):
        self.__set_props_from_env()
        dapa_client = DapaClient().with_verify_ssl(self.__verify_ssl)
        collections_result = dapa_client.get_collection(self.__collection_id)
        return json.dumps(collections_result)

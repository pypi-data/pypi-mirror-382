import json

from mdps_ds_lib.stage_in_out.stage_in_out_utils import StageInOutUtils

from mdps_ds_lib.stage_in_out.dapa_client import DapaClient
from mdps_ds_lib.lib.utils.time_utils import TimeUtils
from mdps_ds_lib.stage_in_out.catalog_granules_abstract import CatalogGranulesAbstract
import logging
import os

from mdps_ds_lib.stage_in_out.cataloging_granules_status_checker import CatalogingGranulesStatusChecker

LOGGER = logging.getLogger(__name__)


class CatalogGranulesUnity(CatalogGranulesAbstract):
    PROVIDER_ID_KEY = 'PROVIDER_ID'
    VERIFY_SSL_KEY = 'VERIFY_SSL'
    DELAY_SECOND = 'DELAY_SECOND'
    REPEAT_TIMES = 'REPEAT_TIMES'
    CHUNK_SIZE = 'CHUNK_SIZE'

    def __init__(self) -> None:
        super().__init__()
        self.__provider_id = ''
        self.__verify_ssl = True
        self.__delaying_second = 30
        self.__repeating_times = 0
        self.__chunk_size = StageInOutUtils.CATALOG_DEFAULT_CHUNK_SIZE

    def __set_props_from_env(self):
        missing_keys = [k for k in [self.UPLOADED_FILES_JSON, self.PROVIDER_ID_KEY] if k not in os.environ]
        if len(missing_keys) > 0:
            raise ValueError(f'missing environment keys: {missing_keys}')
        self._retrieve_stac_json()
        self.__chunk_size = int(os.environ.get(self.CHUNK_SIZE, StageInOutUtils.CATALOG_DEFAULT_CHUNK_SIZE))
        self.__chunk_size = self.__chunk_size if self.__chunk_size > 0 else StageInOutUtils.CATALOG_DEFAULT_CHUNK_SIZE
        self.__provider_id = os.environ.get(self.PROVIDER_ID_KEY)
        self.__verify_ssl = os.environ.get(self.VERIFY_SSL_KEY, 'TRUE').strip().upper() == 'TRUE'
        self.__delaying_second = int(os.environ.get(self.DELAY_SECOND, '30'))
        self.__repeating_times = int(os.environ.get(self.REPEAT_TIMES, '0'))
        self.__verify_ssl = os.environ.get(self.VERIFY_SSL_KEY, 'TRUE').strip().upper() == 'TRUE'
        return self

    def catalog(self, **kwargs):
        self.__set_props_from_env()
        if isinstance(self._uploaded_files_json, dict) and 'features' in self._uploaded_files_json:
            self._uploaded_files_json = self._uploaded_files_json['features']
        dapa_client = DapaClient().with_verify_ssl(self.__verify_ssl)
        main_collection = self._uploaded_files_json[0]['collection']
        collection_result = dapa_client.get_collection(main_collection)
        LOGGER.debug(f'{main_collection} details: {collection_result}')
        response_jsons = []
        for i, features_chunk in enumerate(StageInOutUtils.chunk_list(self._uploaded_files_json, self.__chunk_size)):
            LOGGER.debug(f'working on chunk_index {i}')
            dapa_body = {
                "provider_id": self.__provider_id,
                "features": features_chunk
            }
            LOGGER.debug(f'dapa_body_granules: {dapa_body}')
            dapa_ingest_result = dapa_client.ingest_granules_w_cnm(dapa_body)
            extracted_ids = [k['id'] for k in features_chunk]
            LOGGER.debug(f'checking following IDs: {extracted_ids}')
            status_checker = CatalogingGranulesStatusChecker(features_chunk[0]['collection'],
                                                             extracted_ids,
                                                             TimeUtils().get_datetime_obj().timestamp(),
                                                             self.__delaying_second,
                                                             self.__repeating_times,
                                                             self.__verify_ssl)
            status_result = status_checker.verify_n_times()
            LOGGER.debug(f'chunk_index {i} status_result: {status_result}')
            response_jsons.append({
                'cataloging_request_status': dapa_ingest_result,
                'status_result': status_result
            })
        return json.dumps(response_jsons)

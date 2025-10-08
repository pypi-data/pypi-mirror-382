import logging
import time

from mdps_ds_lib.stage_in_out.dapa_client import DapaClient
from mdps_ds_lib.lib.cumulus_stac.item_transformer import ItemTransformer

LOGGER = logging.getLogger(__name__)


class CatalogingGranulesStatusChecker:
    def __init__(self, collection_id: str, granules_ids: list, threshold_datetime: int, delay: int, repeating_times: int, veriffy_ssl=False):
        self.__collection_id = collection_id
        self.__granules_ids = granules_ids
        self.__threshold_datetime = threshold_datetime
        self.__delay = delay
        self.__repeating_times = repeating_times if repeating_times >= 0 else 0
        self.__dapa_client = DapaClient().with_verify_ssl(veriffy_ssl)
        self.__registered_granules = {}

    def verify_one_time(self):
        granule_ids = [f"'{k}'" for k in self.__granules_ids]
        registered_granules = self.__dapa_client.get_granules(collection_id=self.__collection_id,
                                                              filters=f"id in ({','.join(granule_ids)})")
        LOGGER.debug(f'raw registered_granules: {registered_granules}')
        registered_granules = [ItemTransformer().from_stac(k) for k in registered_granules['features']]
        self.__registered_granules = {k.id: k for k in registered_granules if
                               k.datetime.timestamp() >= self.__threshold_datetime}
        LOGGER.debug(f'registered_granules after filtering: {[k for k in self.__registered_granules.keys()]}')
        LOGGER.debug(f'comparison queried v. expected: {len(self.__registered_granules)} v. {len(self.__granules_ids)}')
        missing_granules = [k for k in self.__granules_ids if k not in self.__registered_granules]
        return {
            'cataloged': len(missing_granules) < 1,
            'missing_granules': missing_granules,
            'registered_granules': [v.to_dict(include_self_link=False, transform_hrefs=False) for v in self.__registered_granules.values()]
        }

    def verify_n_times(self):
        verify_result = {
            'missing_granules': [],
            'registered_granules': []
        }
        for i in range(self.__repeating_times):
            time.sleep(self.__delay)
            verify_result = self.verify_one_time()
            LOGGER.debug(f'time {i} verification result: {verify_result}')
            if len(verify_result['missing_granules']) < 1:
                return verify_result
        return verify_result


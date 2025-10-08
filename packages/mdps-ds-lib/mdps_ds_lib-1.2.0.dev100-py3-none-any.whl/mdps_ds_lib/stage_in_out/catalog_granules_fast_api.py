import json
from collections import defaultdict
from datetime import datetime
from urllib.parse import urlparse

from pystac import Item, Collection, Extent, SpatialExtent, TemporalExtent, Provider, Summaries

from mdps_ds_lib.lib.utils.file_utils import FileUtils
from mdps_ds_lib.stac_fast_api_client.sfa_client_factory import SFAClientFactory
from mdps_ds_lib.stage_in_out.stage_in_out_utils import StageInOutUtils

from mdps_ds_lib.stage_in_out.catalog_granules_abstract import CatalogGranulesAbstract
import logging
import os


LOGGER = logging.getLogger(__name__)


class CatalogGranulesFastAPI(CatalogGranulesAbstract):
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

    def __retrieve_item_collection(self):
        if isinstance(self._uploaded_files_json, list):
            return {
                "type": "FeatureCollection",
                "features": self._uploaded_files_json,
            }
        if isinstance(self._uploaded_files_json, dict):
            if 'type' not in self._uploaded_files_json:
                raise ValueError(f'unknown uploaded_files_json: {self._uploaded_files_json}')
            if self._uploaded_files_json['type'] == 'FeatureCollection':
                return self._uploaded_files_json
            if self._uploaded_files_json['type'] == 'Catalog':
                catalog_file_path = os.environ.get(self.UPLOADED_FILES_JSON)
                # TODO is href already S3 URL? If so, need to download it.
                try:
                    items = [FileUtils.read_json(os.path.join(os.path.dirname(catalog_file_path), k['href'])) for k in self._uploaded_files_json['links'] if k['rel'] == 'item']
                except:
                    LOGGER.exception(f'invalid json in one or more of Catalog > Item > href: {self._uploaded_files_json}')
                    raise RuntimeError(f'invalid json in one or more of Catalog > Item > href: {self._uploaded_files_json}')
                return {
                    "type": "FeatureCollection",
                    "features": items,
                }
        raise ValueError(f'unknown uploaded_files_json: {self._uploaded_files_json}')

    def __verify_items(self):
        errors = []
        for each_item in self._uploaded_files_json['features']:
            each_stac_item = Item.from_dict(each_item)
            # each_stac_item.validate()
            for each_asset_k, each_asset_v in each_stac_item.assets.items():
                each_href = urlparse(each_asset_v.href)
                if each_href.netloc is None or each_href.netloc == '':
                    errors.append(f'incorrect URL: {each_asset_k}: {each_asset_v}')
        if len(errors) > 0:
            raise RuntimeError(f'one or more assets\' href with missing netloc: {errors}')
        return

    def __split_by_collections(self):
        by_collections = defaultdict(list)
        for each_item in self._uploaded_files_json['features']:
            by_collections[each_item['collection']].append(each_item)
        return by_collections

    def __has_or_create_collection(self, sfa_client, collection_id):
        try:
            collection_result = sfa_client.get_collection(collection_id)
        except Exception as e:
            if 'NotFoundError' in str(e):
                new_collection = Collection(id=collection_id,
                                            description='TODO',
                                            extent=Extent(SpatialExtent([[-180, -90, 180, 90]]),
                                                          TemporalExtent([[datetime.utcnow(), datetime.utcnow()]])),
                                            title=collection_id,
                                            providers=[Provider(self.__provider_id)],
                                            summaries=Summaries({
                                            }),
                                            )
                collection_result = new_collection.to_dict(False, False)
                sfa_client.create_collection(collection_result)
            else:
                raise e
        return collection_result

    def catalog(self, **kwargs):
        self.__set_props_from_env()
        # If array, convert to Feature Collection
        # If catalog, convert to Feature Collection
        # Throw error if Catalog or Feature collection or each item is not valid
        # Check assets in Items are absolute URL. Not relative URL.
        # Create one or more collections if needed
        # Make FAST API Call. If too many in items, split?
        self._uploaded_files_json = self.__retrieve_item_collection()
        self.__verify_items()
        self._uploaded_files_json = self.__split_by_collections()  # NOTE: This doesn't return FeatureCollection. Just a simple dict with list
        sfa_client = SFAClientFactory().get_instance_from_env()

        response_jsons = []
        for each_collection, item_list in self._uploaded_files_json.items():
            self.__has_or_create_collection(sfa_client, each_collection)
            for i, features_chunk in enumerate(StageInOutUtils.chunk_list(item_list, self.__chunk_size)):
                LOGGER.debug(f'working on chunk_index {i} for {each_collection}')
                ingest_result = sfa_client.create_item(each_collection, {
                    "type": "FeatureCollection",
                    "features": features_chunk,
                })
                response_jsons.append({
                    'cataloging_request_status': ingest_result,
                })
        return json.dumps(response_jsons)

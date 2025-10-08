import json
import logging
import os

import requests

from mdps_ds_lib.stage_in_out.search_granules_abstract import SearchGranulesAbstract

LOGGER = logging.getLogger(__name__)


class SearchGranulesCmr(SearchGranulesAbstract):
    CMR_BASE_URL_KEY = 'CMR_BASE_URL'
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
        self.__page_size = 2000  # page_size - number of results per page - default is 10, max is 2000
        self.__verify_ssl = True
        self.__cmr_base_url = ''

    def __set_props_from_env(self):
        missing_keys = [k for k in [self.COLLECTION_ID_KEY, self.CMR_BASE_URL_KEY] if k not in os.environ]
        if len(missing_keys) > 0:
            raise ValueError(f'missing environment keys: {missing_keys}')

        self.__collection_id = os.environ.get(self.COLLECTION_ID_KEY)
        self.__cmr_base_url = os.environ.get(self.CMR_BASE_URL_KEY)
        if not self.__cmr_base_url.endswith('/'):
            self.__cmr_base_url = f'{self.__cmr_base_url}/'
        if self.LIMITS_KEY not in os.environ:
            LOGGER.warning(f'missing {self.LIMITS_KEY}. using default: {self.__limit}')
        else:
            self.__limit = int(os.environ.get(self.LIMITS_KEY))

        self.__date_from = os.environ.get(self.DATE_FROM_KEY, '')
        self.__date_to = os.environ.get(self.DATE_TO_KEY, '')
        self.__verify_ssl = os.environ.get(self.VERIFY_SSL_KEY, 'TRUE').strip().upper() == 'TRUE'
        return self

    def __get_correct_result_count(self, results):
        if self.__limit < 0 or self.__limit >= len(results):
            return results
        return results[0: self.__limit]

    def search(self, **kwargs) -> str:
        """
  curl 'https://cmr.earthdata.nasa.gov/search/granules.stac' \
  -H 'accept: application/json; profile=stac-catalogue' \
  -H 'content-type: application/x-www-form-urlencoded' \
  --data-raw 'collection_concept_id=C1649553296-PODAAC&page_num=1&page_size=20&temporal[]=2011-08-01T00:00:00,2011-09-01T00:00:00'

        https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html#stac
        https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html#query-parameters

        :param kwargs:
        :return:
        """
        self.__set_props_from_env()
        header = {
            'accept': 'application/json; profile=stac-catalogue',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        results = []
        page_size = self.__page_size if self.__limit < 0 or self.__limit > self.__page_size else self.__limit
        page_num = 1
        items_collection_shell = None
        while True:
            if 0 < self.__limit <= len(results):
                break
            request_body = {
                'collection_concept_id': self.__collection_id,
                'page_num': str(page_num),
                'page_size': str(page_size),
                'temporal[]': f'{self.__date_from},{self.__date_to}'
            }
            cmr_granules_url = f'{self.__cmr_base_url}search/granules.stac'
            response = requests.post(url=cmr_granules_url, headers=header, verify=self.__verify_ssl,
                                     data=request_body)
            if response.status_code >= 400:
                raise RuntimeError(
                    f'Cognito ends in error. status_code: {response.status_code}. url: {cmr_granules_url}. details: {response.text}')
            temp_results = json.loads(response.content.decode('utf-8'))
            if items_collection_shell is None:
                items_collection_shell = temp_results
            temp_results = temp_results.pop('features')
            page_num += 1
            results.extend(temp_results)
            if len(temp_results) < page_size:
                break
        results = self.__get_correct_result_count(results)
        items_collection_shell['features'] = results
        return json.dumps(items_collection_shell)

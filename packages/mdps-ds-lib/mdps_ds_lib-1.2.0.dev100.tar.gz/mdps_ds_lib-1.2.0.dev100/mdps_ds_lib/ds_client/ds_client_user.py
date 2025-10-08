import json
import logging

import requests
from pystac import Item

from mdps_ds_lib.ds_client.auth_token.token_abstract import TokenAbstract
from mdps_ds_lib.ds_client.ds_client_base import DsClient
from mdps_ds_lib.lib.cumulus_stac.unity_collection_stac import UnityCollectionStac

LOGGER = logging.getLogger(__name__)


class DsClientUser(DsClient):


    def __init__(self, token_retriever: TokenAbstract, ds_url: str, ds_stage: str):
        super().__init__(token_retriever, ds_url, ds_stage)
        self.__granule_query_next_page = None
        self.__collection_query_next_page = None

    def create_new_collection(self, is_actual_execution=False):
        request_url = f'{self._uds_url}collections/'
        if is_actual_execution:
            request_url = f'{request_url}actual'
        s = requests.session()
        s.trust_env = self._trust_env
        temp_collection_id = [
            self.urn, self.org, self.project, self.tenant, self.tenant_venue, self.get_complete_collection()
        ]
        temp_collection_id = ':'.join(temp_collection_id)
        dapa_collection = UnityCollectionStac() \
            .with_id(temp_collection_id) \
            .with_graule_id_regex("^test_file.*$") \
            .with_granule_id_extraction_regex("(^test_file.*)(\\.nc|\\.nc\\.cas|\\.cmr\\.xml)") \
            .with_title("test_file01.nc") \
            .with_process('stac') \
            .with_provider('unity') \
            .add_file_type("test_file01.nc", "^test_file.*\\.nc$", 'unknown_bucket', 'application/json', 'root') \
            .add_file_type("test_file01.nc", "^test_file.*\\.nc$", 'protected', 'data', 'item') \
            .add_file_type("test_file01.nc.cas", "^test_file.*\\.nc.cas$", 'protected', 'metadata', 'item') \
            .add_file_type("test_file01.nc.cmr.xml", "^test_file.*\\.nc.cmr.xml$", 'protected', 'metadata', 'item') \
            .add_file_type("test_file01.nc.stac.json", "^test_file.*\\.nc.stac.json$", 'protected', 'metadata', 'item')
        print(dapa_collection)
        stac_collection = dapa_collection.start()
        print(json.dumps(stac_collection))

        response = s.post(url=request_url, headers={
            'Authorization': f'Bearer {self._token_retriever.get_token()}',
            'Content-Type': 'application/json',
        }, verify=self._trust_env, data=json.dumps(stac_collection))
        response.raise_for_status()
        return response.text

    def delete_collection(self):
        request_url = f'{self._uds_url}collections/'
        s = requests.session()
        s.trust_env = self._trust_env
        temp_collection_id = [
            self.urn, self.org, self.project, self.tenant, self.tenant_venue, self.get_complete_collection()
        ]
        temp_collection_id = ':'.join(temp_collection_id)
        request_url = f'{request_url}{temp_collection_id}/'

        response = s.delete(url=request_url, headers={
            'Authorization': f'Bearer {self._token_retriever.get_token()}',
        }, verify=self._trust_env)
        response.raise_for_status()
        return response.text

    def query_custom_properties(self):
        if self.tenant is None or self.tenant_venue is None or self.collection is None:
            raise ValueError(f'require to set tenant & tenant_venue & collection & granule')
        collection_id_for_granules = ':'.join([self.urn, self.org, self.project, self.tenant, self.tenant_venue, self.get_complete_collection()])
        request_url = f'{self._uds_url}collections/'
        request_url = f'{request_url}{collection_id_for_granules}/variables'
        print(request_url)
        s = requests.session()
        s.trust_env = self._trust_env
        response = s.get(url=request_url, headers={
            'Authorization': f'Bearer {self._token_retriever.get_token()}',
        }, verify=self._trust_env)
        response.raise_for_status()
        response = json.loads(response.text)
        return response

    def query_collections(self, limit=10):
        query_params = {
            # 'datetime': datetime,
            'limit': limit,
            # 'filter': filter,
            # 'bbox': bbox,
            # 'sortby': sort_keys,
        }
        query_params = {k: v for k, v in query_params.items() if v is not None}
        request_url = f'{self._uds_url}collections/'
        query_params = '&'.join([f'{k}={v}' for k, v in query_params.items()])
        request_url = f'{request_url}?{query_params}'
        s = requests.session()
        s.trust_env = self._trust_env
        response = s.get(url=request_url, headers={
            'Authorization': f'Bearer {self._token_retriever.get_token()}',
        }, verify=self._trust_env)
        response.raise_for_status()
        response = json.loads(response.text)
        self.__collection_query_next_page = [k['href'] for k in response['links'] if k['rel'] == 'next']
        self.__collection_query_next_page = None if len(self.__collection_query_next_page) < 1 else \
        self.__collection_query_next_page[0]

        return response

    def query_catalog(self):
        request_url = f'{self._uds_url}catalog/'
        s = requests.session()
        s.trust_env = self._trust_env
        response = s.get(url=request_url, headers={
            'Authorization': f'Bearer {self._token_retriever.get_token()}',
        }, verify=self._trust_env)
        response.raise_for_status()
        response = json.loads(response.text)
        return response

    def query_collections_next(self):
        if self.__collection_query_next_page is None:
            return None
        s = requests.session()
        s.trust_env = self._trust_env
        response = s.get(url=self.__collection_query_next_page, headers={
            'Authorization': f'Bearer {self._token_retriever.get_token()}',
        }, verify=self._trust_env)
        response.raise_for_status()
        response = json.loads(response.text)
        self.__collection_query_next_page = [k['href'] for k in response['links'] if k['rel'] == 'next']
        self.__collection_query_next_page = None if len(self.__collection_query_next_page) < 1 else self.__collection_query_next_page[0]
        return response

    def query_single_collection(self):
        if self.tenant is None or self.tenant_venue is None or self.collection is None:
            raise ValueError(f'require to set tenant & tenant_venue & collection')
        collection_id_for_granules = ':'.join([self.urn, self.org, self.project, self.tenant, self.tenant_venue, self.get_complete_collection()])
        request_url = f'{self._uds_url}collections/'
        request_url = f'{request_url}{collection_id_for_granules}/'
        s = requests.session()
        s.trust_env = self._trust_env
        response = s.get(url=request_url, headers={
            'Authorization': f'Bearer {self._token_retriever.get_token()}',
        }, verify=self._trust_env)
        response.raise_for_status()
        response = json.loads(response.text)
        return response

    def create_new_granule(self, granule_stac: Item):
        request_url = f'{self._uds_url}collections/'
        temp_collection_id = [self.urn, self.org, self.project, self.tenant, self.tenant_venue, self.get_complete_collection()]
        temp_granule_id = temp_collection_id + [self.granule]
        temp_collection_id = ':'.join(temp_collection_id)
        temp_granule_id = ':'.join(temp_granule_id)

        granule_stac.id = temp_granule_id
        granule_stac.collection_id = temp_collection_id
        request_url = f'{request_url}{temp_collection_id}/items/{temp_granule_id}'
        s = requests.session()
        s.trust_env = self._trust_env
        response = s.put(url=request_url, headers={
            'Authorization': f'Bearer {self._token_retriever.get_token()}',
            'Content-Type': 'application/json',
        }, verify=self._trust_env, data=json.dumps(granule_stac.to_dict(False, False)))
        response.raise_for_status()
        return response.text

    def query_granules_across_collections(self, limit= 10, datetime = None, filter = None, bbox= None, sort_keys=None):
        if self.tenant is None or self.tenant_venue is None:
            raise ValueError(f'require to set tenant & tenant_venue')
        collection_id_for_granules = ':'.join([self.urn, self.org, self.project, self.tenant, self.tenant_venue, '*'])
        query_params = {
            'datetime': datetime,
            'limit': limit,
            'filter': filter,
            'bbox': bbox,
            'sortby': sort_keys,
        }
        query_params = {k: v for k, v in query_params.items() if v is not None}

        request_url = f'{self._uds_url}collections/'
        query_params = '&'.join([f'{k}={v}' for k, v in query_params.items()])
        request_url = f'{request_url}{collection_id_for_granules}/items/?{query_params}'
        s = requests.session()
        s.trust_env = self._trust_env
        response = s.get(url=request_url, headers={
            'Authorization': f'Bearer {self._token_retriever.get_token()}',
        }, verify=self._trust_env)
        response.raise_for_status()
        response = json.loads(response.text)
        
        self.__granule_query_next_page = [k['href'] for k in response['links'] if k['rel'] == 'next']
        self.__granule_query_next_page = None if len(self.__granule_query_next_page) < 1 else self.__granule_query_next_page[0]
        return response

    def query_granules_next(self):
        if self.__granule_query_next_page is None:
            return None
        s = requests.session()
        s.trust_env = self._trust_env
        response = s.get(url=self.__granule_query_next_page, headers={
            'Authorization': f'Bearer {self._token_retriever.get_token()}',
        }, verify=self._trust_env)
        response.raise_for_status()
        response = json.loads(response.text)
        self.__granule_query_next_page = [k['href'] for k in response['links'] if k['rel'] == 'next']
        self.__granule_query_next_page = None if len(self.__granule_query_next_page) < 1 else self.__granule_query_next_page[0]
        return response

    def query_granules(self, limit= 10, datetime = None, filter = None, bbox= None, sort_keys=None):
        if self.tenant is None or self.tenant_venue is None or self.collection is None:
            raise ValueError(f'require to set tenant & tenant_venue & collection')
        collection_id_for_granules = ':'.join([self.urn, self.org, self.project, self.tenant, self.tenant_venue, self.get_complete_collection()])
        query_params = {
            'datetime': datetime,
            'limit': limit,
            'filter': filter,
            'bbox': bbox,
            'sortby': sort_keys,
        }
        query_params = {k: v for k, v in query_params.items() if v is not None}

        request_url = f'{self._uds_url}collections/'
        query_params = '&'.join([f'{k}={v}' for k, v in query_params.items()])
        request_url = f'{request_url}{collection_id_for_granules}/items/?{query_params}'
        s = requests.session()
        s.trust_env = self._trust_env
        response = s.get(url=request_url, headers={
            'Authorization': f'Bearer {self._token_retriever.get_token()}',
        }, verify=self._trust_env)
        response.raise_for_status()
        response = json.loads(response.text)

        self.__granule_query_next_page = [k['href'] for k in response['links'] if k['rel'] == 'next']
        self.__granule_query_next_page = None if len(self.__granule_query_next_page) < 1 else \
        self.__granule_query_next_page[0]
        return response

    def query_single_granule(self):
        if self.tenant is None or self.tenant_venue is None or self.collection is None or self.granule is None:
            raise ValueError(f'require to set tenant & tenant_venue & collection & granule')
        collection_id_for_granules = ':'.join([self.urn, self.org, self.project, self.tenant, self.tenant_venue, self.get_complete_collection()])
        granule_id_complete = ':'.join([collection_id_for_granules, self.granule])
        request_url = f'{self._uds_url}collections/'
        request_url = f'{request_url}{collection_id_for_granules}/items/{granule_id_complete}'
        print(request_url)
        s = requests.session()
        s.trust_env = self._trust_env
        response = s.get(url=request_url, headers={
            'Authorization': f'Bearer {self._token_retriever.get_token()}',
        }, verify=self._trust_env)
        response.raise_for_status()
        response = json.loads(response.text)
        return response

    def delete_single_granule(self):
        if self.tenant is None or self.tenant_venue is None or self.collection is None or self.granule is None:
            raise ValueError(f'require to set tenant & tenant_venue & collection & granule')
        collection_id_for_granules = ':'.join([self.urn, self.org, self.project, self.tenant, self.tenant_venue, self.get_complete_collection()])
        granule_id_complete = ':'.join([collection_id_for_granules, self.granule])
        request_url = f'{self._uds_url}collections/'
        request_url = f'{request_url}{collection_id_for_granules}/items/{granule_id_complete}'
        print(request_url)
        s = requests.session()
        s.trust_env = self._trust_env
        response = s.delete(url=request_url, headers={
            'Authorization': f'Bearer {self._token_retriever.get_token()}',
        }, verify=self._trust_env)
        response.raise_for_status()
        response = json.loads(response.text)
        return response

    def add_archive_config(self, daac_config: dict):
        if self.tenant is None or self.tenant_venue is None or self.collection is None:
            raise ValueError(f'require to set tenant & tenant_venue & collection')
        collection_id = ':'.join([self.urn, self.org, self.project, self.tenant, self.tenant_venue, self.get_complete_collection()])

        request_url = f'{self._uds_url}collections/{collection_id}/archive/'
        s = requests.session()
        s.trust_env = self._trust_env
        response = s.put(url=request_url, headers={
            'Authorization': f'Bearer {self._token_retriever.get_token()}',
            'Content-Type': 'application/json',

        }, verify=self._trust_env, data = json.dumps(daac_config))
        response.raise_for_status()
        response = json.loads(response.text)
        return response

    def get_archive_config(self):
        if self.tenant is None or self.tenant_venue is None or self.collection is None:
            raise ValueError(f'require to set tenant & tenant_venue & collection')
        collection_id = ':'.join([self.urn, self.org, self.project, self.tenant, self.tenant_venue, self.get_complete_collection()])

        request_url = f'{self._uds_url}collections/{collection_id}/archive/'
        print(f'request_url: {request_url}')
        print(f'token: {self._token_retriever.get_token()}')
        s = requests.session()
        s.trust_env = self._trust_env
        response = s.get(url=request_url, headers={
            'Authorization': f'Bearer {self._token_retriever.get_token()}',
            'Content-Type': 'application/json',

        }, verify=self._trust_env)
        response.raise_for_status()
        response = json.loads(response.text)
        return response

    def archive_granule(self):
        if self.tenant is None or self.tenant_venue is None or self.collection is None or self.granule is None:
            raise ValueError(f'require to set tenant & tenant_venue & collection & granule')
        collection_id_for_granules = ':'.join([self.urn, self.org, self.project, self.tenant, self.tenant_venue, self.get_complete_collection()])
        granule_id_complete = ':'.join([collection_id_for_granules, self.granule])
        request_url = f'{self._uds_url}collections/'
        request_url = f'{request_url}{collection_id_for_granules}/archive/{granule_id_complete}/'
        print(request_url)
        s = requests.session()
        s.trust_env = self._trust_env
        response = s.put(url=request_url, headers={
            'Authorization': f'Bearer {self._token_retriever.get_token()}',
        }, verify=self._trust_env)
        response.raise_for_status()
        response = json.loads(response.text)
        return response


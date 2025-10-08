import json
import logging

import requests

from mdps_ds_lib.ds_client.auth_token.token_abstract import TokenAbstract
from mdps_ds_lib.ds_client.ds_client_base import DsClient
LOGGER = logging.getLogger(__name__)


class DsClientAdmin(DsClient):


    def __init__(self, token_retriever: TokenAbstract, ds_url: str, ds_stage: str):
        super().__init__(token_retriever, ds_url, ds_stage)

    def add_admin_group(self, crud_actions: list, group_name: str):
        request_url = f'{self._uds_url}admin/auth'
        LOGGER.debug(f'request_url: {request_url}')
        collection_complete_name = '.*' if self.collection is None else \
            f'{self.collection}.*' if self.collection_venue is None else f'{self.collection}___{self.collection_venue}'
        resources = [self.urn, self.org, self.project,
                     self.tenant if self.tenant is not None else '*',
                     self.tenant_venue if self.tenant_venue is not None else '*',
                     collection_complete_name
                     ]
        admin_add_body = {
            "actions": [k.upper() for k in crud_actions],
            "resources": [':'.join(resources)],
            "tenant": self.tenant,
            "venue": self.tenant_venue,
            "group_name": group_name
        }
        LOGGER.debug(f"admin_add_body: {admin_add_body}")
        s = requests.session()
        s.trust_env = self._trust_env
        response = s.put(url=request_url, headers={
            'Authorization': f'Bearer {self._token_retriever.get_token()}',
            'Content-Type': 'application/json',
        }, verify=self._trust_env, data=json.dumps(admin_add_body))
        response.raise_for_status()
        return response.text

    def delete_admin_group(self, group_name: str):
        request_url = f'{self._uds_url}admin/auth'
        LOGGER.debug(f'request_url: {request_url}')
        admin_delete_body = {
            "tenant": self.tenant,
            "venue": self.tenant_venue,
            "group_name": group_name
        }
        LOGGER.debug(f"admin_add_body: {admin_delete_body}")
        s = requests.session()
        s.trust_env = self._trust_env
        response = s.delete(url=request_url, headers={
            'Authorization': f'Bearer {self._token_retriever.get_token()}',
            'Content-Type': 'application/json',
        }, verify=self._trust_env, data=json.dumps(admin_delete_body))
        response.raise_for_status()
        return response.text

    def list_admin_group(self, group_names: list=[]):
        request_url = f'{self._uds_url}admin/auth'
        params = [
            f'tenant={self.tenant}',
            f'venue={self.tenant_venue}',
        ]
        if len(group_names) < 1:
            params.append(f'group_names={",".join(group_names)}')
        params = '&'.join(params)
        request_url = f'{request_url}?{params}'
        LOGGER.debug(f'request_url: {request_url}')
        s = requests.session()
        s.trust_env = self._trust_env
        response = s.get(url=request_url, headers={
            'Authorization': f'Bearer {self._token_retriever.get_token()}',
            'Content-Type': 'application/json',
        }, verify=self._trust_env)
        response.raise_for_status()
        return json.loads(response.text)

    def update_admin_group(self, crud_actions: list, group_name: str):
        raise NotImplementedError(f'TO DO')

    def setup_database(self):
        es_setup_url = f'{self._uds_url}admin/system/es_setup/'
        print(f'es_setup_url: {es_setup_url}')
        s = requests.session()
        s.trust_env = self._trust_env
        response = s.put(url=es_setup_url, headers={'Authorization': f'Bearer {self._token_retriever.get_token()}'}, verify=self._trust_env)
        response.raise_for_status()
        return response.text

    def add_tenant_database_index(self, custom_metadata_es_index: dict):
        request_url = f'{self._uds_url}admin/custom_metadata/{self.tenant}/'
        if self.tenant_venue is not None:
            request_url = f'{request_url}?venue={self.tenant_venue}'
        print(f'request_url: {request_url}')
        s = requests.session()
        s.trust_env = self._trust_env
        response = s.put(url=request_url, headers={
            'Authorization': f'Bearer {self._token_retriever.get_token()}',
            'Content-Type': 'application/json',
        }, verify=self._trust_env, data=json.dumps(custom_metadata_es_index))
        response.raise_for_status()
        return response.text

    def get_tenant_database_index(self):
        request_url = f'{self._uds_url}admin/custom_metadata/{self.tenant}/'
        if self.tenant_venue is not None:
            request_url = f'{request_url}?venue={self.tenant_venue}'
        print(f'request_url: {request_url}')
        s = requests.session()
        s.trust_env = self._trust_env
        response = s.get(url=request_url, headers={
            'Authorization': f'Bearer {self._token_retriever.get_token()}',
            'Content-Type': 'application/json',
        }, verify=self._trust_env)
        response.raise_for_status()
        return json.loads(response.text)

    def delete_tenant_database_index(self):
        request_url = f'{self._uds_url}admin/custom_metadata/{self.tenant}/'
        if self.tenant_venue is not None:
            request_url = f'{request_url}?venue={self.tenant_venue}'
        print(f'request_url: {request_url}')
        s = requests.session()
        s.trust_env = self._trust_env
        response = s.delete(url=request_url, headers={
            'Authorization': f'Bearer {self._token_retriever.get_token()}',
            'Content-Type': 'application/json',
        }, verify=self._trust_env)
        response.raise_for_status()
        return response.text

    def destroy_tenant_database_index(self):
        request_url = f'{self._uds_url}admin/custom_metadata/{self.tenant}/destroy/'
        if self.tenant_venue is not None:
            request_url = f'{request_url}?venue={self.tenant_venue}'
        print(f'request_url: {request_url}')
        s = requests.session()
        s.trust_env = self._trust_env
        response = s.delete(url=request_url, headers={
            'Authorization': f'Bearer {self._token_retriever.get_token()}',
            'Content-Type': 'application/json',
        }, verify=self._trust_env)
        response.raise_for_status()
        return response.text

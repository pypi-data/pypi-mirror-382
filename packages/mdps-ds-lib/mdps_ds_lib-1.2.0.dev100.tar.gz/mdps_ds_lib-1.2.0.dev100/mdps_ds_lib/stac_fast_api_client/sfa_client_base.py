import os
from abc import ABC, abstractmethod

import requests
from dotenv import load_dotenv


class SFAClientBase(ABC):
    def __init__(self, ds_url: str, ds_stage: str):
        load_dotenv()
        self._trust_env = os.getenv('TRUST_ENV', 'FALSE').upper().strip() == 'TRUE'
        self._base_url = f'{ds_url}/{ds_stage}'

    @abstractmethod
    def create_session(self):
        s = requests.session()
        s.trust_env = self._trust_env
        # s.cookies.set('mod_auth_openidc_session', 'xxx-xxx-xxx')
        # s.auth = HTTPBasicAuth('user', 'pass')
        # s.headers.update({"Authorization": f"Bearer {token}"})
        return s

    def _handle_response(self, response):
        """
        Raises HTTPError with detailed response text if available.
        """
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            # Attach response text to the exception for easier debugging
            error_text = response.text.strip()
            raise requests.HTTPError(
                f"{e}\nResponse content: {error_text}"
            ) from None
        try:
            return response.json()
        except:
            raise requests.HTTPError(f'invalid JSON response: {response.text}')

    def get_collections(self, **params):
        url = f"{self._base_url}/collections"
        response = self.create_session().get(url, params=params)
        return self._handle_response(response)

    def get_collection(self, collection_id, **params) -> dict:  # Return a COllection STAC JSON
        url = f"{self._base_url}/collections/{collection_id}"
        response = self.create_session().get(url, params=params)
        return self._handle_response(response)

    def create_collection(self, collection):
        url = f"{self._base_url}/collections"
        response = self.create_session().post(url, json=collection)
        # NOTE: result if not found: {"code":"NotFoundError","description":"Collection Invalid-Collection not found"}
        return self._handle_response(response)

    def get_items(self, collection_id, **params):
        url = f"{self._base_url}/collections/{collection_id}/items"
        response = self.create_session().get(url, params=params)
        return self._handle_response(response)

    def create_item(self, collection_id, item):
        url = f"{self._base_url}/collections/{collection_id}/items"
        my_session = self.create_session()
        my_session.headers.update({'Content-Type': 'application/json'})
        response = self.create_session().post(url, json=item)
        return self._handle_response(response)

    def update_item(self, collection_id, item_id, item, update_whole=True):
        url = f"{self._base_url}/collections/{collection_id}/items/{item_id}"
        my_session = self.create_session()
        my_session.headers.update({'Content-Type': 'application/json'})
        response = self.create_session().put(url, json=item) if update_whole else self.create_session().patch(url, json=item)
        return self._handle_response(response)

    def get_item(self, collection_id, item_id, **params):
        url = f"{self._base_url}/collections/{collection_id}/items/{item_id}"
        response = self.create_session().get(url, params=params)
        return self._handle_response(response)

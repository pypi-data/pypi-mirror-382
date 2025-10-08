import json
import logging
import os

import requests

from dotenv import load_dotenv
from mdps_ds_lib.ds_client.auth_token.token_abstract import TokenAbstract
from mdps_ds_lib.ds_client.auth_token.token_factory import TokenFactory
LOGGER = logging.getLogger(__name__)


class DsClient:
    def __init__(self, token_retriever: TokenAbstract, ds_url: str, ds_stage: str):
        load_dotenv()
        self._trust_env = os.getenv('TRUST_ENV', 'FALSE').upper().strip() == 'TRUE'
        self._token_retriever = token_retriever
        self._uds_url = f'{ds_url}/{ds_stage}/'
        self.__urn, self.__org, self.__project = 'URN', 'NASA', 'UNITY'
        self.__tenant, self.__tenant_venue, self.__collection, self.__collection_venue = None, None, None, None
        self.__granule = None
        self.__default_collection_venue = '001'

    def get_complete_collection(self):
        collection_venue = self.__default_collection_venue if self.collection_venue is None else self.collection_venue
        return f'{self.collection}___{collection_venue}'

    @property
    def granule(self):
        return self.__granule

    @granule.setter
    def granule(self, val):
        """
        :param val:
        :return: None
        """
        self.__granule = val
        return

    @property
    def project(self):
        return self.__project

    @project.setter
    def project(self, val):
        """
        :param val:
        :return: None
        """
        self.__project = val
        return
    @property
    def urn(self):
        return self.__urn

    @urn.setter
    def urn(self, val):
        """
        :param val:
        :return: None
        """
        self.__urn = val
        return
    @property
    def org(self):
        return self.__org

    @org.setter
    def org(self, val):
        """
        :param val:
        :return: None
        """
        self.__org = val
        return
    @property
    def tenant(self):
        return self.__tenant

    @tenant.setter
    def tenant(self, val):
        """
        :param val:
        :return: None
        """
        self.__tenant = val
        return
    @property
    def tenant_venue(self):
        return self.__tenant_venue

    @tenant_venue.setter
    def tenant_venue(self, val):
        """
        :param val:
        :return: None
        """
        self.__tenant_venue = val
        return
    @property
    def collection(self):
        return self.__collection

    @collection.setter
    def collection(self, val):
        """
        :param val:
        :return: None
        """
        self.__collection = val
        return
    @property
    def collection_venue(self):
        return self.__collection_venue

    @collection_venue.setter
    def collection_venue(self, val):
        """
        :param val:
        :return: None
        """
        self.__collection_venue = val
        return



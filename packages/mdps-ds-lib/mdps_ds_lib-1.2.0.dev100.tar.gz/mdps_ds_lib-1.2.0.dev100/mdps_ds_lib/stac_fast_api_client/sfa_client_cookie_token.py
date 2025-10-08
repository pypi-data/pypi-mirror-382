from requests.auth import HTTPBasicAuth

from mdps_ds_lib.stac_fast_api_client.sfa_client_base import SFAClientBase


class SFAClientCookieToken(SFAClientBase):

    def __init__(self, auth_key: str, auth_value: str, ds_url: str, ds_stage: str):
        super().__init__(ds_url, ds_stage)
        self.__auth_key = auth_key
        self.__auth_value = auth_value

    def create_session(self):
        s1 = super().create_session()
        s1.cookies.set(self.__auth_key, self.__auth_value)
        return s1

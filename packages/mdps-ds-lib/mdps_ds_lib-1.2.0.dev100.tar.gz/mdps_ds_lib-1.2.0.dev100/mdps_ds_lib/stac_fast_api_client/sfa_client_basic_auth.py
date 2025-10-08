from requests.auth import HTTPBasicAuth

from mdps_ds_lib.stac_fast_api_client.sfa_client_base import SFAClientBase


class SFAClientBasicAuth(SFAClientBase):

    def __init__(self, username: str, password: str, ds_url: str, ds_stage: str):
        super().__init__(ds_url, ds_stage)
        self.__user = username
        self.__pass = password

    def create_session(self):
        s1 = super().create_session()
        s1.auth = HTTPBasicAuth(self.__user, self.__pass)
        return s1

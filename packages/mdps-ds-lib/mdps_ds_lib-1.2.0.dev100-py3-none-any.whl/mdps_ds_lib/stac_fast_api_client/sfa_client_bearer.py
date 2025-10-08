from requests.auth import HTTPBasicAuth

from mdps_ds_lib.stac_fast_api_client.sfa_client_base import SFAClientBase


class SFAClientBearer(SFAClientBase):

    def __init__(self, bearer_token: str, ds_url: str, ds_stage: str):
        super().__init__(ds_url, ds_stage)
        self.__bearer_token = bearer_token

    def create_session(self):
        s1 = super().create_session()
        s1.headers.update({"Authorization": f"Bearer {self.__bearer_token}"})
        return s1

from requests.auth import HTTPBasicAuth

from mdps_ds_lib.stac_fast_api_client.sfa_client_base import SFAClientBase


class SFAClientNoAuth(SFAClientBase):

    def __init__(self, ds_url: str, ds_stage: str):
        super().__init__(ds_url, ds_stage)

    def create_session(self):
        s1 = super().create_session()
        return s1

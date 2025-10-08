import os

from mdps_ds_lib.ds_client.auth_token.token_abstract import TokenAbstract


class TokenDummy(TokenAbstract):
    def get_token(self):
        env_token = os.getenv('DS_TOKEN', None)
        if env_token is None:
            raise ValueError(f'missing env_token DS_TOKEN')
        return env_token

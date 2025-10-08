import os

from mdps_ds_lib.ds_client.auth_token.token_abstract import TokenAbstract
from mdps_ds_lib.lib.cognito_login.cognito_token_retriever import CognitoTokenRetriever


class TokenCognito(TokenAbstract):
    def get_token(self):
        token_retriever = CognitoTokenRetriever()
        token = token_retriever.start()
        header = {'Authorization': f'Bearer {token}'}
        return token

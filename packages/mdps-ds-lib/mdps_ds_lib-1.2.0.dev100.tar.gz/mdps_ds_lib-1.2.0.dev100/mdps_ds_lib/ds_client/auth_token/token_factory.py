from mdps_ds_lib.lib.utils.factory_abstract import FactoryAbstract


class TokenFactory(FactoryAbstract):
    DUMMY = 'DUMMY'
    COGNITO = 'COGNITO'

    def get_instance_from_env(self, **kwargs):
        raise NotImplementedError('not yet')

    def get_instance(self, class_type, **kwargs):
        ct = class_type.upper()
        if ct == self.DUMMY:
            from mdps_ds_lib.ds_client.auth_token.token_dummy import TokenDummy
            return TokenDummy()
        if ct == self.COGNITO:
            from mdps_ds_lib.ds_client.auth_token.token_cognito import TokenCognito
            return TokenCognito()
        raise ModuleNotFoundError(f'cannot find ES class for {ct}')

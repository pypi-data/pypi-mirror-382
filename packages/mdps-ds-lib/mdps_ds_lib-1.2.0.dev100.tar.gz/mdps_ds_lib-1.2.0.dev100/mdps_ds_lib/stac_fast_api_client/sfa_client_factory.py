from mdps_ds_lib.lib.utils.factory_abstract import FactoryAbstract
from mdps_ds_lib.stac_fast_api_client.sfa_client_base import SFAClientBase
import os


class SFAClientFactory(FactoryAbstract):
    NO_AUTH = 'NO_AUTH'
    BASIC_AUTH = 'BASIC_AUTH'
    COOKIE_AUTH = 'COOKIE_AUTH'
    BEARER_AUTH = 'BEARER_AUTH'

    def get_instance_from_env(self, **kwargs) -> SFAClientBase:
        if 'DS_URL' not in os.environ:
            raise RuntimeError(f'missing mandatory env: DS_URL')
        class_env = {'ds_url': os.getenv('DS_URL'),
                     'ds_stage': '' if 'ds_stage'.upper() not in os.environ else os.getenv('ds_stage'.upper())}

        class_type_env_map = {
            SFAClientFactory.BASIC_AUTH: {
                'SFA_USERNAME': 'username',
                'SFA_PASSWORD': 'password'
            },
            SFAClientFactory.COOKIE_AUTH: {
                'SFA_AUTH_KEY': 'auth_key',
                'SFA_AUTH_VALUE': 'auth_value'
            },
            SFAClientFactory.BEARER_AUTH: {
                'SFA_BEARER_TOKEN': 'bearer_token',
            },
            SFAClientFactory.NO_AUTH: {
            },
        }
        chosen_class = None
        for k, v in class_type_env_map.items():
            if all([k1 in os.environ for k1 in list(v.keys())]):
                for k1, v1 in v.items():
                    class_env[v1] = os.getenv(k1)
                chosen_class = k
                break
        if chosen_class is None:
            raise NotImplementedError(f'unknown class type: missing ENVs. require one of {class_type_env_map}')
        return self.get_instance(chosen_class, **class_env)

    def get_instance(self, class_type, **kwargs) -> SFAClientBase:
        if class_type == self.NO_AUTH:
            from mdps_ds_lib.stac_fast_api_client.sfa_client_no_auth import SFAClientNoAuth
            return SFAClientNoAuth(kwargs['ds_url'], kwargs['ds_stage'])
        if class_type == self.BASIC_AUTH:
            from mdps_ds_lib.stac_fast_api_client.sfa_client_basic_auth import SFAClientBasicAuth
            return SFAClientBasicAuth(kwargs['username'], kwargs['password'], kwargs['ds_url'], kwargs['ds_stage'])
        if class_type == self.COOKIE_AUTH:
            from mdps_ds_lib.stac_fast_api_client.sfa_client_cookie_token import SFAClientCookieToken
            return SFAClientCookieToken(kwargs['auth_key'], kwargs['auth_value'], kwargs['ds_url'], kwargs['ds_stage'])
        if class_type == self.BEARER_AUTH:
            from mdps_ds_lib.stac_fast_api_client.sfa_client_bearer import SFAClientBearer
            return SFAClientBearer(kwargs['bearer_token'], kwargs['ds_url'], kwargs['ds_stage'])
        raise NotImplementedError(f'unknown class type: {class_type}')

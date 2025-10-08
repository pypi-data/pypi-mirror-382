import base64
import logging
import os

from mdps_ds_lib.lib.aws.aws_param_store import AwsParamStore
from mdps_ds_lib.lib.constants import Constants
from mdps_ds_lib.lib.earthdata_login.urs_token import URSToken

LOGGER = logging.getLogger(__name__)


class URSTokenRetriever:
    def __get_username_dwssap(self):
        username = os.environ[Constants.EDL_USERNAME]
        dwssap = os.environ[Constants.EDL_PASSWORD]
        if Constants.EDL_PASSWORD_TYPE not in os.environ:
            LOGGER.debug('no PASSWORD_TYPE set in ENV. assuming PLAIN STR')
            return username, dwssap
        dwssap_type = os.environ[Constants.EDL_PASSWORD_TYPE]
        if dwssap_type == Constants.PLAIN_STR:
            LOGGER.debug('PLAIN_STR in ENV. returning PLAIN STR')
            return username, dwssap
        if dwssap_type == Constants.BASE64_STR:
            LOGGER.debug('BASE64_STR in ENV. decoding & returning')
            username = base64.standard_b64decode(username.encode('utf-8')).decode('utf-8')
            dwssap = base64.standard_b64decode(dwssap.encode('utf-8')).decode('utf-8')
            return username, dwssap
        if dwssap_type == Constants.PARAM_STORE:
            LOGGER.debug('PARAM_STORE in ENV. retrieving value from Param Store')
            username_param_store = AwsParamStore().get_param(username)
            dwssap_param_store = AwsParamStore().get_param(dwssap)
            if username_param_store is None or dwssap_param_store is None:
                raise ValueError(f'NULL username or password from Param Store. Set the value in {username} AND {dwssap}')
            return username_param_store, dwssap_param_store
        raise ValueError(f'invalid {Constants.PASSWORD_TYPE}. value: {dwssap_type}')

    def start(self):
        if Constants.EDL_BEARER_TOKEN in os.environ:
            LOGGER.debug('found EDL_BEARER_TOKEN. returning UNITY_BEARER_TOKEN from ENV')
            return os.environ[Constants.EDL_BEARER_TOKEN]
        LOGGER.debug('EDL_BEARER_TOKEN not found. preparing to login')

        missing_mandatory_env = [k for k in [Constants.EDL_USERNAME, Constants.EDL_PASSWORD] if k not in os.environ]
        if len(missing_mandatory_env) > 0:
            raise ValueError(f'missing mandatory ENV for login: {missing_mandatory_env}')
        username, dwssap = self.__get_username_dwssap()
        urs_token = URSToken(username, dwssap, os.environ.get(Constants.EDL_BASE_URL, ''))
        token = urs_token.get_token()
        return token

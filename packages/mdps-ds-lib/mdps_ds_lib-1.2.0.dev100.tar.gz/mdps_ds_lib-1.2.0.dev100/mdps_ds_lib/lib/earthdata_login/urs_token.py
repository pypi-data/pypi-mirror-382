import json
import logging
import time
from http.cookiejar import CookieJar
from typing import Dict
from urllib import request

import requests
from requests.auth import HTTPBasicAuth
from tenacity import retry, retry_if_result, stop_after_attempt, wait_random_exponential

LOGGER = logging.getLogger(__name__)

class URSToken(object):
    DNS_ERROR_TXT = 'Name-Resolution-Error'
    """
    Traceback (most recent call last):
 File "/usr/local/lib/python3.9/site-packages/urllib3/connection.py", line 174, in _new_conn
  conn = connection.create_connection(
 File "/usr/local/lib/python3.9/site-packages/urllib3/util/connection.py", line 72, in create_connection
  for res in socket.getaddrinfo(host, port, family, socket.SOCK_STREAM):
 File "/usr/local/lib/python3.9/socket.py", line 954, in getaddrinfo
  for res in _socket.getaddrinfo(host, port, family, type, proto, flags):
socket.gaierror: [Errno -3] Temporary failure in name resolution
During handling of the above exception, another exception occurred:
Traceback (most recent call last):
 File "/usr/local/lib/python3.9/site-packages/urllib3/connectionpool.py", line 714, in urlopen
  httplib_response = self._make_request(
 File "/usr/local/lib/python3.9/site-packages/urllib3/connectionpool.py", line 403, in _make_request
  self._validate_conn(conn)
 File "/usr/local/lib/python3.9/site-packages/urllib3/connectionpool.py", line 1053, in _validate_conn
  conn.connect()
 File "/usr/local/lib/python3.9/site-packages/urllib3/connection.py", line 363, in connect
  self.sock = conn = self._new_conn()
 File "/usr/local/lib/python3.9/site-packages/urllib3/connection.py", line 186, in _new_conn
  raise NewConnectionError(
urllib3.exceptions.NewConnectionError: <urllib3.connection.HTTPSConnection object at 0x7f111cbc54f0>: Failed to establish a new connection: [Errno -3] Temporary failure in name resolution
    """
    def __init__(self, username: str, dwssap: str, edl_base_url: str = None, wait_time = 30, retry_times = 5) -> None:
        super().__init__()
        self.__default_edl_base_url = 'https://urs.earthdata.nasa.gov/'
        self.__username = username
        self.__dwssap = dwssap
        self.__edl_base_url = self.__default_edl_base_url if edl_base_url is None or edl_base_url == '' else edl_base_url.strip().lower()
        if not self.__edl_base_url.endswith('/'):
            self.__edl_base_url = f'{self.__edl_base_url}/'
        if not self.__edl_base_url.startswith('http'):
            self.__edl_base_url = f'https://{self.__edl_base_url}'
        self.__token = None
        self.__wait_time = wait_time
        self.__retry_times = retry_times


    @retry(wait=wait_random_exponential(multiplier=1, max=60),
           stop=stop_after_attempt(3),
           reraise=True,
           retry=(retry_if_result(lambda x: x == ''))
           )
    def create_token(self, url: str) -> str:
        token: str = ''
        try:
            headers: Dict = {'Accept': 'application/json'}  # noqa E501
            resp = requests.post(url + "/token", headers=headers, auth=HTTPBasicAuth(self.__username, self.__dwssap))
            if resp.status_code > 300:
                raise ValueError(f'invalid response code: {resp.status_code}. details: {resp.content}')
            response_content: Dict = json.loads(resp.content)
            if "error" in response_content:
                if response_content["error"] == "max_token_limit":
                    LOGGER.error("Max tokens acquired from URS. Using existing token")
                    tokens = self.list_tokens(url)
                    return tokens[0]
            if 'access_token' not in response_content:
                raise ValueError(f'access_token not found. {response_content}')
            token = response_content['access_token']

        # Add better error handling there
        # Max tokens
        # Wrong Username/Password
        # Other
        except Exception as e:  # noqa E722
            LOGGER.warning("Error getting the token - check user name and password", exc_info=True)
            raise RuntimeError(str(e))
        return token

    def list_tokens(self, url: str):
        tokens = []
        try:
            headers: Dict = {'Accept': 'application/json'}  # noqa E501
            resp = requests.get(url + "/tokens", headers=headers, auth=HTTPBasicAuth(self.__username, self.__dwssap))
            if resp.status_code >= 400:
                LOGGER.error(f'error response: {resp.status_code}. details: {resp.content}')
                return tokens
            response_content = json.loads(resp.content)

            for x in response_content:
                tokens.append(x['access_token'])

        except Exception as e:  # noqa E722
            LOGGER.warning("Error getting the token - check user name and password", exc_info=True)
        return tokens

    def setup_earthdata_login_auth(self):
        """
        Set up the request library so that it authenticates against the given
        Earthdata Login endpoint and is able to track cookies between requests.
        This looks in the .netrc file first and if no credentials are found,
        it prompts for them.
        Valid endpoints include:
            urs.earthdata.nasa.gov - Earthdata Login production
        """
        manager = request.HTTPPasswordMgrWithDefaultRealm()
        manager.add_password(None, self.__edl_base_url, self.__username, self.__dwssap)
        auth = request.HTTPBasicAuthHandler(manager)
        __version__ = "1.12.0"

        jar = CookieJar()
        processor = request.HTTPCookieProcessor(jar)
        opener = request.build_opener(auth, processor)
        opener.addheaders = [('User-agent', 'unity-downloader-' + __version__)]
        request.install_opener(opener)

    def delete_token(self, token: str) -> bool:
        try:
            self.setup_earthdata_login_auth()
            headers: Dict = {'Accept': 'application/json'}
            resp = requests.post(f'{self.__edl_base_url}revoke_token', params={"token": token}, headers=headers,
                                 auth=HTTPBasicAuth(self.__username, self.__dwssap))

            if resp.status_code == 200:
                LOGGER.info("EDL token successfully deleted")
                return True
            else:
                LOGGER.info("EDL token deleting failed.")

        except:  # noqa E722
            LOGGER.warning("Error deleting the token", exc_info=True)
        return False

    def __get_token_once(self):
        try:
            token_url = f'{self.__edl_base_url}api/users'
            tokens = self.list_tokens(token_url)
            if len(tokens) == 0:
                return self.create_token(token_url)
        except Exception as conn_err:
            if 'Temporary failure in name resolution' in str(conn_err):
                return self.DNS_ERROR_TXT
            raise conn_err
        return tokens[0]

    def get_token(self) -> str:
        token = self.__get_token_once()
        retry_count = 0
        while token == self.DNS_ERROR_TXT and retry_count < self.__retry_times:
            LOGGER.error(f'{self.DNS_ERROR_TXT} for URS Token. attempt: {retry_count}')
            time.sleep(self.__wait_time)
            token = self.__get_token_once()
            retry_count += 1
        return token


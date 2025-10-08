import time

import requests

from mdps_ds_lib.lib.earthdata_login.urs_token_retriever import URSTokenRetriever
from mdps_ds_lib.stage_in_out.download_granules_abstract import DownloadGranulesAbstract
import logging
import os


LOGGER = logging.getLogger(__name__)


class DownloadGranulesDAAC(DownloadGranulesAbstract):
    VALID_DOMAINS = ['EARTHDATA.NASA.GOV', 'EARTHDATACLOUD.NASA.GOV']

    def __init__(self) -> None:
        super().__init__()
        self.__edl_token = None
        self.__retry_wait_time_sec = int(os.environ.get('DOWNLOAD_RETRY_WAIT_TIME', '30'))
        self.__retry_times = int(os.environ.get('DOWNLOAD_RETRY_TIMES', '5'))

    @property
    def edl_token(self):
        return self.__edl_token

    @edl_token.setter
    def edl_token(self, val: str):
        """
        :param val:
        :return: None
        """
        self.__edl_token = val
        return

    def _set_props_from_env(self):
        missing_keys = [k for k in [self.STAC_JSON, self.DOWNLOAD_DIR_KEY] if k not in os.environ]
        if len(missing_keys) > 0:
            raise ValueError(f'missing environment keys: {missing_keys}')
        self._retrieve_stac_json()
        self._setup_download_dir()
        self.__edl_token = URSTokenRetriever().start()
        return self

    def download_one_item(self, downloading_url):
        if self.edl_token is None:
            raise ValueError(f'missing edl_token. Unable to download from DAAC')
        headers = {
            'Authorization': f'Bearer {self.edl_token}'
        }
        r = requests.get(downloading_url, headers=headers)
        download_count = 1
        while r.status_code in [502, 504] and download_count < self.__retry_times:
            LOGGER.error(f'502 or 504 while downloading {downloading_url}. attempt: {download_count}')
            time.sleep(self.__retry_wait_time_sec)
            r = requests.get(downloading_url, headers=headers)
            download_count += 1
        r.raise_for_status()
        local_file_path = os.path.join(self._download_dir, os.path.basename(downloading_url))
        with open(local_file_path, 'wb') as fd:
            fd.write(r.content)
        return local_file_path

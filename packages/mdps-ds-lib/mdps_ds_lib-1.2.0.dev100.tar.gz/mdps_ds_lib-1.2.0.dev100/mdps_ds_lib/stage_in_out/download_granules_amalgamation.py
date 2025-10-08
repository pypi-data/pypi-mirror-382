import logging
import os

from mdps_ds_lib.lib.earthdata_login.urs_token_retriever import URSTokenRetriever
from mdps_ds_lib.stage_in_out.download_granules_abstract import DownloadGranulesAbstract
from mdps_ds_lib.stage_in_out.download_granules_daac import DownloadGranulesDAAC
from mdps_ds_lib.stage_in_out.download_granules_http import DownloadGranulesHttp
from mdps_ds_lib.stage_in_out.download_granules_s3 import DownloadGranulesS3

LOGGER = logging.getLogger(__name__)


class DownloadGranulesAmalgamation(DownloadGranulesAbstract):
    def __init__(self) -> None:
        super().__init__()
        self.__edl_token = None

    def _set_props_from_env(self):
        missing_keys = [k for k in [self.STAC_JSON, self.DOWNLOAD_DIR_KEY] if k not in os.environ]
        if len(missing_keys) > 0:
            raise ValueError(f'missing environment keys: {missing_keys}')
        self._retrieve_stac_json()
        self._setup_download_dir()
        try:
            self.__edl_token = URSTokenRetriever().start()
        except Exception as e:
            LOGGER.exception(f'unable to get URS Token. which is not an issue if not used.')
            self.__edl_token = None
        return self

    def download_one_item(self, downloading_url: str):
        LOGGER.error(f'downloading: {downloading_url}')
        upper_download_url = downloading_url.upper()
        if upper_download_url.startswith('S3://'):
            download_s3 = DownloadGranulesS3()
            download_s3._download_dir = self._download_dir
            return download_s3.download_one_item(downloading_url)
        if not upper_download_url.startswith('HTTPS://'):
            raise ValueError(f'unknown URL to download: {downloading_url}')
        if any([k in upper_download_url for k in DownloadGranulesDAAC.VALID_DOMAINS]):
            download_daac = DownloadGranulesDAAC()
            download_daac.edl_token = self.__edl_token
            download_daac._download_dir = self._download_dir
            return download_daac.download_one_item(downloading_url)
        download_http = DownloadGranulesHttp()
        download_http._download_dir = self._download_dir
        return download_http.download_one_item(downloading_url)

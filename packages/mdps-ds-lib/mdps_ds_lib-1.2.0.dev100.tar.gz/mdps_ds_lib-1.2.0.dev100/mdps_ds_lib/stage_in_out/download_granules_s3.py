from mdps_ds_lib.stage_in_out.download_granules_abstract import DownloadGranulesAbstract
import logging
import os

from mdps_ds_lib.lib.aws.aws_s3 import AwsS3

LOGGER = logging.getLogger(__name__)


class DownloadGranulesS3(DownloadGranulesAbstract):

    def __init__(self) -> None:
        super().__init__()
        self.__s3 = AwsS3()

    def _set_props_from_env(self):
        missing_keys = [k for k in [self.STAC_JSON, self.DOWNLOAD_DIR_KEY] if k not in os.environ]
        if len(missing_keys) > 0:
            raise ValueError(f'missing environment keys: {missing_keys}')
        self._retrieve_stac_json()
        self._setup_download_dir()
        return self

    def download_one_item(self, downloading_url):
        local_file_path = self.__s3.set_s3_url(downloading_url).download(self._download_dir)
        return local_file_path

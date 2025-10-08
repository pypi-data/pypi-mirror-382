import json
import logging
import os
from abc import ABC, abstractmethod

from mdps_ds_lib.lib.utils.file_utils import FileUtils

LOGGER = logging.getLogger(__name__)


class CatalogGranulesAbstract(ABC):
    UPLOADED_FILES_JSON = 'UPLOADED_FILES_JSON'

    def __init__(self) -> None:
        super().__init__()
        self._uploaded_files_json = None

    def _retrieve_stac_json(self):
        uploaded_files_json_raw = os.environ.get(self.UPLOADED_FILES_JSON)
        try:
            self._uploaded_files_json = json.loads(uploaded_files_json_raw)
            return self
        except:
            LOGGER.debug(f'uploaded_files_json is not JSON: {uploaded_files_json_raw}. trying to see if file exists')
        if not FileUtils.file_exist(uploaded_files_json_raw):
            raise ValueError(f'missing file or not JSON: {uploaded_files_json_raw}')
        self._uploaded_files_json = FileUtils.read_json(uploaded_files_json_raw)
        if self._uploaded_files_json is None:
            raise ValueError(f'{uploaded_files_json_raw} is not JSON')
        return self

    @abstractmethod
    def catalog(self, **kwargs):
        raise NotImplementedError()

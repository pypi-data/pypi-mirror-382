import json
import logging
import os
from typing import Union

from mdps_ds_lib.lib.utils.file_utils import FileUtils

LOGGER = logging.getLogger(__name__)


class StageInOutUtils:
    OUTPUT_FILE = 'OUTPUT_FILE'
    CATALOG_DEFAULT_CHUNK_SIZE = 5

    @staticmethod
    def write_output_to_file(output_json: Union[dict, str, list]):
        if StageInOutUtils.OUTPUT_FILE not in os.environ:
            LOGGER.debug(f'Not writing output to file due to missing {StageInOutUtils.OUTPUT_FILE} in ENV')
            return
        output_filepath = os.environ.get(StageInOutUtils.OUTPUT_FILE)
        FileUtils.mk_dir_p(os.path.dirname(output_filepath))
        output_str = json.dumps(output_json) if not isinstance(output_json, str) else output_json
        with open(output_filepath, 'w') as ff:
            ff.write(output_str)
        return

    @staticmethod
    def chunk_list(input_list, chunked_size):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(input_list), chunked_size):
            yield input_list[i:i + chunked_size]
        return

import logging

# Define the new log level AUDIT
AUDIT_LEVEL = 60
logging.addLevelName(AUDIT_LEVEL, "AUDIT")


# Define a custom method for logging at AUDIT level
def audit(self, message, *args, **kwargs):
    if self.isEnabledFor(AUDIT_LEVEL):
        self._log(AUDIT_LEVEL, message, args, **kwargs)


logging.Logger.audit = audit

import os
from abc import ABC, abstractmethod

from mdps_ds_lib.lib.constants import Constants


class UploadGranulesAbstract(ABC):
    RESULT_PATH_PREFIX = 'RESULT_PATH_PREFIX'  # s3 prefix
    DEFAULT_RESULT_PATH_PREFIX = 'stage_out'  # default s3 prefix
    OUTPUT_DIRECTORY = 'OUTPUT_DIRECTORY'  # To store successful & failed features json
    COLLECTION_ID_KEY = 'COLLECTION_ID'  # Need this only for arbitrary upload
    PROJECT_KEY = 'PROJECT'  # Need this only for process stageout
    VENUE_KEY = 'VENUE'  # Need this only for process stageout
    STAGING_BUCKET_KEY = 'STAGING_BUCKET'  # S3 Bucket
    VERIFY_SSL_KEY = 'VERIFY_SSL'
    DELETE_FILES_KEY = 'DELETE_FILES'
    DRY_RUN = 'DRY_RUN'

    def __init__(self) -> None:
        super().__init__()
        self._collection_id = ''
        self._project = ''
        self._venue = ''
        self._staging_bucket = ''
        self._result_path_prefix = ''
        self._parallel_count = int(os.environ.get(Constants.PARALLEL_COUNT, '-1'))
        self._retry_wait_time_sec = int(os.environ.get('UPLOAD_RETRY_WAIT_TIME', '30'))
        self._retry_times = int(os.environ.get('UPLOAD_RETRY_TIMES', '5'))
        self._verify_ssl = True
        self._dry_run = False
        self._delete_files = False

    def _set_props_from_env(self):
        missing_keys = [k for k in [self.STAGING_BUCKET_KEY] if k not in os.environ]
        if len(missing_keys) > 0:
            raise ValueError(f'missing environment keys: {missing_keys}')

        self._dry_run = os.environ.get(self.DRY_RUN, 'FALSE').upper().strip() == 'TRUE'
        self._collection_id = os.environ.get(self.COLLECTION_ID_KEY)
        self._project = os.environ.get(self.PROJECT_KEY)
        self._venue = os.environ.get(self.VENUE_KEY)
        self._staging_bucket = os.environ.get(self.STAGING_BUCKET_KEY)
        self._result_path_prefix = os.environ.get(self.RESULT_PATH_PREFIX, self.DEFAULT_RESULT_PATH_PREFIX)
        if self._result_path_prefix is None or self._result_path_prefix.strip() == '':
            self._result_path_prefix = self.DEFAULT_RESULT_PATH_PREFIX
        self._result_path_prefix = self._result_path_prefix[:-1] if self._result_path_prefix.endswith('/') else self._result_path_prefix
        self._result_path_prefix = self._result_path_prefix[1:] if self._result_path_prefix.startswith('/') else self._result_path_prefix

        self._verify_ssl = os.environ.get(self.VERIFY_SSL_KEY, 'TRUE').strip().upper() == 'TRUE'
        self._delete_files = os.environ.get(self.DELETE_FILES_KEY, 'FALSE').strip().upper() == 'TRUE'
        return self

    @abstractmethod
    def upload(self, **kwargs) -> str:
        raise NotImplementedError()

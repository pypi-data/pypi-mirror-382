import logging
import os
from glob import glob

from mdps_ds_lib.lib.processing_jobs.job_manager_abstract import JobManagerAbstract, JobManagerProps
from mdps_ds_lib.lib.utils.file_utils import FileUtils

LOGGER = logging.getLogger(__name__)


class JobManagerLocalFileSystem(JobManagerAbstract):
    def __init__(self, props=JobManagerProps()) -> None:
        super().__init__()
        self.__props = props

    def get_all_job_files(self):
        return [k.replace(self.__props.job_bucket, '')[1:] for k in glob(os.path.join(self.__props.job_bucket, self.__props.job_path, f'*{self.__props.job_file_postfix}'))]

    def get_job_file(self, job_path, validate_job_content=lambda x: True):
        job_abs_path = os.path.join(self.__props.job_bucket, job_path)
        with self.__props.lock:
            try:
                job_content = FileUtils.read_json(job_abs_path)
            except:
                LOGGER.exception(f'job in this path is not in JSON: {job_path}')
                return None
            FileUtils.remove_if_exists(job_abs_path)
        if validate_job_content(job_content) is False:
            LOGGER.error(f'{job_path} does not have valid json: {job_content}. Putting back')
            FileUtils.write_json(job_abs_path, job_content, overwrite=True)
            return None
        LOGGER.debug(f'writing job to processing path')
        FileUtils.mk_dir_p(os.path.join(self.__props.job_bucket, self.__props.processing_job_path))
        FileUtils.write_json(os.path.join(self.__props.job_bucket, self.__props.processing_job_path, os.path.basename(job_path)), job_content, overwrite=True)
        return job_content

    def put_back_failed_job(self, original_job_path: str):
        processing_job_path = os.path.join(self.__props.processing_job_path, os.path.basename(original_job_path))
        LOGGER.debug(f'reading failed job file: {processing_job_path}')
        try:
            job_json: dict = FileUtils.read_json(os.path.join(self.__props.job_bucket, processing_job_path))
            LOGGER.debug(f'deleting failed job file from processing dir: {processing_job_path}')
            FileUtils.remove_if_exists(os.path.join(self.__props.job_bucket, processing_job_path))
            LOGGER.debug(f'uploading failed job back to folder')
            FileUtils.write_json(os.path.join(self.__props.job_bucket, original_job_path), job_json)
        except Exception as e:
            LOGGER.exception(f'error while reading failed job file from from processing dir: {processing_job_path}')
        return

    def remove_from_processing(self, job_path):
        FileUtils.remove_if_exists(os.path.join(self.__props.job_bucket, self.__props.processing_job_path, os.path.basename(job_path)))
        return True

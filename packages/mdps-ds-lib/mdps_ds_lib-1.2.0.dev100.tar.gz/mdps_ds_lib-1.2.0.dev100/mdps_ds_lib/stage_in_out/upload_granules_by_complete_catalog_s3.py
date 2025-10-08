import json
import sys
from multiprocessing import Manager

from mdps_ds_lib.lib.utils.time_utils import TimeUtils

from mdps_ds_lib.lib.utils.file_utils import FileUtils

from pystac import ItemCollection, Item

from mdps_ds_lib.lib.cumulus_stac.granules_catalog import GranulesCatalog
from mdps_ds_lib.lib.processing_jobs.job_executor_abstract import JobExecutorAbstract
from mdps_ds_lib.lib.processing_jobs.job_manager_abstract import JobManagerProps
from mdps_ds_lib.lib.processing_jobs.job_manager_memory import JobManagerMemory
from mdps_ds_lib.lib.processing_jobs.multithread_processor import MultiThreadProcessorProps, \
    MultiThreadProcessor
from mdps_ds_lib.stage_in_out.upload_granules_abstract import UploadGranulesAbstract
import logging
import os
from mdps_ds_lib.lib.aws.aws_s3 import AwsS3

LOGGER = logging.getLogger(__name__)


class UploadItemExecutor(JobExecutorAbstract):
    def __init__(self, result_list, error_list, project_venue_set, staging_bucket, retry_wait_time_sec, retry_times, delete_files: bool, dry_run=False) -> None:
        super().__init__()
        self.__dry_run = dry_run
        self.__project_venue_set = project_venue_set
        self.__staging_bucket = staging_bucket
        self.__delete_files = delete_files

        self.__result_list = result_list
        self.__error_list = error_list
        self.__gc = GranulesCatalog()
        self.__s3 = AwsS3()
        self.__retry_wait_time_sec = retry_wait_time_sec
        self.__retry_times = retry_times

    def validate_job(self, job_obj):
        return True

    # def __upload_function_w_retry(self, ):
    # NOTE: 2023-10-09: we are not proceeding with "retry" logic at this moment as most the errors (when failed to upload) are not transient.
    #     upload_try_count = 1
    #     while r.status_code in [502, 504] and upload_try_count < self.__retry_times:
    #         LOGGER.error(f'502 or 504 while downloading {upload_try_count}. attempt: {upload_try_count}')
    #         time.sleep(self.__retry_wait_time_sec)
    #         upload_try_count += 1
    #     return

    def __exec_actual_job(self, each_child, lock) -> bool:
        try:
            current_granule_stac: Item = self.__gc.get_granules_item(each_child)
            current_collection_id = current_granule_stac.collection_id.strip()
        except Exception as e:
            LOGGER.exception(f'error while processing: {each_child}')
            error_item = Item(id='unknown',
                              properties={'message': 'unknown error', 'granule': each_child, 'details': str(e)},
                              geometry={
                                  "type": "Point",
                                  "coordinates": [0.0, 0.0]
                              },
                              bbox=[-180, -90, 180, 90],
                              datetime=TimeUtils().parse_from_unix(0, True).get_datetime_obj(),
                              collection='unknown')
            self.__error_list.put(error_item.to_dict(False, False))
            return True
        try:
            current_collection_id = GranulesCatalog.get_unity_formatted_collection_id(current_collection_id, self.__project_venue_set)
            LOGGER.debug(f'reformatted current_collection_id: {current_collection_id}')
            current_granules_dir = os.path.dirname(each_child)
            current_assets = self.__gc.extract_assets_href(current_granule_stac, current_granules_dir)  # returns defaultdict(list)
            if 'data' not in current_assets:  # this is still ok .coz extract_assets_href is {'data': [url1, url2], ...}
                LOGGER.warning(f'skipping {each_child}. no data in {current_assets}')
                current_granule_stac.properties['upload_error'] = f'missing "data" in assets'
                self.__error_list.put(current_granule_stac.to_dict(False, False))
                return True
            current_granule_id = str(current_granule_stac.id)
            if current_granule_id in ['', 'NA', None]:
                raise ValueError(f'invalid current_granule_id in granule {each_child}: {current_granule_id} ...')
            updating_assets = {}
            uploading_current_granule_stac = None
            for asset_type, asset_hrefs in current_assets.items():
                for asset_name, asset_href in asset_hrefs.items():
                    LOGGER.audit(f'uploading type={asset_type}, name={asset_name}, href={asset_href}')
                    s3_url = self.__s3.upload(asset_href, self.__staging_bucket,
                                              f'{current_collection_id}/{current_collection_id}:{current_granule_id}',
                                              self.__delete_files)
                    if asset_href == each_child:
                        uploading_current_granule_stac = s3_url
                    updating_assets[asset_name] = s3_url
            self.__gc.update_assets_href(current_granule_stac, updating_assets)
            current_granule_stac.id = current_granule_id
            current_granule_stac.collection_id = current_collection_id
            if uploading_current_granule_stac is not None:  # upload metadata file again
                self.__s3.set_s3_url(uploading_current_granule_stac)
                self.__s3.upload_bytes(json.dumps(current_granule_stac.to_dict(False, False)).encode())
            current_granule_stac.id = f'{current_collection_id}:{current_granule_id}'
            self.__result_list.put(current_granule_stac.to_dict(False, False))
        except Exception as e:
            current_granule_stac.properties['upload_error'] = str(e)
            LOGGER.exception(f'error while processing: {each_child}')
            self.__error_list.put(current_granule_stac.to_dict(False, False))
        return True

    def __exec_dry_run(self, each_child, lock) -> bool:
        local_errors, local_results = [], []
        try:
            current_granule_stac: Item = self.__gc.get_granules_item(each_child)
        except Exception as e:
            local_errors.append({
                'granule_file': each_child,
                'error': 'unable to read the stac file',
                'details': str(e)
            })
            if len(local_errors) > 0:
                self.__error_list.put(local_errors)
            if len(local_results) > 0:
                self.__result_list.put(local_results)

            return True
        current_collection_id = current_granule_stac.collection_id.strip()
        try:
            current_collection_id = GranulesCatalog.get_unity_formatted_collection_id(current_collection_id, self.__project_venue_set)
            LOGGER.debug(f'reformatted current_collection_id: {current_collection_id}')
            current_granules_dir = os.path.dirname(each_child)
            current_assets = self.__gc.extract_assets_href(current_granule_stac,
                                                           current_granules_dir)  # returns defaultdict(list)

            if 'data' not in current_assets:  # this is still ok .coz extract_assets_href is {'data': [url1, url2], ...}
                local_errors.append({
                    'granule_file': each_child,
                    'error': 'missing "data" in assets',
                    'details': current_assets,
                })
            current_granule_id = str(current_granule_stac.id)
            if current_granule_id in ['', 'NA', None]:
                local_errors.append({
                    'granule_file': each_child,
                    'error': 'invalid current_granule_id in granule',
                    'details': current_granule_id,
                })
                current_granule_id = 'INVALID_GRANULE_ID'
            for asset_type, asset_hrefs in current_assets.items():
                for asset_name, asset_href in asset_hrefs.items():
                    if not FileUtils.file_exist(asset_href):
                        local_errors.append({
                            'granule_file': each_child,
                            'error': f'missing uploading file for {asset_type} - {asset_name}',
                            'details': asset_href,
                        })
                    local_results.append({
                        'granule_file': each_child,
                        's3_url': f's3://{self.__staging_bucket}/{current_collection_id}/{current_collection_id}:{current_granule_id}/{os.path.basename(asset_href)}'
                    })
        except Exception as e:
            local_errors.append({
                'granule_file': each_child,
                'error': 'unexpected error',
                'details': str(e),
            })
            LOGGER.exception(f'error while processing: {each_child}')
        if len(local_errors) > 0:
            self.__error_list.put(local_errors)
        if len(local_results) > 0:
            self.__result_list.put(local_results)
        return True

    def execute_job(self, each_child, lock) -> bool:
        if not self.__dry_run:
            return self.__exec_actual_job(each_child, lock)
        return self.__exec_dry_run(each_child, lock)



class UploadGranulesByCompleteCatalogS3(UploadGranulesAbstract):
    CATALOG_FILE = 'CATALOG_FILE'

    def __init__(self) -> None:
        super().__init__()
        self.__gc = GranulesCatalog()
        self.__s3 = AwsS3()

    def __actual_upload(self):
        output_dir = os.environ.get(self.OUTPUT_DIRECTORY)
        if not FileUtils.dir_exist(output_dir):
            raise ValueError(f'OUTPUT_DIRECTORY: {output_dir} does not exist')
        missing_keys = [k for k in [self.CATALOG_FILE] if k not in os.environ]
        if len(missing_keys) > 0:
            raise ValueError(f'missing environment keys: {missing_keys}')
        catalog_file_path = os.environ.get(self.CATALOG_FILE)
        child_links = self.__gc.get_child_link_hrefs(catalog_file_path)
        local_items = Manager().Queue()
        error_list = Manager().Queue()
        job_manager_props = JobManagerProps()
        for each_child in child_links:
            job_manager_props.memory_job_dict[each_child] = each_child

        project_venue_set = (self._project, self._venue)
        # https://www.infoworld.com/article/3542595/6-python-libraries-for-parallel-processing.html
        multithread_processor_props = MultiThreadProcessorProps(self._parallel_count)
        multithread_processor_props.job_manager = JobManagerMemory(job_manager_props)
        multithread_processor_props.job_executor = UploadItemExecutor(local_items, error_list, project_venue_set, self._staging_bucket, self._retry_wait_time_sec, self._retry_times, self._delete_files)
        multithread_processor = MultiThreadProcessor(multithread_processor_props)
        multithread_processor.start()

        LOGGER.debug(f'finished uploading all granules')
        dapa_body_granules = []
        while not local_items.empty():
            dapa_body_granules.append(local_items.get())

        errors = []
        while not error_list.empty():
            errors.append(error_list.get())
        LOGGER.debug(f'successful count: {len(dapa_body_granules)}. failed count: {len(errors)}')
        successful_item_collections = ItemCollection(items=dapa_body_granules)
        failed_item_collections = ItemCollection(items=errors)
        successful_features_file = os.path.join(output_dir, 'successful_features.json')

        failed_features_file = os.path.join(output_dir, 'failed_features.json')
        LOGGER.debug(f'writing results: {successful_features_file} && {failed_features_file}')
        FileUtils.write_json(successful_features_file, successful_item_collections.to_dict(False))
        FileUtils.write_json(failed_features_file, failed_item_collections.to_dict(False))
        if len(failed_item_collections.items) > 0:
            LOGGER.fatal(f'One or more Failures: {failed_item_collections.to_dict(False)}')

        LOGGER.debug(f'creating response catalog')
        catalog_json = GranulesCatalog().update_catalog(catalog_file_path, [successful_features_file, failed_features_file])
        LOGGER.debug(f'catalog_json: {catalog_json}')
        if len(successful_item_collections) < 1:  # TODO check this.
            LOGGER.debug(f'No successful items in Upload: Not uploading successful_features_ to s3://{self._staging_bucket}/{self._result_path_prefix}')
            return json.dumps(catalog_json)

        s3_url = self.__s3.upload(successful_features_file, self._staging_bucket,
                                  self._result_path_prefix,
                                  s3_name=f'successful_features_{TimeUtils.get_current_time()}.json',
                                  delete_files=self._delete_files)
        LOGGER.debug(f'uploaded successful features to S3: {s3_url}')
        return json.dumps(catalog_json)

    def __exec_dry_run(self):
        local_items = Manager().Queue()
        error_list = Manager().Queue()

        errors = []
        results = []
        if self.OUTPUT_DIRECTORY not in os.environ:
            errors.append({
                'error': f'missing {self.OUTPUT_DIRECTORY} to write result files'
            })
        else:
            output_dir = os.environ.get(self.OUTPUT_DIRECTORY)
            if not FileUtils.dir_exist(output_dir):
                errors.append({
                    'error': f'OUTPUT_DIRECTORY: {output_dir} does not exist'
                })
        catalog_file_path = os.environ.get(self.CATALOG_FILE)
        child_links = self.__gc.get_child_link_hrefs(catalog_file_path)

        job_manager_props = JobManagerProps()
        for each_child in child_links:
            job_manager_props.memory_job_dict[each_child] = each_child

        project_venue_set = (self._project, self._venue)
        # https://www.infoworld.com/article/3542595/6-python-libraries-for-parallel-processing.html
        multithread_processor_props = MultiThreadProcessorProps(self._parallel_count)
        multithread_processor_props.job_manager = JobManagerMemory(job_manager_props)
        multithread_processor_props.job_executor = UploadItemExecutor(local_items, error_list, project_venue_set, self._staging_bucket, self._retry_wait_time_sec, self._retry_times, self._delete_files, True)
        multithread_processor = MultiThreadProcessor(multithread_processor_props)
        multithread_processor.start()

        LOGGER.debug(f'finished dry-run uploading all granules')
        while not local_items.empty():
            results.extend(local_items.get())

        while not error_list.empty():
            errors.extend(error_list.get())

        if len(errors) > 0:
            print('There are ERRORS in the setup.', file=sys.stderr)
            for each in errors:
                print(json.dumps(each, indent=4), file=sys.stderr)
            return "{}"
        print('Result of dry-run')
        for each in results:
            print(json.dumps(each, indent=4))
        return "{}"

    def upload(self, **kwargs) -> str:
        self._set_props_from_env()
        if self._dry_run:
            return self.__exec_dry_run()
        return self.__actual_upload()


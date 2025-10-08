import json
import logging
import os
from abc import ABC, abstractmethod
from multiprocessing import Manager

import requests
from mdps_ds_lib.lib.cognito_login.cognito_token_retriever import CognitoTokenRetriever

from mdps_ds_lib.lib.constants import Constants
from pystac import ItemCollection, Asset, Item, Catalog, Link

from mdps_ds_lib.lib.processing_jobs.job_executor_abstract import JobExecutorAbstract
from mdps_ds_lib.lib.processing_jobs.job_manager_abstract import JobManagerProps
from mdps_ds_lib.lib.processing_jobs.job_manager_memory import JobManagerMemory
from mdps_ds_lib.lib.processing_jobs.multithread_processor import MultiThreadProcessorProps, \
    MultiThreadProcessor
from mdps_ds_lib.lib.utils.file_utils import FileUtils

LOGGER = logging.getLogger(__name__)


class DownloadItemExecutor(JobExecutorAbstract):
    def __init__(self, downloading_keys, downloading_roles, download_one_item_func, result_list, error_list) -> None:
        self._downloading_keys = downloading_keys
        self._downloading_roles = downloading_roles
        self._download_one_item_func = download_one_item_func
        self.__result_list = result_list
        self.__error_list = error_list

    def validate_job(self, job_obj):
        return isinstance(job_obj, Item)

    def __is_downloading_this_file(self, file_key, file_role):
        if len(self._downloading_roles) > 0:
            role_comparison_result = file_role in self._downloading_roles
            LOGGER.debug(f'Result for role comparison for {file_key}, {file_role} v. {self._downloading_roles}. Result: {role_comparison_result}')
            return role_comparison_result
        if len(self._downloading_keys) > 0:
            key_comparison_result = file_key in self._downloading_keys
            LOGGER.debug(f'Result for role comparison for {file_key}, {file_role} v. {self._downloading_keys}. Result: {key_comparison_result}')
            return key_comparison_result
        LOGGER.debug(f'both _downloading_keys and _downloading_roles are not set. Downloading: {file_key}, {file_role}')
        return True

    def execute_job(self, granule_item, lock) -> bool:
        try:
            new_asset_dict = {}
            for name, value_dict in granule_item.assets.items():
                value_dict: Asset = value_dict
                role = value_dict.roles[0] if value_dict.roles is not None and len(value_dict.roles) > 0 else 'unknown'
                if not self.__is_downloading_this_file(name, role):
                    LOGGER.debug(f'skipping {name}. Not in downloading keys')
                    continue
                downloading_url = value_dict.href
                LOGGER.debug(f'downloading: {downloading_url}')
                self._download_one_item_func(downloading_url)
                value_dict.href = os.path.join('', os.path.basename(downloading_url))
                new_asset_dict[name] = value_dict
            granule_item.assets = new_asset_dict
            self.__result_list.put(granule_item)
        except Exception as e:
            LOGGER.exception(f'error downloading granule: {granule_item.id}')
            self.__error_list.put({'error': str(e), 'id': granule_item.id, })
        LOGGER.debug(f'done DownloadItemExecutor#execute_job')
        return True  # always return true?


class DownloadGranulesAbstract(ABC):
    STAC_AUTH_TYPE = 'STAC_AUTH_TYPE'
    STAC_JSON = 'STAC_JSON'
    DOWNLOAD_DIR_KEY = 'DOWNLOAD_DIR'
    DOWNLOADING_KEYS = 'DOWNLOADING_KEYS'
    DOWNLOADING_ROLES = 'DOWNLOADING_ROLES'
    VERIFY_SSL_KEY = 'VERIFY_SSL_KEY'

    def __init__(self) -> None:
        super().__init__()
        self._granules_json: ItemCollection = {}
        self._download_dir = '/tmp'
        self._downloading_roles = os.environ.get(self.DOWNLOADING_ROLES, '')
        self._downloading_roles = set([]) if self._downloading_roles == '' else set([k.strip() for k in self._downloading_roles.strip().split(',')])
        self._downloading_keys = os.environ.get(self.DOWNLOADING_KEYS, '')
        self._downloading_keys = set([]) if self._downloading_keys == '' else set([k.strip() for k in self._downloading_keys.strip().split(',')])
        self._parallel_count = int(os.environ.get(Constants.PARALLEL_COUNT, '-1'))

    @abstractmethod
    def _set_props_from_env(self):
        raise NotImplementedError(f'to be implemented in concrete classes')

    @abstractmethod
    def download_one_item(self, downloading_url):
        raise NotImplementedError(f'to be implemented in concrete classes')

    def _setup_download_dir(self):
        self._download_dir = os.environ.get(self.DOWNLOAD_DIR_KEY)
        self._download_dir = self._download_dir[:-1] if self._download_dir.endswith('/') else self._download_dir
        LOGGER.debug(f'creating download dir: {self._download_dir}')
        FileUtils.mk_dir_p(self._download_dir)
        return self

    def _retrieve_stac_json(self):
        raw_stac_json = os.environ.get(self.STAC_JSON)
        LOGGER.debug(f'attempting to decode raw_stac_json to JSON object')
        try:
            self._granules_json = ItemCollection.from_dict(json.loads(raw_stac_json))
            return self
        except:
            LOGGER.debug(f'raw_stac_json is not STAC_JSON: {raw_stac_json}. trying to see if file exists')

        if raw_stac_json.startswith('https'):
            if os.environ.get(self.STAC_AUTH_TYPE, 'NONE').strip().upper() == 'UNITY':
                LOGGER.debug(f'STAC_AUTH_TYPE = UNITY')
                token_retriever = CognitoTokenRetriever()
                token = token_retriever.start()
                header = {'Authorization': f'Bearer {token}'}
                verify_ssl = os.environ.get(self.VERIFY_SSL_KEY, 'TRUE').strip().upper() == 'TRUE'
                downloading_response = requests.get(url=raw_stac_json, headers=header, verify=verify_ssl)
            else:
                LOGGER.debug(f'download raw stac json from public URL: {raw_stac_json}')
                downloading_response = requests.get(raw_stac_json)
            downloading_response.raise_for_status()
            self._granules_json = ItemCollection.from_dict(json.loads(downloading_response.content.decode()))
            return self
        if not FileUtils.file_exist(raw_stac_json):
            raise ValueError(f'missing file or not JSON: {raw_stac_json}')
        json_stac = FileUtils.read_json(raw_stac_json)
        if json_stac is None:
            raise ValueError(f'{raw_stac_json} is not JSON')
        self._granules_json = ItemCollection.from_dict(json_stac)
        return self
    
    def download(self, **kwargs) -> str:
        self._set_props_from_env()
        LOGGER.debug(f'creating download dir: {self._download_dir}')

        catalog = Catalog(
            id='NA',
            description='NA')
        catalog.add_link(Link('root', f'catalog.json', 'application/json'))
        if len(self._granules_json.items) < 1:
            LOGGER.warning(f'cannot find any granules')
            granules_json_dict = self._granules_json.to_dict(False)
            FileUtils.write_json(os.path.join(self._download_dir, 'catalog.json'), catalog.to_dict(False, False), overwrite=True, prettify=True)
            return json.dumps(granules_json_dict)
        # local_items = []
        # error_list = []
        local_items = Manager().Queue()
        error_list = Manager().Queue()
        job_manager_props = JobManagerProps()
        for each_item in self._granules_json.items:
            job_manager_props.memory_job_dict[each_item.id] = each_item

        # https://www.infoworld.com/article/3542595/6-python-libraries-for-parallel-processing.html
        multithread_processor_props = MultiThreadProcessorProps(self._parallel_count)
        multithread_processor_props.job_manager = JobManagerMemory(job_manager_props)
        multithread_processor_props.job_executor = DownloadItemExecutor(self._downloading_keys, self._downloading_roles, self.download_one_item, local_items, error_list)
        multithread_processor = MultiThreadProcessor(multithread_processor_props)
        multithread_processor.start()

        LOGGER.debug(f'finished downloading all granules')
        local_items_list = []
        while not local_items.empty():
            local_items_list.append(local_items.get())

        error_list_list = []
        while not error_list.empty():
            error_list_list.append(error_list.get())

        for each_local_stac_item in local_items_list:
            local_stac_item_id_updated = each_local_stac_item.id.replace(':', '-').replace('/', '-').replace('\\', '-')
            FileUtils.write_json(os.path.join(self._download_dir, f'{local_stac_item_id_updated}.stac.json'),
                                 each_local_stac_item.to_dict(False, False), overwrite=False, prettify=True)
            catalog.add_link(Link('item', f'{local_stac_item_id_updated}.stac.json', 'application/json'))
        self._granules_json.items = local_items_list
        LOGGER.debug(f'writing features collection json to downloading directory')
        granules_json_dict = self._granules_json.to_dict(transform_hrefs=False)
        # TODO throw error when there is a <id>.stac.json
        FileUtils.write_json(os.path.join(self._download_dir, 'catalog.json'), catalog.to_dict(False, False), overwrite=True, prettify=True)
        LOGGER.debug(f'writing errors if any')
        if len(error_list_list) > 0:
            with open(f'{self._download_dir}/error.log', 'w') as error_file:
                error_file.write(json.dumps(error_list_list, indent=4))
        return json.dumps(granules_json_dict)

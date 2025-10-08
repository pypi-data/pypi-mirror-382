
from mdps_ds_lib.lib.processing_jobs.job_manager_abstract import JobManagerProps
from mdps_ds_lib.lib.processing_jobs.job_manager_local_filesystem import JobManagerLocalFileSystem
from mdps_ds_lib.lib.processing_jobs.job_manager_memory import JobManagerMemory
from mdps_ds_lib.lib.utils.factory_abstract import FactoryAbstract


class JobManagerFactory(FactoryAbstract):
    MEMORY = 'MEMORY'
    LOCAL = 'LOCAL'
    def get_instance(self, class_type, **kwargs):
        props = JobManagerProps().load_from_json(kwargs)
        fr = class_type.upper()
        if fr == self.LOCAL:
            return JobManagerLocalFileSystem(props)
        if fr == self.MEMORY:
            return JobManagerMemory(props)
        raise ModuleNotFoundError(f'cannot find JobManagerFactory class for {class_type}')

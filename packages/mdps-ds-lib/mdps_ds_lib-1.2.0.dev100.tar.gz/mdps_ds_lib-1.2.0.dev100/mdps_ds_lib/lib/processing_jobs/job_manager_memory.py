from mdps_ds_lib.lib.processing_jobs.job_manager_abstract import JobManagerAbstract, JobManagerProps


class JobManagerMemory(JobManagerAbstract):
    def __init__(self, props=JobManagerProps()) -> None:
        self.__props = props
        self.__processing_job_dict = {}

    def get_all_job_files(self):
        return [k for k in self.__props.memory_job_dict.keys()]

    def get_job_file(self, job_path, validate_job_content=lambda x: True):
        if job_path not in self.__props.memory_job_dict:
            return None
        job = self.__props.memory_job_dict.get(job_path)
        del self.__props.memory_job_dict[job_path]
        if not validate_job_content(job):
            return None
        self.__processing_job_dict[job_path] = job
        return job

    def remove_from_processing(self, job_path):
        if job_path not in self.__processing_job_dict:
            return
        del self.__processing_job_dict[job_path]
        pass

    def put_back_failed_job(self, original_job_path: str):
        if original_job_path not in self.__processing_job_dict:
            return
        self.__props.memory_job_dict[original_job_path] = self.__processing_job_dict[original_job_path]
        del self.__processing_job_dict[original_job_path]
        return

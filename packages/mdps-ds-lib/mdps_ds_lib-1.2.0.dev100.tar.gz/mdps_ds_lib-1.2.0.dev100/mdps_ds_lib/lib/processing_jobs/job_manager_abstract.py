from abc import ABCMeta, abstractmethod

from mdps_ds_lib.lib.utils.fake_lock import FakeLock


class JobManagerProps:
    def __init__(self):
        self.__job_bucket = None
        self.__job_path = None
        self.__job_file_postfix = ''
        self.__processing_job_path = None
        self.__lock = FakeLock()
        self.__memory_job_dict = {}

    @property
    def memory_job_dict(self):
        return self.__memory_job_dict

    @memory_job_dict.setter
    def memory_job_dict(self, val):
        """
        :param val:
        :return: None
        """
        self.__memory_job_dict = val
        return

    def load_from_json(self, input_json: dict):
        if 'memory_job_dict' in input_json:
            self.memory_job_dict = input_json['memory_job_dict']
        if 'job_bucket' in input_json:
            self.job_bucket = input_json['job_bucket']
        if 'job_path' in input_json:
            self.job_path = input_json['job_path']
        if 'processing_job_path' in input_json:
            self.processing_job_path = input_json['processing_job_path']
        if 'job_file_postfix' in input_json:
            self.job_file_postfix = input_json['job_file_postfix']
        return self

    @property
    def job_file_postfix(self):
        return self.__job_file_postfix

    @job_file_postfix.setter
    def job_file_postfix(self, val):
        """
        :param val:
        :return: None
        """
        self.__job_file_postfix = val
        return

    @property
    def lock(self):
        return self.__lock

    @lock.setter
    def lock(self, val):
        """
        :param val:
        :return: None
        """
        self.__lock = val
        return

    @property
    def job_bucket(self):
        return self.__job_bucket

    @job_bucket.setter
    def job_bucket(self, val):
        """
        :param val:
        :return: None
        """
        self.__job_bucket = val
        return

    @property
    def job_path(self):
        return self.__job_path

    @job_path.setter
    def job_path(self, val):
        """
        :param val:
        :return: None
        """
        self.__job_path = val
        return

    @property
    def processing_job_path(self):
        return self.__processing_job_path

    @processing_job_path.setter
    def processing_job_path(self, val):
        """
        :param val:
        :return: None
        """
        self.__processing_job_path = val
        return


class JobManagerAbstract(metaclass=ABCMeta):
    @abstractmethod
    def get_all_job_files(self):
        return

    @abstractmethod
    def get_job_file(self, job_path, validate_job_content=lambda x: True):
        return

    @abstractmethod
    def remove_from_processing(self, job_path):
        return

    @abstractmethod
    def put_back_failed_job(self, original_job_path: str):
        return
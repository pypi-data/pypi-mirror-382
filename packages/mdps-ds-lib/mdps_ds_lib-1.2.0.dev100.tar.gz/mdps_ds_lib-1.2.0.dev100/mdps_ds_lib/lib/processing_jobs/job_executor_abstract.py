from abc import ABCMeta, abstractmethod


class JobExecutorAbstract(metaclass=ABCMeta):
    @abstractmethod
    def validate_job(self, job_obj):
        return

    @abstractmethod
    def execute_job(self, job_obj, lock) -> bool:
        return

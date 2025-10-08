import logging
import time
import multiprocessing
multiprocessing.set_start_method("fork")
from multiprocessing import Process, Queue, Lock, cpu_count
from random import randint

from mdps_ds_lib.lib.processing_jobs.job_executor_abstract import JobExecutorAbstract
from mdps_ds_lib.lib.processing_jobs.job_manager_abstract import JobManagerAbstract

LOGGER = logging.getLogger(__name__)


class MultiThreadProcessorProps:
    def __init__(self, process_count: int = -1):
        self.__consumers = []
        self.__message_queue = Queue()
        self.__lock = Lock()
        self.__process_count = process_count
        if self.__process_count < 0:
            self.__process_count = cpu_count()
        self.__end_flag = 'end_of_queue'
        self.__job_manager: JobManagerAbstract = None
        self.__job_executor: JobExecutorAbstract = None

    @property
    def job_executor(self):
        return self.__job_executor

    @job_executor.setter
    def job_executor(self, val: JobExecutorAbstract):
        """
        :param val: JobExecutorAbstract
        :return: None
        """
        self.__job_executor = val
        return

    @property
    def job_manager(self):
        return self.__job_manager

    @job_manager.setter
    def job_manager(self, val: JobManagerAbstract):
        """
        :param val:
        :return: None
        """
        self.__job_manager = val
        return

    @property
    def end_flag(self):
        return self.__end_flag

    @end_flag.setter
    def end_flag(self, val):
        """
        :param val:
        :return: None
        """
        self.__end_flag = val
        return

    @property
    def consumers(self):
        return self.__consumers

    @consumers.setter
    def consumers(self, val):
        """
        :param val:
        :return: None
        """
        self.__consumers = val
        return

    @property
    def message_queue(self):
        return self.__message_queue

    @message_queue.setter
    def message_queue(self, val):
        """
        :param val:
        :return: None
        """
        self.__message_queue = val
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
    def process_count(self):
        return self.__process_count

    @process_count.setter
    def process_count(self, val):
        """
        :param val:
        :return: None
        """
        self.__process_count = val
        return


class MultiThreadProcessor:
    def __init__(self, props=MultiThreadProcessorProps()):
        self.__props = props

    def __execute_job(self):
        while True:
            time.sleep(randint(0, 3))
            job_path = self.__props.message_queue.get()
            LOGGER.debug(f'processing: {job_path}')
            if job_path == self.__props.end_flag:
                self.__props.message_queue.put(self.__props.end_flag)
                LOGGER.debug(f'no more jobs breaking the loop')
                break
            with self.__props.lock:
                job = self.__props.job_manager.get_job_file(job_path,
                                                            lambda x: self.__props.job_executor.validate_job(x))
            if job is None:
                LOGGER.debug(f'cannot find job. continuing to next job: {job_path}')
                continue
            LOGGER.debug(f'executing job: {job}')
            result = self.__props.job_executor.execute_job(job, self.__props.lock)
            if result is True:
                LOGGER.debug(f'executed job: `{job}` successfully. removing from the processing dir')
                self.__props.job_manager.remove_from_processing(job_path)
            else:
                LOGGER.debug(f'executed job: `{job}` ends in Error. putting back to jobs dir')
                self.__props.job_manager.put_back_failed_job(job_path)
        LOGGER.debug(f'quitting __execute_job')
        return

    def start(self):
        if self.__props.job_executor is None or self.__props.job_manager is None:
            raise RuntimeError('missing job_executor or job_manager')
        LOGGER.info(f'multithread processing starting with process_count: {self.__props.process_count}')
        for i in range(self.__props.process_count):
            p = Process(target=self.__execute_job, args=())
            p.daemon = True
            self.__props.consumers.append(p)
        for c in self.__props.consumers:
            c.start()
            LOGGER.info('starting consumer pid: {}, exit_code: {}'.format(c.pid, c.exitcode))
        for k in self.__props.job_manager.get_all_job_files():
            self.__props.message_queue.put(k)
        LOGGER.debug(f'pushed all job files to queue')
        self.__props.message_queue.put(self.__props.end_flag)
        for c in self.__props.consumers:  # to check if all consumers are done processing it
            LOGGER.info('joining consumers: {}. exit_code: {}'.format(c.pid, c.exitcode))
            c.join()
            LOGGER.debug('joined')
        return

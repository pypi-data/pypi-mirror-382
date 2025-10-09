import threading
import os
import uuid
from rq.worker import RandomWorker
from funboost.core.loggers import get_funboost_file_logger
from redis3 import Redis
from rq import Worker
from funboost.funboost_config_deafult import BrokerConnConfig
from funboost.assist.rq_windows_worker import WindowsWorker


def _install_signal_handlers_monkey(self):
    """ 不能在非主线程中操作信号"""
    pass


Worker._install_signal_handlers = _install_signal_handlers_monkey


class RandomWindowsWorker(RandomWorker, WindowsWorker):
    """ 这个是为了 每个队列都有机会同时拉取，默认是前面的队列先消费完才会消费下一个队列名"""

    pass


class RqHelper:
    redis_conn = Redis.from_url(BrokerConnConfig.REDIS_URL)

    queue_name__rq_job_map = {}
    to_be_start_work_rq_queue_name_set = set()

    @classmethod
    def realy_start_rq_worker(cls, threads_num=50):
        threads = []
        for i in range(threads_num):
            t = threading.Thread(target=cls.__rq_work)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

    @classmethod
    def __rq_work(cls):
        worker_cls = RandomWindowsWorker if os.name == 'nt' else RandomWorker
        worker = worker_cls(queues=list(cls.to_be_start_work_rq_queue_name_set), connection=cls.redis_conn, name=uuid.uuid4().hex)
        worker.work()

    @staticmethod
    def add_nb_log_handler_to_rq():
        get_funboost_file_logger('rq', log_level_int=20,)

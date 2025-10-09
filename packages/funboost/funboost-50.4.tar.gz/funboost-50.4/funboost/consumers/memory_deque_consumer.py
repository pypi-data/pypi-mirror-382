# -*- coding: utf-8 -*-
# @Author  : ydf
# @Time    : 2022/8/8 0008 13:36
import json
from collections import deque

from funboost.constant import BrokerEnum
from funboost.consumers.base_consumer import AbstractConsumer
from funboost.publishers import meomory_deque_publisher


class LocalPythonQueueConsumer(AbstractConsumer):
    """
    python 内置queue对象作为消息队列，这个要求发布和消费必须在同一python解释器内部运行，不支持分布式。
    """

    @property
    def local_python_queue(self) -> deque:
        return meomory_deque_publisher.deque_queue_name__deque_obj_map[self._queue_name]

    def _shedual_task(self):
        while True:
            task = self.local_python_queue.popleft()
            # self.logger.debug(f'从当前python解释器内部的 [{self._queue_name}] 队列中 取出的消息是：  {json.dumps(task)}  ')
            kw = {'body': task}
            self._submit_task(kw)

    def _confirm_consume(self, kw):
        pass

    def _requeue(self, kw):
        self.local_python_queue.append(kw['body'])

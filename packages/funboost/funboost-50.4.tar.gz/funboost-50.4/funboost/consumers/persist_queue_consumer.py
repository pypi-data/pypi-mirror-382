# -*- coding: utf-8 -*-
# @Author  : ydf
# @Time    : 2022/8/8 0008 13:35
import json
from funboost.constant import BrokerEnum
from funboost.consumers.base_consumer import AbstractConsumer
from funboost.publishers.persist_queue_publisher import PersistQueuePublisher
from funboost.core.func_params_model import PublisherParams

class PersistQueueConsumer(AbstractConsumer):
    """
    persist queue包实现的本地持久化消息队列。
    """

    def _shedual_task(self):
        pub = PersistQueuePublisher(publisher_params=PublisherParams(queue_name=self.queue_name))
        while True:
            item = pub.queue.get()
            # self.logger.debug(f'从本地持久化sqlite的 [{self._queue_name}] 队列中 取出的消息是：   {item}  ')
            kw = {'body': item, 'q': pub.queue, 'item': item}
            self._submit_task(kw)

    def _confirm_consume(self, kw):
        kw['q'].ack(kw['item'])

    def _requeue(self, kw):
        kw['q'].nack(kw['item'])

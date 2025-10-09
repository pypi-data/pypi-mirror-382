# -*- coding: utf-8 -*-
# @Author  : ydf
# @Time    : 2022/8/8 0008 13:32
import json
from funboost.constant import BrokerEnum
from funboost.consumers.base_consumer import AbstractConsumer
from funboost.utils.redis_manager import RedisMixin


class RedisPbSubConsumer(AbstractConsumer, RedisMixin):
    """
    redis作为中间件实现的。
    """


    def _shedual_task0000(self):
        pub = self.redis_db_frame.pubsub()
        pub.subscribe(self.queue_name)
        for item in pub.listen():
            if item['type'] == 'message':

                kw = {'body': item['data']}
                self._submit_task(kw)

    def _shedual_task(self):
        pub = self.redis_db_frame.pubsub()
        pub.subscribe(self.queue_name)
        pub.parse_response()
        while True:  # 无限循环
            msg_list = pub.parse_response(timeout=60)  # 得到消息内容
            if msg_list:
                kw = {'body': msg_list[2]}
                self._submit_task(kw)



    def _confirm_consume(self, kw):
        pass

    def _requeue(self, kw):
        pass

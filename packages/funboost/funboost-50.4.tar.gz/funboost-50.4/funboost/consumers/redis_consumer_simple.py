﻿# -*- coding: utf-8 -*-
# @Author  : ydf
# @Time    : 2023/8/8 0008 13:32
import json
from funboost.constant import BrokerEnum
from funboost.consumers.base_consumer import AbstractConsumer
from funboost.core.serialization import Serialization
from funboost.utils.redis_manager import RedisMixin


class RedisConsumer(AbstractConsumer, RedisMixin):
    """
    redis作为中间件实现的。
    """


    def _shedual_task(self):
        while True:
            result = self.redis_db_frame.blpop(self._queue_name,timeout=60)
            if result:
                kw = {'body': result[1]}
                self._submit_task(kw)

    def _confirm_consume(self, kw):
        pass  # redis没有确认消费的功能。

    def _requeue(self, kw):
        self.redis_db_frame.rpush(self._queue_name, Serialization.to_json_str(kw['body']))



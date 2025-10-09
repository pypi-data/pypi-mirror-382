# -*- coding: utf-8 -*-
# @Author  : ydf
# @Time    : 2022/8/8 0008 13:32
import json
# import time
import time



from funboost.constant import BrokerEnum
from funboost.consumers.base_consumer import AbstractConsumer
from funboost.utils.redis_manager import RedisMixin
from funboost.core.serialization import Serialization

class RedisConsumer(AbstractConsumer, RedisMixin):
    """
    redis作为中间件实现的，使用redis list 结构实现的。
    这个如果消费脚本在运行时候随意反复重启或者非正常关闭或者消费宕机，会丢失大批任务。高可靠需要用rabbitmq或者redis_ack_able或者redis_stream的中间件方式。

    这个是复杂版，一次性拉取100个,减少和redis的交互，简单版在 funboost/consumers/redis_consumer_simple.py
    """



    # noinspection DuplicatedCode
    def _shedual_task(self):
        pull_msg_batch_size =  self.consumer_params.broker_exclusive_config['pull_msg_batch_size']
        while True:
            # if False:
            #     pass
            with self.redis_db_frame.pipeline() as p:
                p.lrange(self._queue_name, 0, pull_msg_batch_size- 1)
                p.ltrim(self._queue_name, pull_msg_batch_size, -1)
                task_str_list = p.execute()[0]
            if task_str_list:
                # self.logger.debug(f'从redis的 [{self._queue_name}] 队列中 取出的消息是：  {task_str_list}  ')
                self._print_message_get_from_broker( task_str_list)
                for task_str in task_str_list:
                    kw = {'body': task_str}
                    self._submit_task(kw)
            else:
                result = self.redis_db_frame.brpop(self._queue_name, timeout=60)
                if result:
                    # self.logger.debug(f'从redis的 [{self._queue_name}] 队列中 取出的消息是：  {result[1].decode()}  ')
                    kw = {'body': result[1]}
                    self._submit_task(kw)

    def _shedual_task00(self):
        while True:
            result = self.redis_db_frame.blpop(self._queue_name, timeout=60)
            if result:
                # self.logger.debug(f'从redis的 [{self._queue_name}] 队列中 取出的消息是：  {result[1].decode()}  ')
                kw = {'body': result[1]}
                self._submit_task(kw)

    def _confirm_consume(self, kw):
        pass  # redis没有确认消费的功能。

    def _requeue(self, kw):
        self.redis_db_frame.rpush(self._queue_name,Serialization.to_json_str(kw['body']))

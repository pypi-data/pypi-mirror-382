# -*- coding: utf-8 -*-
# @Author  : ydf
# @Time    : 2021-04-15 0008 12:12
import os

import json

# noinspection PyUnresolvedReferences
from kombu.transport.virtual.base import Channel
from kombu.entity import Exchange, Queue
from kombu.connection import Connection

from funboost.publishers.base_publisher import AbstractPublisher, deco_mq_conn_error
from funboost.funboost_config_deafult import BrokerConnConfig, FunboostCommonConfig

# nb_log.get_logger(name=None,log_level_int=10)
"""
https://www.cnblogs.com/shenh/p/10497244.html

rabbitmq  交换机知识。

https://docs.celeryproject.org/projects/kombu/en/stable/introduction.html
kombu 教程
"""


# noinspection PyMethodMayBeStatic,PyRedundantParentheses
class NoEncode():
    def encode(self, s):
        # return bytes_to_str(base64.b64encode(str_to_bytes(s)))
        return s

    def decode(self, s):
        # return base64.b64decode(str_to_bytes(s))
        return s


Channel.codecs['no_encode'] = NoEncode()  # 不使用base64更分方便查看内容


# noinspection PyAttributeOutsideInit
class KombuPublisher(AbstractPublisher, ):
    """
    使用kombu作为中间件,这个能直接一次性支持很多种小众中间件，但性能很差，除非是分布式函数调度框架没实现的中间件种类用户才可以用这种，用户也可以自己对比性能。
    """

    def custom_init(self):
        self.kombu_url = self.publisher_params.broker_exclusive_config['kombu_url'] or BrokerConnConfig.KOMBU_URL
        self._kombu_broker_url_prefix = self.kombu_url.split(":")[0]
        # logger_name = f'{self._logger_prefix}{self.__class__.__name__}--{self._kombu_broker_url_prefix}--{self._queue_name}'
        # self.logger = get_logger(logger_name, log_level_int=self._log_level_int,
        #                          _log_filename=f'{logger_name}.log' if self._is_add_file_handler else None,
        #                          formatter_template=FunboostCommonConfig.NB_LOG_FORMATER_INDEX_FOR_CONSUMER_AND_PUBLISHER,
        #                          )  #
        if self.kombu_url.startswith('filesystem://'):
            self._create_msg_file_dir()

    def _create_msg_file_dir(self):
        os.makedirs(self.publisher_params.broker_exclusive_config['transport_options']['data_folder_in'], exist_ok=True)
        os.makedirs(self.publisher_params.broker_exclusive_config['transport_options']['data_folder_out'], exist_ok=True)
        processed_folder = self.publisher_params.broker_exclusive_config['transport_options'].get('processed_folder', None)
        if processed_folder:
            os.makedirs(processed_folder, exist_ok=True)

    def init_broker(self):
        self.exchange = Exchange('funboost_exchange', 'direct', durable=True)
        self.queue = Queue(self._queue_name, exchange=self.exchange, routing_key=self._queue_name, auto_delete=False)
        self.conn = Connection(self.kombu_url, transport_options=self.publisher_params.broker_exclusive_config['transport_options'])
        self.queue(self.conn).declare()
        self.producer = self.conn.Producer(serializer='json')
        self.channel = self.producer.channel  # type: Channel
        self.channel.body_encoding = 'no_encode'  # 这里改了编码，存到中间件的参数默认把消息base64了，我觉得没必要不方便查看消息明文。
        # self.channel = self.conn.channel()  # type: Channel
        # # self.channel.exchange_declare(exchange='distributed_framework_exchange', durable=True, type='direct')
        # self.queue = self.channel.queue_declare(queue=self._queue_name, durable=True)
        self.logger.warning(f'使用 kombu 库 连接 {self._kombu_broker_url_prefix} 中间件')

    @deco_mq_conn_error
    def concrete_realization_of_publish(self, msg):
        self.producer.publish(json.loads(msg), exchange=self.exchange, routing_key=self._queue_name, declare=[self.queue])

    @deco_mq_conn_error
    def clear(self):
        self.logger.warning(f'kombu清空消息队列 {self.queue_name}')
        self.channel.queue_purge(self._queue_name)

    @deco_mq_conn_error
    def get_message_count(self):
        # queue = self.channel.queue_declare(queue=self._queue_name, durable=True)
        # return queue.method.message_count
        # self.logger.warning(self.channel._size(self._queue_name))
        queue_declare_ok_t_named_tuple = self.channel.queue_declare(queue=self._queue_name, durable=True, auto_delete=False)
        # print(queue_declare_ok_t_named_tuple)
        return queue_declare_ok_t_named_tuple.message_count
        # if self._kombu_broker_url_prefix == 'amqp' or True:
        #     '''amqp tries to use librabbitmq but falls back to pyamqp.'''
        #     queue_declare_ok_t_named_tuple = self.channel.queue_declare(queue=self._queue_name, durable=True, auto_delete=False)
        #     # queue_declare_ok_t(queue='test_rabbit_queue2', message_count=100000, consumer_count=0)
        #     # print(type(queue_declare_ok_t_named_tuple),queue_declare_ok_t_named_tuple)
        #     return queue_declare_ok_t_named_tuple.message_count
        # # noinspection PyProtectedMember
        # return self.channel._size(self._queue_name)

    def close(self):
        self.channel.close()
        self.conn.close()
        self.logger.warning('关闭 kombu 包 链接')

# -*- coding: utf-8 -*-
# @Author  : ydf
# @Time    : 2022/8/19 0008 12:12
from funboost.core.lazy_impoter import GnsqImporter
from funboost.publishers.base_publisher import AbstractPublisher
from funboost.funboost_config_deafult import BrokerConnConfig


class NsqPublisher(AbstractPublisher, ):
    """
    使用nsq作为中间件
    """

    # noinspection PyAttributeOutsideInit
    def custom_init(self):
        self._nsqd_cleint = GnsqImporter().NsqdHTTPClient(BrokerConnConfig.NSQD_HTTP_CLIENT_HOST, BrokerConnConfig.NSQD_HTTP_CLIENT_PORT)
        self._producer = GnsqImporter().Producer(BrokerConnConfig.NSQD_TCP_ADDRESSES)
        self._producer.start()

    def concrete_realization_of_publish(self, msg):
        # noinspection PyTypeChecker
        self._producer.publish(self._queue_name, msg.encode())

    def clear(self):
        try:
            self._nsqd_cleint.empty_topic(self._queue_name)
        except GnsqImporter().NSQHttpError as e:
            self.logger.exception(e)  # 不能清除一个不存在的topoc会报错，和其他消息队列中间件不同。
        self.logger.warning(f'清除 {self._queue_name} topic中的消息成功')

    def get_message_count(self):
        return -1

    def close(self):
        self._producer.close()

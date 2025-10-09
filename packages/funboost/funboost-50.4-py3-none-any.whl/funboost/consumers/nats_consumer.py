﻿import json
# from pynats import NATSClient, NATSMessage  # noqa

from funboost.consumers.base_consumer import AbstractConsumer
from funboost.core.lazy_impoter import NatsImporter
from funboost.funboost_config_deafult import BrokerConnConfig


class NatsConsumer(AbstractConsumer):
    """
    nats作为中间件实现的。
    """


    def _shedual_task(self):
        # print(88888888888888)
        nats_client = NatsImporter().NATSClient(BrokerConnConfig.NATS_URL, socket_timeout=600, socket_keepalive=True)
        nats_client.connect()

        def callback(msg: NatsImporter().NATSMessage):
            # print(type(msg))
            # print(msg.reply)
            # print(f"Received a message with subject {msg.subject}: {msg.payload}")
            kw = {'body': msg.payload}
            self._submit_task(kw)

        nats_client.subscribe(subject=self.queue_name, callback=callback)
        nats_client.wait()

    def _confirm_consume(self, kw):
        pass   # 没有确认消费

    def _requeue(self, kw):
        self.publisher_of_same_queue.publish(kw['body'])

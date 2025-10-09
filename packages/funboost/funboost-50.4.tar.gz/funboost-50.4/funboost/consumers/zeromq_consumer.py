# -*- coding: utf-8 -*-
# @Author  : ydf
import os
import socket
import json
# import time
# import zmq
import multiprocessing
from funboost.constant import BrokerEnum
from funboost.consumers.base_consumer import AbstractConsumer
from funboost.core.lazy_impoter import ZmqImporter
# from nb_log import get_logger
from funboost.core.loggers import get_funboost_file_logger


# noinspection PyPep8
def check_port_is_used(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # noinspection PyPep8,PyBroadException
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        # 利用shutdown()函数使socket双向数据传输变为单向数据传输。shutdown()需要一个单独的参数，
        # 该参数表示了如何关闭socket。具体为：0表示禁止将来读；1表示禁止将来写；2表示禁止将来读和写。
        return True
    except BaseException:
        return False


logger_zeromq_broker = get_funboost_file_logger('zeromq_broker')


# noinspection PyUnresolvedReferences
def start_broker(port_router: int, port_dealer: int):
    try:
        context = ZmqImporter().zmq.Context()
        # noinspection PyUnresolvedReferences
        frontend = context.socket(ZmqImporter().zmq.ROUTER)
        backend = context.socket(ZmqImporter().zmq.DEALER)
        frontend.bind(f"tcp://*:{port_router}")
        backend.bind(f"tcp://*:{port_dealer}")

        # Initialize poll set
        poller = ZmqImporter().zmq.Poller()
        poller.register(frontend, ZmqImporter().zmq.POLLIN)
        poller.register(backend, ZmqImporter().zmq.POLLIN)
        logger_zeromq_broker.info(f'broker 绑定端口  {port_router}   {port_dealer}  成功')

        # Switch messages between sockets
        # noinspection DuplicatedCode
        while True:
            socks = dict(poller.poll())  # 轮询器 循环接收

            if socks.get(frontend) == ZmqImporter().zmq.POLLIN:
                message = frontend.recv_multipart()
                backend.send_multipart(message)

            if socks.get(backend) == ZmqImporter().zmq.POLLIN:
                message = backend.recv_multipart()
                frontend.send_multipart(message)
    except BaseException as e:
        logger_zeromq_broker.warning(e)


class ZeroMqConsumer(AbstractConsumer):
    """
    zeromq 中间件的消费者，zeromq基于socket代码，不会持久化，且不需要安装软件。
    """



    def custom_init(self):
        self._port = self.consumer_params.broker_exclusive_config['port']
        if self._port is None:
            raise ValueError('please specify port')

    def _start_broker_port(self):
        # threading.Thread(target=self._start_broker).start()
        # noinspection PyBroadException
        try:
            if not (10000 < int(self._port) < 65535):
                raise ValueError("请设置port是一个 10000到65535的之间的一个端口数字")
        except BaseException:
            self.logger.critical(f" 请设置port是一个 10000到65535的之间的一个端口数字")
            # noinspection PyProtectedMember
            os._exit(444)
        if check_port_is_used('127.0.0.1', int(self._port)):
            self.logger.debug(f"""{int(self._port)} router端口已经启动(或占用) """)
            return
        if check_port_is_used('127.0.0.1', int(self._port) + 1):
            self.logger.debug(f"""{int(self._port) + 1} dealer 端口已经启动(或占用) """)
            return
        multiprocessing.Process(target=start_broker, args=(int(self._port), int(self._port) + 1)).start()

    # noinspection DuplicatedCode
    def _shedual_task(self):
        self._start_broker_port()
        context = ZmqImporter().zmq.Context()
        # noinspection PyUnresolvedReferences
        zsocket = context.socket(ZmqImporter().zmq.REP)
        zsocket.connect(f"tcp://localhost:{int(self._port) + 1}")

        while True:
            message = zsocket.recv()
            # self.logger.debug(f""" 从 zeromq 取出的消息是 {message}""")
            self._submit_task({'body': message})
            zsocket.send('recv ok'.encode())

    def _confirm_consume(self, kw):
        pass  #

    def _requeue(self, kw):
        self.publisher_of_same_queue.publish(kw['body'])

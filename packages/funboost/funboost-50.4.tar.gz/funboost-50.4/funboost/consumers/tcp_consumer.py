# -*- coding: utf-8 -*-
# @Author  : ydf
# @Time    : 2022/8/8 0008 13:32
import json
from threading import Thread
import socket
from funboost.constant import BrokerEnum
from funboost.consumers.base_consumer import AbstractConsumer


class TCPConsumer(AbstractConsumer, ):
    """
    socket 实现消息队列，不支持持久化，但不需要安装软件。
    """



    # noinspection PyAttributeOutsideInit
    def custom_init(self):
        # ip__port_str = self.queue_name.split(':')
        # ip_port = (ip__port_str[0], int(ip__port_str[1]))
        # self._ip_port_raw = ip_port
        # self._ip_port = ('', ip_port[1])
        # ip_port = ('', 9999)
        self._ip_port = (self.consumer_params.broker_exclusive_config['host'],
                         self.consumer_params.broker_exclusive_config['port'])
        self.bufsize = self.consumer_params.broker_exclusive_config['bufsize']

    # noinspection DuplicatedCode
    def _shedual_task(self):
      
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # tcp协议
        server.bind(self._ip_port)
        server.listen(128)
        self._server = server
        while True:
            tcp_cli_sock, addr = self._server.accept()
            Thread(target=self.__handle_conn, args=(tcp_cli_sock,)).start()  # 服务端多线程，可以同时处理多个tcp长链接客户端发来的消息。

    def __handle_conn(self, tcp_cli_sock):
        try:
            while True:
                data = tcp_cli_sock.recv(self.bufsize)
                # print('server收到的数据', data)
                if not data:
                    break
                # self._print_message_get_from_broker(f'udp {self._ip_port_raw}', data.decode())
                tcp_cli_sock.send('has_recived'.encode())
                # tcp_cli_sock.close()
                kw = {'body': data}
                self._submit_task(kw)
            tcp_cli_sock.close()
        except ConnectionResetError:
            pass

    def _confirm_consume(self, kw):
        pass  # 没有确认消费的功能。

    def _requeue(self, kw):
        pass

# -*- coding: utf-8 -*-
# @Author  : ydf
# @Time    : 2022/8/8 0008 13:32
import logging
import threading


from flask import Flask, request

from funboost.consumers.base_consumer import AbstractConsumer
from funboost.core.function_result_status_saver import FunctionResultStatus
from funboost.core.msg_result_getter import FutureStatusResult
from funboost.core.serialization import Serialization




class HTTPConsumer(AbstractConsumer, ):
    """
    flask 作为消息队列实现 consumer
    """


    # noinspection PyAttributeOutsideInit
    def custom_init(self):
        # try:
        #     self._ip, self._port = self.queue_name.split(':')
        #     self._port = int(self._port)
        # except BaseException as e:
        #     self.logger.critical(f'http作为消息队列时候,队列名字必须设置为 例如 192.168.1.101:8200  这种,  ip:port')
        #     raise e
        self._ip = self.consumer_params.broker_exclusive_config['host']
        self._port = self.consumer_params.broker_exclusive_config['port']
        if self._port is None:
            raise ValueError('please specify port')

    def _shedual_task(self):
        """
        使用Flask实现HTTP服务器
        相比aiohttp，Flask是同步框架，避免了异步阻塞问题
        """
     

        # 创建Flask应用
        flask_app = Flask(__name__)
        # 关闭Flask的日志，避免干扰funboost的日志
        flask_app.logger.disabled = True
        logging.getLogger('werkzeug').disabled = True
        
        @flask_app.route('/', methods=['GET'])
        def hello():
            """健康检查接口"""
            return "Hello, from funboost (Flask version)"
        
        @flask_app.route('/queue', methods=['POST'])
        def recv_msg():
            """
            接收消息的核心接口
            支持两种调用类型：
            1. publish: 异步发布，立即返回
            2. sync_call: 同步调用，等待结果返回
            """
            try:
                # 获取请求数据
                msg = request.form.get('msg')
                call_type = request.form.get('call_type', 'publish')
                
                if not msg:
                    return {"error": "msg parameter is required"}, 400
                
                # 构造消息数据
                kw = {
                    'body': msg,
                    'call_type': call_type,
                }
                
                if call_type == 'sync_call':
                    # 同步调用：需要等待执行结果
                    future_status_result = FutureStatusResult(call_type=call_type)
                    kw['future_status_result'] = future_status_result
                    
                    # 提交任务到线程池执行
                    self._submit_task(kw)
                    
                    # 等待任务完成（带超时）
                    if future_status_result.wait_finish(self.consumer_params.rpc_timeout):
                        # 返回执行结果
                        result = future_status_result.get_staus_result_obj()
                        return Serialization.to_json_str(
                            result.get_status_dict(without_datetime_obj=True)
                        )
                    else:
                        # 超时处理
                        self.logger.error(f'sync_call wait timeout after {self.consumer_params.rpc_timeout}s')
                        return {"error": "execution timeout"}, 408
                        
                else:
                    # 异步发布：直接提交任务，立即返回
                    self._submit_task(kw)
                    return "finish"
                    
            except Exception as e:
                self.logger.error(f'处理HTTP请求时出错: {e}', exc_info=True)
                return {"error": str(e)}, 500
        
        # 启动Flask服务器
        # 注意：Flask默认是单线程的，但funboost使用线程池处理任务，所以这里threaded=True
        self.logger.info(f'启动Flask HTTP服务器，监听 {self._ip}:{self._port}')

        # flask_app.run(
        #     host='0.0.0.0',  # 监听所有接口
        #     port=self._port,
        #     debug=False,     # 生产环境关闭debug
        #     threaded=True,   # 开启多线程支持
        #     use_reloader=False,  # 关闭自动重载
        # )

        import waitress
        waitress.serve(flask_app, host='0.0.0.0', port=self._port,threads=self.consumer_params.concurrent_num)

    def _frame_custom_record_process_info_func(self, current_function_result_status: FunctionResultStatus, kw: dict):
        """
        任务执行完成后的回调函数
        对于sync_call模式，需要通知等待的HTTP请求
        """
        if kw['call_type'] == "sync_call":
            future_status_result: FutureStatusResult = kw['future_status_result']
            future_status_result.set_staus_result_obj(current_function_result_status)
            future_status_result.set_finish()
            # self.logger.info('sync_call任务执行完成，通知HTTP请求返回结果')

    def _confirm_consume(self, kw):
        """HTTP模式没有确认消费的功能"""
        pass

    def _requeue(self, kw):
        """HTTP模式没有重新入队的功能"""
        pass

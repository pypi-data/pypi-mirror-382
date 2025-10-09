# -*- coding: utf-8 -*-
# @Author  : ydf
# @Time    : 2022/8/8 0008 13:10
"""
任务消费完成后，如果重复发布则过滤。分别实现永久性过滤重复任务和过滤有效期内的重复任务。
任务过滤 = 函数参数过滤 = 字典过滤 = 排序后的键值对json字符串过滤。
"""

import json
import time
from collections import OrderedDict
import typing

from funboost.core.serialization import Serialization
from funboost.utils import  decorators
from funboost.core.loggers import FunboostFileLoggerMixin

from funboost.utils.redis_manager import RedisMixin


class RedisFilter(RedisMixin, FunboostFileLoggerMixin):
    """
    使用set结构，
    基于函数参数的任务过滤。这个是永久性的过滤，除非自己手动删除这个键。
    """

    def __init__(self, redis_key_name, redis_filter_task_expire_seconds):
        """
        :param redis_key_name: 任务过滤键
        :param redis_filter_task_expire_seconds: 任务过滤的过期时间
        """
        self._redis_key_name = redis_key_name
        self._redis_filter_task_expire_seconds = redis_filter_task_expire_seconds

        # @staticmethod
        # def _get_ordered_str(value):
        #     """对json的键值对在redis中进行过滤，需要先把键值对排序，否则过滤会不准确如 {"a":1,"b":2} 和 {"b":2,"a":1}"""
        #     value = Serialization.to_dict(value)
        #     ordered_dict = OrderedDict()
        #     for k in sorted(value):
        #         ordered_dict[k] = value[k]
        #     return json.dumps(ordered_dict)
    
    @staticmethod
    def generate_filter_str(value: typing.Union[str, dict],  filter_str: typing.Optional[str] = None):
        """对json的键值对在redis中进行过滤，需要先把键值对排序，否则过滤会不准确如 {"a":1,"b":2} 和 {"b":2,"a":1}"""
        if filter_str: # 如果用户单独指定了过滤字符串，就使用使用户指定的过滤字符串，否则使用排序后的键值对字符串
            return filter_str
        value = Serialization.to_dict(value)
        ordered_dict = OrderedDict()
        for k in sorted(value):
            ordered_dict[k] = value[k]
        # print(ordered_dict,filter_str)
        return json.dumps(ordered_dict)


    def add_a_value(self, value: typing.Union[str, dict], filter_str: typing.Optional[str] = None):
        self.redis_db_filter_and_rpc_result.sadd(self._redis_key_name, self.generate_filter_str(value, filter_str))

    def manual_delete_a_value(self, value: typing.Union[str, dict], filter_str: typing.Optional[str] = None):
        self.redis_db_filter_and_rpc_result.srem(self._redis_key_name, self.generate_filter_str(value, filter_str))

    def check_value_exists(self, value, filter_str: typing.Optional[str] = None):
        return self.redis_db_filter_and_rpc_result.sismember(self._redis_key_name, self.generate_filter_str(value, filter_str))

    def delete_expire_filter_task_cycle(self):
        pass


class RedisImpermanencyFilter(RedisFilter):
    """
    使用zset结构
    基于函数参数的任务过滤。这个是非永久性的过滤，例如设置过滤过期时间是1800秒 ，30分钟前发布过1 + 2 的任务，现在仍然执行，
    如果是30分钟内发布过这个任务，则不执行1 + 2，现在把这个逻辑集成到框架，一般用于接口缓存。
    """

    def add_a_value(self, value: typing.Union[str, dict], filter_str: typing.Optional[str] = None):
        self.redis_db_filter_and_rpc_result.zadd(self._redis_key_name, {self.generate_filter_str(value, filter_str):time.time()})

    def manual_delete_a_value(self, value: typing.Union[str, dict], filter_str: typing.Optional[str] = None):
        self.redis_db_filter_and_rpc_result.zrem(self._redis_key_name, self.generate_filter_str(value, filter_str))

    def check_value_exists(self, value, filter_str: typing.Optional[str] = None):
        # print(self.redis_db_filter_and_rpc_result.zrank(self._redis_key_name, self.generate_filter_str(value, filter_str)))
        is_exists = False if self.redis_db_filter_and_rpc_result.zscore(self._redis_key_name, self.generate_filter_str(value, filter_str)) is None else True
        # print(is_exists,value,filter_str,self.generate_filter_str(value, filter_str))
        return is_exists   

    @decorators.keep_circulating(60, block=False)
    def delete_expire_filter_task_cycle000(self):
        """
        一直循环删除过期的过滤任务。
        # REMIND 任务过滤过期时间最好不要小于60秒，否则删除会不及时,导致发布的新任务由于命中了任务过滤，而不能触发执行。一般实时价格接口是缓存5分钟或30分钟没有问题。
        :return:
        """
        time_max = time.time() - self._redis_filter_task_expire_seconds
        for value in self.redis_db_filter_and_rpc_result.zrangebyscore(self._redis_key_name, 0, time_max):
            self.logger.info(f'删除 {self._redis_key_name} 键中的过滤任务 {value}')
            self.redis_db_filter_and_rpc_result.zrem(self._redis_key_name, value)

    @decorators.keep_circulating(60, block=False)
    def delete_expire_filter_task_cycle(self):
        """

        一直循环删除过期的过滤任务。任务过滤过期时间最好不要小于60秒，否则删除会不及时,导致发布的新任务不能触发执行。一般实时价格接口是缓存5分钟或30分钟。
        :return:
        """
        time_max = time.time() - self._redis_filter_task_expire_seconds
        delete_num = self.redis_db_filter_and_rpc_result.zremrangebyscore(self._redis_key_name, 0, time_max)
        self.logger.warning(f'从{self._redis_key_name}  键删除 {delete_num} 个过期的过滤任务')
        self.logger.warning(f'{self._redis_key_name}  键中有 {self.redis_db_filter_and_rpc_result.zcard(self._redis_key_name)} 个没有过期的过滤任务')


class RedisImpermanencyFilterUsingRedisKey(RedisFilter):
    """
    直接把任务当做redis的key，使用redis自带的过期机制删除过期的过滤任务。
    基于函数参数的任务过滤。这个是非永久性的过滤，例如设置过滤过期时间是1800秒 ，30分钟前发布过1 + 2 的任务，现在仍然执行，
    如果是30分钟内发布过这个任务，则不执行1 + 2，现在把这个逻辑集成到框架，一般用于接口缓存。
    这种过滤模式键太多了，很难看，固定放到 redis_db_filter_and_rpc_result ，不放到消息队列的db里面。
    """

    def __add_dir_prefix(self, value):
        """
        添加一个前缀，以便redis形成一个树形文件夹，方便批量删除和折叠
        :return:
        """
        return f'{self._redis_key_name}:{value.replace(":", "：")}'  # 任务是json，带有：会形成很多树，换成中文冒号。

    def add_a_value(self, value: typing.Union[str, dict], filter_str: typing.Optional[str] = None):
        redis_key = self.__add_dir_prefix(self.generate_filter_str(value, filter_str))
        self.redis_db_filter_and_rpc_result.set(redis_key, 1)
        self.redis_db_filter_and_rpc_result.expire(redis_key, self._redis_filter_task_expire_seconds)

    def manual_delete_a_value(self, value: typing.Union[str, dict], filter_str: typing.Optional[str] = None):
        self.redis_db_filter_and_rpc_result.delete(self.__add_dir_prefix(self.generate_filter_str(value, filter_str)))

    def check_value_exists(self, value, filter_str: typing.Optional[str] = None):
        return True if self.redis_db_filter_and_rpc_result.exists(self.__add_dir_prefix(self.generate_filter_str(value, filter_str))) else True

    def delete_expire_filter_task_cycle(self):
        """
        redis服务端会自动删除过期的过滤任务键。不用在客户端管理。
        :return:
        """
        pass


if __name__ == '__main__':
    # params_filter = RedisFilter('filter_set:abcdefgh2', 120)
    params_filter = RedisImpermanencyFilter('filter_zset:abcdef2', 120)
    # params_filter = RedisImpermanencyFilterUsingRedisKey('filter_dir', 300)
    for i in range(10):
        # params_filter.add_a_value({'x': i, 'y': i * 2},str(i))
        params_filter.add_a_value({'x': i, 'y': i * 2},None)

    # params_filter.manual_delete_a_value({'a': 1, 'b': 2})
    print(params_filter.check_value_exists({'x': 1, 'y': 2}))
    # params_filter.delete_expire_filter_task_cycle()
    # params_filter.add_a_value({'a': 1, 'b': 5})
    # print(params_filter.check_value_exists({'a': 1, 'b': 2}))
    # time.sleep(130)
    # print(params_filter.check_value_exists({'a': 1, 'b': 2}))

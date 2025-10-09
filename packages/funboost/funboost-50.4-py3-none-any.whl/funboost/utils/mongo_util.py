# -*- coding: utf-8 -*-
# @Author  : ydf
# @Time    : 2022/9/17 0017 15:26
import functools
import os
import pymongo
from pymongo.collection import Collection
from funboost.utils import decorators


@functools.lru_cache()
def _get_mongo_url():
    from funboost.funboost_config_deafult import BrokerConnConfig
    return BrokerConnConfig.MONGO_CONNECT_URL

class MongoMixin0000:
    """
    mixin类被继承，也可以直接实例化。


    这种在 linux运行 + pymongo 版本4.xx  + 多进程子进程中操作会报错。
    /usr/local/lib/python3.8/dist-packages/pymongo/topology.py:172: UserWarning: MongoClient opened before fork. Create MongoClient only after forking.
    See PyMongo's documentation for details: https://pymongo.readthedocs.io/en/stable/faq.html#is-pymongo-fork-safe
    """

    @property
    @decorators.cached_method_result
    def mongo_client(self):
        return pymongo.MongoClient(_get_mongo_url(), connect=False)  # connect等于False原因见注释

    @property
    @decorators.cached_method_result
    def mongo_db_task_status(self):
        return self.mongo_client.get_database('task_status')


class MongoMixin:
    """
    mixin类被继承，也可以直接实例化。

    这个是修改后的，当使用f.multi_process_connsume() + linux +  保存结果到mongo + pymongo.0.2 时候不再报错了。

    在linux上 即使写 connect=False，如果在主进程操作了collection，那么就破坏了 connect=False，在子进程中继续操作这个collection全局变量就会报错。
    设计了多进程+fork 每次都 get_mongo_collection() 是最保险的
    """
    processid__client_map = {}
    processid__db_map = {}
    processid__col_map = {}

    @property
    def mongo_client(self) -> pymongo.MongoClient:
        pid = os.getpid()
        key = pid
        if key not in MongoMixin.processid__client_map:
            MongoMixin.processid__client_map[key] = pymongo.MongoClient(_get_mongo_url(),
                                                                        connect=False, maxIdleTimeMS=60 * 1000, minPoolSize=3, maxPoolSize=20)
        return MongoMixin.processid__client_map[key]

    @property
    def mongo_db_task_status(self):
        pid = os.getpid()
        key = (pid, 'task_status')
        if key not in MongoMixin.processid__db_map:
            MongoMixin.processid__db_map[key] = self.mongo_client.get_database('task_status')
        return MongoMixin.processid__db_map[key]

    def get_mongo_collection(self, database_name, colleciton_name) -> pymongo.collection.Collection:
        pid = os.getpid()
        key = (pid, database_name, colleciton_name)
        if key not in MongoMixin.processid__col_map:
            MongoMixin.processid__col_map[key] = self.mongo_client.get_database(database_name).get_collection(colleciton_name)
        return MongoMixin.processid__col_map[key]


if __name__ == '__main__':
    print(MongoMixin().get_mongo_collection('db2', 'col2'))
    print(MongoMixin().get_mongo_collection('db2', 'col3'))

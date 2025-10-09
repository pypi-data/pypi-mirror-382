# -*- coding: UTF-8 -*-
# @Time : 2023/9/27 16:28 
# @Author : 刘洪波
import redis
import logging
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from pytz import timezone
from minio.error import S3Error
from minio import Minio
from typing import Any, List, Optional
import redis.asyncio as aioredis  # redis-py 4.2+ 提供 asyncio 支持


def mongo_client(host: str, port, user: str = None, password: str = None,
                 tz_aware: bool = False, tzinfo: str = 'Asia/Shanghai'):
    uri = f"mongodb://{host}:{port}"
    if user and password:
        uri = f"mongodb://{user}:{password}@{host}:{port}"
    elif user:
        raise ValueError('Please check user and password')
    elif password:
        raise ValueError('Please check user and password')
    if tz_aware:
        return MongoClient(uri, tz_aware=tz_aware, tzinfo=timezone(tzinfo))
    return MongoClient(uri)


def async_mongo_client(host: str, port, user: str = None, password: str = None,
                       tz_aware: bool = False, tzinfo: str = 'Asia/Shanghai'):
    uri = f"mongodb://{host}:{port}"
    if user and password:
        uri = f"mongodb://{user}:{password}@{host}:{port}"
    elif user:
        raise ValueError('Please check user and password')
    elif password:
        raise ValueError('Please check user and password')
    if tz_aware:
        return AsyncIOMotorClient(uri, tz_aware=tz_aware, tzinfo=timezone(tzinfo))
    return AsyncIOMotorClient(uri)


class MinioClinet(object):
    def __init__(self, minio_endpoint: str, access_key: str, secret_key: str, secure: bool = False,
                 logger: logging.Logger = None):
        """
        Minio客户端
        :param minio_endpoint: 服务器地址
        :param access_key:  访问密钥
        :param secret_key:  秘密密钥
        :param secure: 是否使用 HTTPS，默认False 不使用
        :param logger: 日志收集器
        """
        self.clinet = Minio(
                    endpoint=minio_endpoint,
                    access_key=access_key,
                    secret_key=secret_key,
                    secure=secure
                )

        self.logger = logger or logging.getLogger(__name__)

    def check_bucket(self, bucket_name: str, create: bool=True):
        """
        检查桶状态，也可以用于创建桶， 默认创建
        注：创建桶命名限制：小写字母，句点，连字符和数字是唯一允许使用的字符（使用大写字母、下划线等命名会报错），长度至少应为3个字符
        :param bucket_name: bucket名字
        :param create:  默认为True 创建该bucket
        """
        try:
            # bucket_exists：检查桶是否存在
            if self.clinet.bucket_exists(bucket_name=bucket_name):
                self.logger.info(f"The {bucket_name} bucket already exists.")
            elif create: # 桶不存在时，create为True时创建，为False不创建
                self.clinet.make_bucket(bucket_name)
                self.logger.info(f"The {bucket_name} bucket has been created successfully.")
            return True
        except S3Error as e:
            self.logger.error(e)
        return False

    def get_bucket_list(self):
        buckets_list = []
        try:
            buckets = self.clinet.list_buckets()
            buckets_list = [{'name': bucket.name, 'creation_date': bucket.creation_date} for bucket in buckets]
            self.logger.info(f'buckets_list: {buckets_list}')
        except S3Error as e:
            self.logger.error(e)
        return buckets_list


class RedisClient:
    def __init__(self, host: str, port: int, password: str = None, logger: logging.Logger = None, max_connections: int=10):
        """
        初始化Redis客户端
        :param host: Redis服务器地址
        :param port: Redis服务器端口
        :param password: Redis服务器密码
        :param logger: 日志收集器
        :param max_connections: 最大连接数量，默认为10
        """
        self.pool = redis.ConnectionPool(
            host=host,
            port=port,
            password=password,  # 密码参数
            decode_responses=False,
            max_connections=max_connections  # 连接池容量
        )
        self.conn = redis.Redis(connection_pool=self.pool)
        self.logger = logger or logging.getLogger(__name__)

    def save(self, key: str, value: Any, ex_time: int = None) -> bool:
        """
        保存键值对到Redis（带过期时间）
        :param key: 键名
        :param value: 值
        :param ex_time: 过期时间（秒）
        :return: 操作是否成功
        """
        try:
            return self.conn.set(key, value, ex=ex_time)
        except redis.RedisError as e:
            self.logger.error(f"Redis save error: {e}")
            return False

    def get(self, key: str) -> Optional[str]:
        """
        从Redis获取值
        :param key: 键名
        :return: 值或None
        """
        try:
            return self.conn.get(key)
        except redis.RedisError as e:
            self.logger.error(f"Redis get error: {e}")
            return None

    def push_list(self, list_name: str, *values: Any, right_side: bool = False, ex_time: int = None) -> int:
        """
        向列表添加元素
        :param list_name: 列表名称
        :param values: 要添加的值
        :param right_side: 是否从右侧添加（默认左侧添加）
        :param ex_time: 过期时间（秒）
        :return: 操作后的列表长度
        """
        try:
            if right_side:
                res = self.conn.rpush(list_name, *values)
            else:
                res = self.conn.lpush(list_name, *values)
            if ex_time:
                self.conn.expire(list_name, ex_time)
            return res
        except redis.RedisError as e:
            self.logger.error(f"Redis list push error: {e}")
            return 0

    def get_list(self, list_name: str, start: int = 0, end: int = -1) -> List[str]:
        """
        获取列表范围元素
        :param list_name: 列表名称
        :param start: 起始索引
        :param end: 结束索引
        :return: 元素列表
        """
        try:
            return self.conn.lrange(list_name, start, end)
        except redis.RedisError as e:
            self.logger.error(f"Redis list range error: {e}")
            return []

    def get_list_item(self, list_name: str, index: int) -> Optional[str]:
        """
        获取列表指定位置的元素
        :param list_name: 列表名称
        :param index: 元素索引
        :return: 元素值或None
        """
        try:
            return self.conn.lindex(list_name, index)
        except redis.RedisError as e:
            self.logger.error(f"Redis list index error: {e}")
            return None

    def list_length(self, list_name: str) -> int:
        """
        获取列表长度
        :param list_name: 列表名称
        :return: 列表长度
        """
        try:
            return self.conn.llen(list_name)
        except redis.RedisError as e:
            self.logger.error(f"Redis list length error: {e}")
            return 0

    def delete_key(self, key: str) -> int:
        """
        删除指定的键（包括列表）
        :param key: 键名
        :return: 删除的键数量 (1=成功, 0=键不存在)
        """
        try:
            return self.conn.delete(key)
        except redis.RedisError as e:
            self.logger.error(f"Redis delete key error: {e}")
            return 0

    def pop_list(self, list_name: str, right_side: bool = False) -> Optional[str]:
        """
        从列表中弹出元素（移除并返回）
        :param list_name: 列表名称
        :param right_side: 是否从右侧弹出（默认左侧弹出）
        :return: 弹出的元素值或None（列表为空时）
        """
        try:
            if right_side:
                return self.conn.rpop(list_name)
            return self.conn.lpop(list_name)
        except redis.RedisError as e:
            self.logger.error(f"Redis list pop error: {e}")
            return None

    def remove_list_value(self, list_name: str, value: str, count: int = 0) -> int:
        """
        从列表中移除指定值的元素
        :param list_name: 列表名称
        :param value: 要移除的值
        :param count: 移除数量控制:
            count > 0 : 从头到尾移除最多count个匹配元素
            count < 0 : 从尾到头移除最多count个匹配元素
            count = 0 : 移除所有匹配元素
        :return: 实际移除的元素数量
        """
        try:
            return self.conn.lrem(list_name, count, value)
        except redis.RedisError as e:
            self.logger.error(f"Redis list remove error: {e}")
            return 0

    def trim_list(self, list_name: str, start: int, end: int) -> bool:
        """
        修剪列表，只保留指定范围内的元素
        :param list_name: 列表名称
        :param start: 起始索引
        :param end: 结束索引
        :return: 操作是否成功
        """
        try:
            self.conn.ltrim(list_name, start, end)
            return True
        except redis.RedisError as e:
            self.logger.error(f"Redis list trim error: {e}")
            return False

    def close(self) -> None:
        """关闭连接池"""
        self.pool.disconnect()

    # ---------------- 上下文管理器支持 ----------------
    def __enter__(self):
        """进入上下文时返回自身"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时自动关闭连接"""
        self.close()


class AsyncRedisClient:
    def __init__(self, host: str, port: int, password: str = None, logger: logging.Logger = None, max_connections: int=10):
        """
        初始化异步 Redis 客户端
        :param host: Redis服务器地址
        :param port: Redis服务器端口
        :param password: 密码
        :param logger: 日志收集器
        :param max_connections: 最大连接数量，默认为10
        """
        self.pool = aioredis.ConnectionPool(
            host=host,
            port=port,
            password=password,
            decode_responses=False,
            max_connections=max_connections
        )
        self.conn = aioredis.Redis(connection_pool=self.pool)
        self.logger = logger or logging.getLogger(__name__)

    async def save(self, key: str, value: Any, ex_time: int = None) -> bool:
        """保存键值对到Redis"""
        try:
            return await self.conn.set(key, value, ex=ex_time)
        except aioredis.RedisError as e:
            self.logger.error(f"Redis save error: {e}")
            return False

    async def get(self, key: str) -> Optional[str]:
        """获取键值"""
        try:
            return await self.conn.get(key)
        except aioredis.RedisError as e:
            self.logger.error(f"Redis get error: {e}")
            return None

    async def push_list(self, list_name: str, *values: Any, right_side: bool = False, ex_time: int = None) -> int:
        """向列表添加元素"""
        try:
            if right_side:
                res = await self.conn.rpush(list_name, *values)
            else:
                res = await self.conn.lpush(list_name, *values)
            if ex_time:
                await self.conn.expire(list_name, ex_time)
            return res
        except aioredis.RedisError as e:
            self.logger.error(f"Redis list push error: {e}")
            return 0

    async def get_list(self, list_name: str, start: int = 0, end: int = -1) -> List[str]:
        """获取列表范围元素"""
        try:
            return await self.conn.lrange(list_name, start, end)
        except aioredis.RedisError as e:
            self.logger.error(f"Redis list range error: {e}")
            return []

    async def get_list_item(self, list_name: str, index: int) -> Optional[str]:
        """获取列表指定索引元素"""
        try:
            return await self.conn.lindex(list_name, index)
        except aioredis.RedisError as e:
            self.logger.error(f"Redis list index error: {e}")
            return None

    async def list_length(self, list_name: str) -> int:
        """获取列表长度"""
        try:
            return await self.conn.llen(list_name)
        except aioredis.RedisError as e:
            self.logger.error(f"Redis list length error: {e}")
            return 0

    async def delete_key(self, key: str) -> int:
        """删除键"""
        try:
            return await self.conn.delete(key)
        except aioredis.RedisError as e:
            self.logger.error(f"Redis delete key error: {e}")
            return 0

    async def pop_list(self, list_name: str, right_side: bool = False) -> Optional[str]:
        """弹出列表元素"""
        try:
            if right_side:
                return await self.conn.rpop(list_name)
            return await self.conn.lpop(list_name)
        except aioredis.RedisError as e:
            self.logger.error(f"Redis list pop error: {e}")
            return None

    async def remove_list_value(self, list_name: str, value: str, count: int = 0) -> int:
        """移除列表中指定值"""
        try:
            return await self.conn.lrem(list_name, count, value)
        except aioredis.RedisError as e:
            self.logger.error(f"Redis list remove error: {e}")
            return 0

    async def trim_list(self, list_name: str, start: int, end: int) -> bool:
        """修剪列表"""
        try:
            await self.conn.ltrim(list_name, start, end)
            return True
        except aioredis.RedisError as e:
            self.logger.error(f"Redis list trim error: {e}")
            return False

    async def close(self) -> None:
        """关闭连接池"""
        await self.pool.disconnect()

    # ---------------- 异步上下文管理器 ----------------
    async def __aenter__(self):
        """进入上下文时返回自身"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时自动关闭连接池"""
        await self.close()
"""Databases tools"""

from typing import *

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError
from pymongo.results import InsertOneResult, InsertManyResult

from loguru import logger


def create_collection(db: Database, collection: str, keys: Optional[List[Tuple[str, int]]]=None, index: Optional[Any] = None) -> Collection:
    """创建集合
    
    :param db: mongo的db对象
    :param collection: 集合名称
    :param keys: 主键索引，支持联合主键，格式（列表元组或列表列表均可）：[["id", 1], ["user.id", 1], ["created_at", 1]]
    :parma index: 索引，可以是单个字符，也可以是列表，目前只支持单个索引创建
    """
    if collection not in db.list_collection_names():
        coll = db.create_collection(collection)
        coll.create_index(keys, unique=True)
        coll.create_index(index)
    else:
        coll = db.get_collection(collection)
    return coll


def set_results(collection: Collection, datas: List[Dict], if_exists='ignore') -> int:
    """插入数据

    :param collection:
    :param datas:
    :param if_exists: 重复处理，包括：'ignore' 'replace' 
    :return:
    """
    if not isinstance(datas, (list, tuple, set)):
        datas = [datas]

    add_count = 0
    for data in datas:
        try:
            insert_res = collection.insert_one(data)
            _id = insert_res.inserted_id
        except DuplicateKeyError as e:
            if if_exists == 'ignore':
                continue
            else:
                # 解析错误信息以获取重复的键值
                error_details = e.details
                logger.debug(f"捕获到重复键错误: {error_details}")
                if 'keyValue' in error_details:
                    # 获取重复的键值
                    duplicate_key_value = error_details['keyValue']
                    # print(duplicate_key_value, data)
                    duplicate_key_value.pop("_id", None)
                    data.pop('_id', None)
                    logger.debug(f"重复的键值: {duplicate_key_value}")

                    # 使用获取到的键值进行更新操作
                    update_result = collection.update_one(
                        duplicate_key_value,
                        {'$set': data},
                        upsert=True
                    )
                    if update_result.upserted_id:
                        logger.debug(f"文档不存在，已插入，文档ID: {update_result.upserted_id}")
                    else:
                        logger.debug(f"文档已存在，已更新")
        add_count += 1
    return add_count

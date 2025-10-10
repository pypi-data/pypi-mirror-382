#!/usr/bin/env python3
# coding = utf8
"""
@ Author : ZeroSeeker
@ e-mail : zeroseeker@foxmail.com
@ GitHub : https://github.com/ZeroSeeker
@ Gitee : https://gitee.com/ZeroSeeker
"""
import copy

from .basics import Basics
from .basics import convert_decimals
import showlog
import time
import envx
default_silence = False
default_env_file_name = 'mongo.env'


def make_con_info(
        env_file_name: str = default_env_file_name
):
    # ---------------- 固定设置 ----------------
    inner_env = envx.read(file_name=env_file_name)
    connect_str = inner_env.get('connect_str')
    if connect_str is None:
        host = inner_env.get('host', 'localhost')
        port = int(inner_env.get('port', '27017'))
        username = inner_env.get('username')
        password = inner_env.get('password')
        if username or password:
            # 填写了账号密码，走验证
            connect_str = f'mongodb://{username}:{password}@{host}:{port}/'
        else:
            # 未填写账号密码不走验证
            connect_str = f'mongodb://{host}:{port}/'
    else:
        pass
    return connect_str
    # ---------------- 固定设置 ----------------


def safe_get_records(
        query: dict = None,
        db: str = None,
        collection: str = None,
        connect_str: str = None,  # 若指定，将优先使用
        env_file_name: str = default_env_file_name,
        silence: bool = default_silence
):
    # ---------------- 固定设置 ----------------
    if connect_str is None:
        connect_str = make_con_info(env_file_name=env_file_name)
    # ---------------- 固定设置 ----------------
    while True:
        try:
            mongo_basics = Basics(
                connect_str=connect_str,
                db=db,
                collection=collection,
                silence=silence,
            )
            response = mongo_basics.collection_records(
                query=query,
                db=db,
                collection=collection
            )
            return response
        except ConnectionError:
            if silence is False:
                showlog.warning('连接失败，将重试...')
            time.sleep(1)
        except Exception as ex:
            if silence is False:
                showlog.error('未知错误')
            time.sleep(1)


def safe_find(
        db: str = None,
        collection: str = None,
        query: dict = None,
        show_setting: dict = None,
        sort_setting: list = None,
        limit_num: int = None,
        skip_num: int = None,
        connect_str: str = None,
        env_file_name: str = default_env_file_name,
        silence: bool = default_silence,
        show_id: bool = True,
        distinct_by: str = None
):
    """
    查询
    :param db:
    :param collection:
    :param query:
    :param show_setting:
    :param sort_setting: 排序设置，例如[('_id', -1)]，其中的数字可设置为-1/1，-1为降序，1为升序
    :param limit_num:
    :param skip_num:
    :param connect_str: 若指定，将优先使用
    :param env_file_name:
    :param silence:
    :param show_id: 是否返回id
    :param distinct_by: 取某字段的唯一值
    """
    # ---------------- 固定设置 ----------------
    if connect_str is None:
        connect_str = make_con_info(
            env_file_name=env_file_name
        )
    # ---------------- 固定设置 ----------------
    if not show_setting and show_id is False:
        show_setting = {"_id": 0}
    elif show_setting and show_id is False:
        show_setting["_id"] = 0

    while True:
        try:
            mongo_basics = Basics(
                connect_str=connect_str,
                db=db,
                collection=collection,
                silence=silence,
            )
            response, response_count = mongo_basics.find(
                query=query,
                db=db,
                collection=collection,
                show_setting=show_setting,
                sort_setting=sort_setting,
                limit_num=limit_num,
                skip_num=skip_num,
                distinct_by=distinct_by
            )
            return response
        except ConnectionError:
            if silence is False:
                showlog.warning('连接失败，将重试...')
            time.sleep(1)
        except Exception as ex:
            if silence is False:
                showlog.error('未知错误')
            time.sleep(1)


def safe_find_distinct(
        by: str,
        db: str = None,
        collection: str = None,

        connect_str: str = None,
        env_file_name: str = default_env_file_name,
        silence: bool = default_silence,
):
    """
    查询字段的唯一值
    :param by:
    :param db:
    :param collection:
    :param connect_str: 若指定，将优先使用
    :param env_file_name:
    :param silence:
    """
    # ---------------- 固定设置 ----------------
    if connect_str is None:
        connect_str = make_con_info(
            env_file_name=env_file_name
        )
    # ---------------- 固定设置 ----------------

    while True:
        try:
            mongo_basics = Basics(
                connect_str=connect_str,
                db=db,
                collection=collection,
                silence=silence,
            )
            response = mongo_basics.distinct(
                by=by,
                db=db,
                collection=collection
            )
            return response
        except ConnectionError:
            if silence is False:
                showlog.warning('连接失败，将重试...')
            time.sleep(1)
        except Exception as ex:
            if silence is False:
                showlog.error('未知错误')
            time.sleep(1)


def safe_find_page(
        db: str = None,
        collection: str = None,
        query: dict = None,
        previous_tag: str = None,
        previous_value: str = None,
        where_str: str = '$gt',
        show_setting: dict = None,
        sort_setting: list = None,
        limit_num: int = 10,
        connect_str: str = None,
        env_file_name: str = default_env_file_name,
        silence: bool = default_silence,
        show_id: bool = True
):
    """
    分页查询
    :param db:
    :param collection:
    :param query:
    :param previous_tag:
    :param previous_value:
    :param where_str:
    :param show_setting:
    :param sort_setting: 排序设置，例如[('_id', -1)]，其中的数字可设置为-1/1，-1为降序，1为升序
    :param limit_num:
    :param connect_str: 若指定，将优先使用
    :param env_file_name:
    :param silence:
    :param show_id: 是否返回id
    """
    # ---------------- 固定设置 ----------------
    if connect_str is None:
        connect_str = make_con_info(env_file_name=env_file_name)
    # ---------------- 固定设置 ----------------
    if not show_setting and show_id is False:
        show_setting = {"_id": 0}
    elif show_setting and show_id is False:
        show_setting["_id"] = 0

    while True:
        try:
            mongo_basics = Basics(
                connect_str=connect_str,
                db=db,
                collection=collection,
                silence=silence,
            )
            response, response_count = mongo_basics.find_page(
                db=db,
                collection=collection,
                query=query,
                previous_tag=previous_tag,
                previous_value=previous_value,
                where_str=where_str,
                show_setting=show_setting,
                sort_setting=sort_setting,
                limit_num=limit_num
            )
            return response
        except ConnectionError:
            if silence is False:
                showlog.warning('连接失败，将重试...')
            time.sleep(1)
        except Exception as ex:
            if silence is False:
                showlog.error('未知错误')
            time.sleep(1)


def safe_find_page_by_num(
        db: str = None,
        collection: str = None,
        query: dict = None,
        show_setting: dict = None,
        sort_setting: list = None,
        previous_tag: str = None,
        page_size: int = 20,
        page: int = 1,
        _id: str = None,
        connect_str: str = None,
        env_file_name: str = default_env_file_name,
        silence: bool = default_silence,
        show_id: bool = True
):
    """
    分页查询，按页码查询
    :param db:
    :param collection:
    :param query:
    :param show_setting:
    :param sort_setting: 排序设置，例如[('_id', -1)]，其中的数字可设置为-1/1，-1为降序，1为升序
    :param previous_tag:
    :param page_size:
    :param page:
    :param _id:
    :param connect_str: 若指定，将优先使用
    :param env_file_name:
    :param silence:
    :param show_id: 是否返回id
    """
    # ---------------- 固定设置 ----------------
    if connect_str is None:
        connect_str = make_con_info(env_file_name=env_file_name)
    # ---------------- 固定设置 ----------------
    if not show_setting and show_id is False:
        show_setting = {"_id": 0}
    elif show_setting and show_id is False:
        show_setting["_id"] = 0

    while True:
        try:
            mongo_basics = Basics(
                connect_str=connect_str,
                db=db,
                collection=collection,
                silence=silence,
            )
            response, response_count = mongo_basics.get_page_data(
                db=db,
                collection=collection,
                query=query,
                show_setting=show_setting,
                sort_setting=sort_setting,
                previous_tag=previous_tag,
                page_size=page_size,
                page=page,
                _id=_id
            )
            return response, response_count
        except ConnectionError:
            if silence is False:
                showlog.warning('连接失败，将重试...')
            time.sleep(1)
        except Exception as ex:
            if silence is False:
                showlog.error('未知错误')
            time.sleep(1)


def safe_aggregate(
        db: str = None,
        collection: str = None,
        query: list = None,
        connect_str: str = None,
        env_file_name: str = default_env_file_name,
        silence: bool = default_silence
):
    """
    聚合查询
    :param db:
    :param collection:
    :param query:
    :param connect_str: 若指定，将优先使用
    :param env_file_name:
    :param silence:
    """
    # ---------------- 固定设置 ----------------
    if connect_str is None:
        connect_str = make_con_info(
            env_file_name=env_file_name
        )
    # ---------------- 固定设置 ----------------
    while True:
        try:
            mongo_basics = Basics(
                connect_str=connect_str,
                db=db,
                collection=collection,
                silence=silence,
            )
            response = mongo_basics.aggregate(
                query=query,
                db=db,
                collection=collection
            )
            return response
        except ConnectionError:
            if silence is False:
                showlog.warning('连接失败，将重试...')
            time.sleep(1)
        except Exception as ex:
            if silence is False:
                showlog.error('未知错误')
            time.sleep(1)


def safe_insert(
        values: list,
        db: str = None,
        collection: str = None,
        connect_str: str = None,  # 若指定，将优先使用
        env_file_name: str = default_env_file_name,
        silence: bool = default_silence,
        index_list: list = None
):
    # ---------------- 固定设置 ----------------
    if connect_str is None:
        connect_str = make_con_info(env_file_name=env_file_name)
    # ---------------- 固定设置 ----------------
    while True:
        try:
            mongo_basics = Basics(
                connect_str=connect_str,
                db=db,
                collection=collection,
                silence=silence,
            )
            response = mongo_basics.insert(
                values=convert_decimals(copy.deepcopy(values)),
                db=db,
                collection=collection,
                index_list=index_list
            )
            return response
        except ConnectionError:
            if silence is False:
                showlog.warning('连接失败，将重试...')
            time.sleep(1)
        except Exception as ex:
            if silence is False:
                showlog.error('未知错误')
            time.sleep(1)


def safe_upsert(
        values: list,
        db: str = None,
        collection: str = None,
        query_keys: list = None,
        connect_str: str = None,  # 若指定，将优先使用
        env_file_name: str = default_env_file_name,
        silence: bool = default_silence,
        index_list: list = None
):
    # ---------------- 固定设置 ----------------
    if connect_str is None:
        connect_str = make_con_info(env_file_name=env_file_name)
    # ---------------- 固定设置 ----------------
    if index_list:
        index_list_new = copy.deepcopy(index_list)
    else:
        index_list_new = list()

    if query_keys:
        index_list_new.extend(query_keys)

    while True:
        try:
            mongo_basics = Basics(
                connect_str=connect_str,
                db=db,
                collection=collection,
                silence=silence,
            )
            response = mongo_basics.upsert(
                values=convert_decimals(copy.deepcopy(values)),
                db=db,
                collection=collection,
                query_keys=query_keys,
                index_list=index_list_new
            )
            return response
        except ConnectionError:
            if silence is False:
                showlog.warning('连接失败，将重试...')
            time.sleep(1)
        except Exception as ex:
            if silence is False:
                showlog.error('未知错误')
            time.sleep(1)


def safe_delete_one(
        db: str = None,
        collection: str = None,
        query: dict = None,
        connect_str: str = None,  # 若指定，将优先使用
        env_file_name: str = default_env_file_name,
        silence: bool = default_silence
):
    """
    删除一条数据
    """
    # ---------------- 固定设置 ----------------
    if connect_str is None:
        connect_str = make_con_info(env_file_name=env_file_name)
    # ---------------- 固定设置 ----------------
    while True:
        try:
            mongo_basics = Basics(
                connect_str=connect_str,
                db=db,
                collection=collection,
                silence=silence,
            )
            response = mongo_basics.delete_one(
                db=db,
                collection=collection,
                query=query
            )
            return response
        except ConnectionError:
            if silence is False:
                showlog.warning('连接失败，将重试...')
            time.sleep(1)
        except Exception as ex:
            if silence is False:
                showlog.error('未知错误')
            time.sleep(1)


def safe_delete_many(
        db: str = None,
        collection: str = None,
        query: dict = None,
        connect_str: str = None,  # 若指定，将优先使用
        env_file_name: str = default_env_file_name,
        silence: bool = default_silence
):
    """
    删除满足条件的所有数据
    """
    # ---------------- 固定设置 ----------------
    if connect_str is None:
        connect_str = make_con_info(env_file_name=env_file_name)
    # ---------------- 固定设置 ----------------
    while True:
        try:
            mongo_basics = Basics(
                connect_str=connect_str,
                db=db,
                collection=collection,
                silence=silence,
            )
            response = mongo_basics.delete_many(
                db=db,
                collection=collection,
                query=query
            )
            return response
        except ConnectionError:
            if silence is False:
                showlog.warning('连接失败，将重试...')
            time.sleep(1)
        except Exception as ex:
            if silence is False:
                showlog.error('未知错误')
            time.sleep(1)


def collections(
        db: str = None,
        connect_str: str = None,  # 若指定，将优先使用
        env_file_name: str = default_env_file_name,
        silence: bool = default_silence
):
    """
    获取所有的集合名
    """
    # ---------------- 固定设置 ----------------
    if connect_str is None:
        connect_str = make_con_info(env_file_name=env_file_name)
    # ---------------- 固定设置 ----------------
    while True:
        try:
            mongo_basics = Basics(
                connect_str=connect_str,
                db=db,
                silence=silence,
            )
            return mongo_basics.collections(
                db=db,
            )
        except ConnectionError:
            if silence is False:
                showlog.warning('连接失败，将重试...')
            time.sleep(1)
        except Exception as ex:
            if silence is False:
                showlog.error('未知错误')
            time.sleep(1)


def drop_collection(
        db: str,
        collection: str,
        connect_str: str = None,  # 若指定，将优先使用
        env_file_name: str = default_env_file_name,
        silence: bool = default_silence
):
    """
    删除集合
    """
    # ---------------- 固定设置 ----------------
    if connect_str is None:
        connect_str = make_con_info(env_file_name=env_file_name)
    # ---------------- 固定设置 ----------------
    while True:
        try:
            mongo_basics = Basics(
                connect_str=connect_str,
                db=db,
                silence=silence,
            )
            return mongo_basics.drop_collection(
                db=db,
                collection=collection,
            )
        except ConnectionError:
            if silence is False:
                showlog.warning('连接失败，将重试...')
            time.sleep(1)
        except Exception as ex:
            if silence is False:
                showlog.error('未知错误')
            time.sleep(1)

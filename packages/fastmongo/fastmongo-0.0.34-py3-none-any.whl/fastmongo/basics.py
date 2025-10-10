#!/usr/bin/env python3
# coding = utf8
"""
@ Author : ZeroSeeker
@ e-mail : zeroseeker@foxmail.com
@ GitHub : https://github.com/ZeroSeeker
@ Gitee : https://gitee.com/ZeroSeeker
"""
from bson.objectid import ObjectId
from pymongo import UpdateOne
from pymongo import ASCENDING
from pymongo import DESCENDING
import pymongo
import showlog
import copy
import time


def convert_decimals(obj):
    """
    mongo不支持decimal,但是支持Decimal128，这里将数据提前转换
    """
    from bson import Decimal128
    from decimal import Decimal
    if isinstance(obj, Decimal):
        return Decimal128(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(v) for v in obj]
    return obj


class Basics:
    """
    这是一个封装了mongodb基础方法的类，方便快捷使用
    """
    def __init__(
            self,
            connect_str: str,
            db: str = None,
            collection: str = None,
            silence: bool = False
    ):
        self.db = db
        self.collection = collection
        self.client = pymongo.MongoClient(connect_str)
        self.silence = silence

    def create_collection_with_index(
            self,
            db: str,
            collection: str,
            index_list: list
    ):
        my_db = self.client[db]
        if collection not in my_db.list_collection_names():
            # 如果集合不存在
            my_db.create_collection(collection)  # 创建空集合（显式创建）
        else:
            # 集合存在
            pass
        my_collection = my_db[collection]

        if index_list:
            # 存在指定索引
            existing_indexes = my_collection.index_information()  # 获取所有现有索引的信息
            for each_index in index_list:
                # 目标索引的键和方向
                target_key = [(each_index, ASCENDING)]  # 创建升序索引
                index_exists = any(
                    info["key"] == target_key  # 比较键和方向
                    for info in existing_indexes.values()
                )
                if not index_exists:
                    # 需要创建的索引不存在
                    my_collection.create_index(target_key)  # 创建单字段索引
                    if not self.silence:
                        showlog.info(f"索引[{target_key}]创建成功")
                else:
                    pass
                    # 需要创建的索引已存在
                    # if not self.silence:
                    #     showlog.info(f"索引[{target_key}]已存在，无需重复创建")
        else:
            # 不存在制定索引
            pass


    def insert(
            self,
            values: list,
            db: str = None,
            collection: str = None,
            index_list: list = None
    ) -> object:
        # 增，values 为一个list
        if len(values) == 0:
            return
        else:
            pass

        if db is None:
            query_db = self.db
        else:
            query_db = db
        if collection is None:
            query_collection = self.collection
        else:
            query_collection = collection
        my_db = self.client[query_db]
        self.create_collection_with_index(
            db=query_db,
            collection=query_collection,
            index_list=index_list
        )
        # if query_collection not in my_db.list_collection_names():
        #     # 如果集合不存在
        #     my_db.create_collection(query_collection)  # 创建空集合（显式创建）
        # else:
        #     pass
        my_collection = my_db[query_collection]
        #
        # if index_list:
        #     for each_index in index_list:
        #         # 创建单字段索引
        #         my_collection.create_index([(each_index, ASCENDING)])
        # else:
        #     pass
        if len(values) == 1:
            return my_collection.insert_one(values[0])
        else:
            return my_collection.insert_many(values)

    def update(
            self,
            values: list,
            db: str = None,
            collection: str = None,
            query: dict = None,
            index_list: list = None
    ) -> object:
        # 改（单个）
        if len(values) == 0:
            return
        else:
            pass

        if db is None:
            query_db = self.db
        else:
            query_db = db
        if collection is None:
            query_collection = self.collection
        else:
            query_collection = collection
        while True:
            try:
                my_db = self.client[query_db]
                break
            except:
                if self.silence is False:
                    showlog.warning('连接错误，正在重连...')
                time.sleep(1)
        self.create_collection_with_index(
            db=query_db,
            collection=query_collection,
            index_list=index_list
        )
        # if query_collection not in my_db.list_collection_names():
        #     # 如果集合不存在
        #     my_db.create_collection(query_collection)  # 创建空集合（显式创建）
        # else:
        #     pass
        my_collection = my_db[query_collection]
        # if index_list:
        #     for each_index in index_list:
        #         # 创建单字段索引
        #         my_collection.create_index([(each_index, ASCENDING)])
        # else:
        #     pass
        set_values = {"$set": values[0]}
        return my_collection.update(query, set_values, True)

    def upsert(
            self,
            values: list,  # [{'value': 1}, {'value': 2}]
            db: str = None,
            collection: str = None,
            query_keys: list = None,  # ['value']
            index_list: list = None
    ) -> object:
        # 改（批量）
        """
        这是针对多条数据的批量插入/更新方法
        主键在query_keys参数设定，作为主键名列表，将会根据设定的主键规则去执行
        """
        if len(values) == 0:
            return
        else:
            pass

        if query_keys is None:
            query_keys = []

        if db is None:
            query_db = self.db
        else:
            query_db = db
        if collection is None:
            query_collection = self.collection
        else:
            query_collection = collection
        while True:
            try:
                my_db = self.client[query_db]
                break
            except:
                if self.silence is False:
                    showlog.warning('连接错误，正在重连...')
                time.sleep(1)
        self.create_collection_with_index(
            db=query_db,
            collection=query_collection,
            index_list=index_list
        )
        my_collection = my_db[query_collection]
        arr = list()  # 初始化一个空列表
        for line in values:
            query_dict = dict()

            if "_id" in line.keys() and "_id" not in query_keys:
                query_keys.append("_id")

            if not query_keys:
                pass
            else:
                for query_key in query_keys:
                    query_data = line.get(query_key)
                    if query_data is not None:
                        query_dict[query_key] = query_data
                    else:
                        continue
            one = UpdateOne(
                filter=copy.deepcopy(query_dict),
                update={"$set": copy.deepcopy(line)},
                upsert=True
            )
            arr.append(one)
        return my_collection.bulk_write(arr)

    def update_many(
            self,
            values: list,
            db: str = None,
            collection: str = None,
            query: dict = None,
            index_list: list = None
    ) -> object:
        # 改（批量）
        if len(values) == 0:
            return
        else:
            pass

        if db is None:
            query_db = self.db
        else:
            query_db = db
        if collection is None:
            query_collection = self.collection
        else:
            query_collection = collection
        my_db = self.client[query_db]
        self.create_collection_with_index(
            db=query_db,
            collection=query_collection,
            index_list=index_list
        )
        # if query_collection not in my_db.list_collection_names():
        #     # 如果集合不存在
        #     my_db.create_collection(query_collection)  # 创建空集合（显式创建）
        # else:
        #     pass
        my_collection = my_db[query_collection]
        # if index_list:
        #     for each_index in index_list:
        #         # 创建单字段索引
        #         my_collection.create_index([(each_index, ASCENDING)])
        # else:
        #     pass
        set_values = {"$set": values[0]}
        return my_collection.update_many(query, set_values, True)

    def delete_key(
            self,
            key_name: str,
            db: str = None,
            collection: str = None,
            query: dict = None
    ) -> object:
        # 改-删除
        if db is None:
            query_db = self.db
        else:
            query_db = db
        if collection is None:
            query_collection = self.collection
        else:
            query_collection = collection
        my_db = self.client[query_db]
        my_collection = my_db[query_collection]
        set_values = {"$unset": {key_name: None}}
        return my_collection.update(query, set_values, True)

    def delete_one(
            self,
            db: str = None,
            collection: str = None,
            query: dict = None
    ) -> object:
        # 删，只删1条
        if db is None:
            query_db = self.db
        else:
            query_db = db
        if collection is None:
            query_collection = self.collection
        else:
            query_collection = collection
        if query is None:
            return
        else:
            my_db = self.client[query_db]
            my_collection = my_db[query_collection]
            return my_collection.delete_one(query)

    def delete_many(
            self,
            db: str = None,
            collection: str = None,
            query: dict = None
    ) -> object:
        # 删，删除所有满足条件的记录
        if db is None:
            query_db = self.db
        else:
            query_db = db
        if collection is None:
            query_collection = self.collection
        else:
            query_collection = collection
        if query is None:
            return
        else:
            my_db = self.client[query_db]
            my_collection = my_db[query_collection]
            return my_collection.delete_many(query)

    def insert_or_update(
            self,
            values: list,
            db: str = None,
            collection: str = None,
            query: dict = None,
            index_list: list = None
    ) -> object:
        # 改，当前只支持单条数据操作
        if len(values) == 0:
            return
        else:
            pass

        if db is None:
            query_db = self.db
        else:
            query_db = db
        if collection is None:
            query_collection = self.collection
        else:
            query_collection = collection
        my_db = self.client[query_db]
        self.create_collection_with_index(
            db=query_db,
            collection=query_collection,
            index_list=index_list
        )
        # if query_collection not in my_db.list_collection_names():
        #     # 如果集合不存在
        #     my_db.create_collection(query_collection)  # 创建空集合（显式创建）
        # else:
        #     pass
        my_collection = my_db[query_collection]
        # if index_list:
        #     for each_index in index_list:
        #         # 创建单字段索引
        #         my_collection.create_index([(each_index, ASCENDING)])
        # else:
        #     pass
        if query is None:
            # 无查询语句，直接插入
            self.insert(
                values,
                db=query_db,
                collection=query_collection
            )
        else:
            # 更新
            find_res, find_count = self.find(
                query=query,
                db=db,
                collection=collection
            )
            if len(find_res) == 0:
                # 未查询到数据，直接插入
                self.insert(
                    values,
                    db=query_db,
                    collection=query_collection
                )
            else:
                set_values = {"$set": values[0]}
                return my_collection.update(query, set_values, True)

    def find_db_list(
            self
    ) -> object:
        """
        查询db列表
        """
        my_db = self.client.list_database_names()
        return my_db


    def dbs(
            self
    ) -> object:
        """
        查询db列表
        """
        my_db = self.client.list_database_names()
        return my_db

    def collections(
            self,
            db: str = None,
    ) -> object:
        """
        查询collection列表，如果没输入，则查询所有
        """
        if not db:
            collections = dict()
            for each_db in self.dbs():
                collections[each_db] = self.client[each_db].list_collection_names()
            return collections
        else:
            return self.client[db].list_collection_names()


    def drop_collection(
            self,
            db: str,
            collection: str,
    ) -> object:
        """
        删除集合
        """
        return self.client[db].drop_collection(collection)


    def find(
            self,
            query: dict = None,
            db: str = None,
            collection: str = None,
            show_setting: dict = None,
            sort_setting: list = None,  # 注意在python里是list，例如[('aa', 1)]
            limit_num: int = None,
            skip_num: int = None,
            distinct_by: str = None
    ) -> object:
        # 查-多条
        """
        按照查询语句查找，内置将查询结果提取到list里面
        my_query = {'_id': 'balabala'}
        show_setting = {'_id': 0}  不显示_id，显示就为1，注意为dict格式，最好新建dict
        sort_setting = {'age': 1} 1正序 -1倒序
        query={} 表示查询所有数据
        distinct_by: 取该字段的唯一值
        """
        if db is None:
            query_db = self.db
        else:
            query_db = db
        if collection is None:
            query_collection = self.collection
        else:
            query_collection = collection
        if query is None:
            query = {}
        else:
            pass
        my_db = self.client[query_db]
        my_collection = my_db[query_collection]
        if distinct_by:
            my_doc = my_collection.find(query).distinct(distinct_by)
            return my_doc, len(my_doc)
        else:
            if show_setting is None:
                if sort_setting is None:
                    if limit_num is None:
                        if skip_num is None:
                            my_doc = my_collection.find(query)
                        else:
                            my_doc = my_collection.find(query).skip(skip_num)
                    else:
                        if skip_num is None:
                            my_doc = my_collection.find(query).limit(limit_num)
                        else:
                            my_doc = my_collection.find(query).limit(limit_num).skip(skip_num)
                else:
                    if limit_num is None:
                        if skip_num is None:
                            my_doc = my_collection.find(query).sort(sort_setting)
                        else:
                            my_doc = my_collection.find(query).sort(sort_setting).skip(skip_num)
                    else:
                        if skip_num is None:
                            my_doc = my_collection.find(query).sort(sort_setting).limit(limit_num)
                        else:
                            my_doc = my_collection.find(query).sort(sort_setting).limit(limit_num).skip(skip_num)
            else:
                if sort_setting is None:
                    if limit_num is None:
                        if skip_num is None:
                            my_doc = my_collection.find(query, show_setting)
                        else:
                            my_doc = my_collection.find(query, show_setting).skip(skip_num)
                    else:
                        if skip_num is None:
                            my_doc = my_collection.find(query, show_setting).limit(limit_num)
                        else:
                            my_doc = my_collection.find(query, show_setting).limit(limit_num).skip(skip_num)
                else:
                    if limit_num is None:
                        if skip_num is None:
                            my_doc = my_collection.find(query, show_setting).sort(sort_setting)
                        else:
                            my_doc = my_collection.find(query, show_setting).sort(sort_setting).skip(skip_num)
                    else:
                        if skip_num is None:
                            my_doc = my_collection.find(query, show_setting).sort(sort_setting).limit(limit_num)
                        else:
                            my_doc = my_collection.find(query, show_setting).sort(sort_setting).limit(limit_num).skip(skip_num)
            res_list = list()
            for doc in my_doc:
                res_list.append(doc)
            res_count = my_doc.count()
            if res_count:
                return res_list, my_doc.count()
            else:
                return res_list, 0

    def distinct(
            self,
            by: str,
            db: str = None,
            collection: str = None,
    ) -> object:
        """
        查询某个字段的唯一值
        """
        if db is None:
            query_db = self.db
        else:
            query_db = db
        if collection is None:
            query_collection = self.collection
        else:
            query_collection = collection
        my_db = self.client[query_db]
        my_collection = my_db[query_collection]

        my_doc = my_collection.distinct(by)

        res_list = list()
        for doc in my_doc:
            res_list.append(doc)
        return res_list

    def aggregate(
            self,
            query: list = None,
            db: str = None,
            collection: str = None
    ) -> object:
        """
        聚合查询
        """
        if not db:
            query_db = self.db
        else:
            query_db = db
        if collection is None:
            query_collection = self.collection
        else:
            query_collection = collection
        if query is None:
            query = [{}]
        else:
            pass
        my_db = self.client[query_db]
        my_collection = my_db[query_collection]
        my_doc = my_collection.aggregate(query)

        res_list = list()
        for doc in my_doc:
            res_list.append(doc)

        return res_list

    def find_page(
            self,
            db: str = None,
            collection: str = None,
            query: dict = None,
            previous_tag: str = '_id',
            previous_value=None,  # 非强制类型，str/int
            where_str: str = '$gt',
            show_setting: dict = None,
            sort_setting: list = [('_id', -1)],  # 注意在python里是list，例如[('aa', 1)]，1（升序），-1（降序）
            limit_num: int = 10
    ) -> object:
        """
        提供翻页查询功能，按照上一个位置向后翻页
        条件查询：
            $lt <
            $lte <=
            $gt >
            $gte >=
        """
        if db is None:
            query_db = self.db
        else:
            query_db = db
        if collection is None:
            query_collection = self.collection
        else:
            query_collection = collection

        if previous_tag == '_id':
            if query is None:
                if previous_value is None:
                    query = {}
                else:
                    query = {previous_tag: {where_str: ObjectId(previous_value)}}
            else:
                if previous_value is None:
                    query = {}
                else:
                    query[previous_tag] = {where_str: ObjectId(previous_value)}
        else:
            if query is None:
                if previous_value is None:
                    query = {}
                else:
                    query = {previous_tag: {where_str: previous_value}}
            else:
                if previous_value is None:
                    query = {}
                else:
                    query[previous_tag] = {where_str: previous_value}
        my_db = self.client[query_db]
        my_collection = my_db[query_collection]
        if show_setting is None:
            if sort_setting is None:
                my_doc = my_collection.find(query).limit(limit_num)
            else:
                my_doc = my_collection.find(query).sort(sort_setting).limit(limit_num)
        else:
            if sort_setting is None:
                my_doc = my_collection.find(query, show_setting).limit(limit_num)
            else:
                my_doc = my_collection.find(query, show_setting).sort(sort_setting).limit(limit_num)
        res_list = list()
        for doc in my_doc:
            res_list.append(doc)
        return res_list, my_doc.count()

    def find_random(
            self,
            db: str = None,
            collection: str = None,
            num: int = 1
    ) -> list:
        # 随机抽取指定量的数据
        """
        按照查询语句查找，内置将查询结果提取到list里面
        my_query = {'_id': 'balabala'}
        """
        if db is None:
            query_db = self.db
        else:
            query_db = db
        if collection is None:
            query_collection = self.collection
        else:
            query_collection = collection
        my_db = self.client[query_db]
        my_collection = my_db[query_collection]
        my_doc = my_collection.aggregate([{'$sample': {'size': num}}])
        res_list = list()
        for doc in my_doc:
            res_list.append(doc)
        return res_list

    def collection_records(
            self,
            query: dict = None,
            db: str = None,
            collection: str = None
    ) -> int:
        # 查询collection的文档数量
        if db is None:
            query_db = self.db
        else:
            query_db = db
        if collection is None:
            query_collection = self.collection
        else:
            query_collection = collection
        my_db = self.client[query_db]
        my_collection = my_db[query_collection]
        if query is None:
            collection_count = my_collection.find().count()
        else:
            collection_count = my_collection.find(query).count()
        return collection_count

    def get_page_data(
            self,
            query: dict = None,
            db: str = None,
            collection: str = None,
            show_setting: dict = None,
            sort_setting: list = None,
            previous_tag: str = None,
            page_size: int = 10,
            page: int = 1,
            _id: str = None
    ) -> object:
        """
        获取某页的数据
        """
        if db is None:
            query_db = self.db
        else:
            query_db = db
        if collection is None:
            query_collection = self.collection
        else:
            query_collection = collection

        if _id is None:
            # 不按前序步骤标记翻页，按照最新页翻页
            find_res, find_count = self.find(
                query=query,
                db=query_db,
                collection=query_collection,
                show_setting=show_setting,
                sort_setting=sort_setting,
                limit_num=page_size,
                skip_num=(page - 1) * page_size
            )
            res_new_list = list()
            for each_find in find_res:
                if each_find.get('_id') is not None:
                    each_find['_id'] = str(each_find.get('_id'))
                res_new_list.append(each_find)
            return res_new_list, find_count
        else:
            # 从指定位置向后翻页，先按照_id找到排序字段的值，然后按照这个序列翻页继续查询
            find_record, find_count = self.find(
                query={'_id': ObjectId(_id)},
                db=query_db,
                collection=query_collection,
                show_setting=show_setting
            )
            if len(find_record) == 0:
                return [], 0
            else:
                previous_value = find_record[0][previous_tag]
                find_res, find_count = self.find_page(
                    query=query,
                    db=query_db,
                    collection=query_collection,
                    show_setting=show_setting,
                    sort_setting=sort_setting,
                    previous_tag=previous_tag,
                    previous_value=previous_value,
                    limit_num=page_size
                )
                res_new_list = list()
                for each_find in find_res:
                    if each_find.get('_id') is not None:
                        each_find['_id'] = str(each_find.get('_id'))
                    res_new_list.append(each_find)
                return res_new_list, find_count

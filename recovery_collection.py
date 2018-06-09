# coding=utf-8
"""
将Collection中的数据恢复出来的一个
"""
import json
import sys

from config import *
import wt_util
import time
from mongo_util import mongo_dump_data


def dump_collection(
        collection_name: str,
        target_database: str = "final_mongo",
        target_collection: str = "temp",
        drop_after_dump: bool = True
):
    """

    :param collection_name:
    :param target_database:
    :param target_collection:
    :param drop_after_dump:
    :param re_index:
    :return:
    """
    """
    获取MongoDB表的元信息
    :return:
    """
    with TempMongoDBProcess(is_clean_path=True) as tmp:
        # 创建一个库，创建一个Collection
        with tmp.create_connection() as mc:
            db = mc.conn.get_database(target_database)
            coll = db.get_collection(target_collection)
            coll.insert_one({"x": 1})
            coll.remove({})
            uri = db.command({
                "collStats": target_collection
            })["wiredTiger"]["uri"]
            target_recovery_file = str(uri).replace("statistics:table:", "") + ".wt"
    # 数据库已经关闭，并且成功的获取了URI
    # 抓取DUMP文件
    dump_file_name = os.path.join(os.getcwd(), "temp.wtdump")
    wt_util.dump(crashed_mongo_path, collection_name, dump_file_name)
    # 休息三秒，等待锁的释放
    time.sleep(3)
    # 重新加载到指定uri中
    wt_util.load(temp_db_path, target_recovery_file, dump_file_name)
    with TempMongoDBProcess(is_clean_path=False) as tmp:
        # 导出dump文件
        mongo_dump_data(target_database, target_collection)
        # 有必要的话删除表
        if drop_after_dump:
            with tmp.create_connection() as mc:
                mc.conn.get_database(target_database).get_collection(target_collection).drop()


if __name__ == '__main__':
    dump_collection(sys.argv[1], sys.argv[2], sys.argv[3])

# coding=utf-8
"""
利用WT工具加载表结构信息

启动MongoDB实例，
尝试修复META信息表
尝试dump出META信息
"""
import json
from config import *
import wt_util
import time
import sys


def load_meta_data() -> dict:
    """
    获取MongoDB表的元信息
    :return:
    """
    with TempMongoDBProcess(is_clean_path=True) as tmp:
        # 创建一个库，创建一个Collection
        with tmp.create_connection() as mc:
            db = mc.conn.get_database("final_mongo")
            coll = db.get_collection("meta")
            coll.insert_one({"x": 1})
            coll.remove({})
            uri = db.command({
                "collStats": "meta"
            })["wiredTiger"]["uri"]
            target_recovery_file = str(uri).replace("statistics:table:", "") + ".wt"
    # 数据库已经关闭，并且成功的获取了URI
    # 抓取DUMP文件
    dump_file_name = os.path.join(os.getcwd(), "meta.wtdump")
    wt_util.dump(crashed_mongo_path, "table:_mdb_catalog", dump_file_name)
    # 休息三秒，等待锁的释放
    time.sleep(3)
    # 重新加载到指定uri中
    wt_util.load(temp_db_path, target_recovery_file, dump_file_name)
    with TempMongoDBProcess(is_clean_path=False) as tmp:
        # 创建一个库，创建一个Collection
        with tmp.create_connection() as mc:
            docs = [x for x in mc.conn.get_database("final_mongo").get_collection("meta").find({})]
            mapping = {doc["md"]["ns"]: doc["ident"] for doc in docs if "md" in doc and "ident" in doc}
            print(json.dumps(mapping, indent=2))
            return mapping


if __name__ == '__main__':
    with open("meta_data.json", "w") as fp:
        json.dump([
            {
                "db": collection_info.split(".")[0],
                "coll": collection_info.split(".")[1],
                "wt": wired_tiger_info
            }
            for collection_info, wired_tiger_info in load_meta_data().items()
        ], fp, indent=2)

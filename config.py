# coding=utf-8
import os
from subprocess import Popen
# MongoDB 可执行文件路径
import yaml
import pymongo

# MongoDB二进制文件
mongo_bin_path = "/opt/mongodb/bin"

# 有线老虎工具集编译过后的地址
wt_bin_path = "/opt/wiredtiger/"

# 已经被破坏的MongoDB的位置
crashed_mongo_path = os.path.join(os.getcwd(), "crashed_mongo")

temp_db_path = os.path.join(os.getcwd(), "final_mongo_temp")


def make_temp_db(make_path: str = temp_db_path):
    """
    创建数据库使用的文件夹
    :return:
    """
    os.system("mkdir -p " + make_path)


def clean_temp_db(clean_path: str = temp_db_path):
    """
    清理临时数据库使用的文件夹
    :return:
    """
    os.system("rm -rf " + os.path.join(clean_path, "*"))
    make_temp_db(clean_path)


temp_db_port = 17027

# MongoDB 本地配置
local_mongo_config = {
    "net": {
        "bindIp": "127.0.0.1",
        "port": temp_db_port
    },
    "storage": {
        "directoryPerDB": True,
        "dbPath": temp_db_path,
        "engine": "wiredTiger"
    }
}


def generate_local_config(config_file: str, db_path: str = temp_db_path):
    """
    生成本地MongoDB配置文件
    :param config_file: 保存位置
    :param db_path: 数据库位置
    :return:
    """
    config_data = local_mongo_config
    config_data["storage"]["dbPath"] = db_path
    with open(config_file, "w") as fp:
        yaml.dump(config_data, fp)


class MongoConnection:
    def __init__(
            self,
            host: str = "127.0.0.1",
            port: int = 27017,
            user: str = None,
            password: str = None,
            auth_db: str = "admin"
    ):
        self.conn = pymongo.MongoClient(host, port)
        if user is not None and password is not None:
            self.auth_db = self.conn.get_database(auth_db)
            self.auth_db.authenticate(user, password)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()


class TempMongoDBProcess:
    """
    启动临时的MongoDB
    """

    def __init__(self, db_path: str = temp_db_path, is_clean_path: bool = False):
        """
        初始化
        :param db_path:
        :param is_clean_path:
        """
        if is_clean_path:
            clean_temp_db(db_path)
        else:
            make_temp_db(db_path)
        # 生成配置文件
        config_file = os.path.join(os.getcwd(), "temp_mongo.yaml")
        generate_local_config(config_file, db_path)
        self.__process = Popen(
            [os.path.join(mongo_bin_path, "mongod"), "--config", config_file, "--nojournal"])

    def create_connection(self) -> MongoConnection:
        return MongoConnection(port=temp_db_port)

    def close(self):
        self.__process.terminate()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# MongoDB 写入目标机器
mongo_target = {
    "host": "10.10.11.12",  # 地址
    "port": 27017,  # 端口
    "final_db": "final_mongo"  # 元信息无法恢复的时候默认使用的数据库
}

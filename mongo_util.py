import os
from config import temp_db_port, mongo_bin_path


def mongo_dump_data(db: str, coll: str):
    """
    备份MongoDB数据
    :param db:
    :param coll:
    :return:
    """
    command = os.path.join(mongo_bin_path, "mongodump") + \
              "  -v --host 127.0.0.1:{}  -d \"{}\" -c \"{}\" --archive={}.{}.mongz --gzip".format(
                  temp_db_port, db, coll, db, coll
              )
    print(command)
    os.system(
        command
    )

# coding=utf-8
"""
有线老虎工具集
"""
from config import *


def get_command(host: str):
    """
    获取WT工具指令
    :param host: MongoDB数据目录的绝对路径
    :return:
    """
    return "\"{}\" -v -h \"{}\" -C \"extensions=[{}]\" ".format(
        os.path.join(wt_bin_path, "wt"),
        host,
        os.path.join(wt_bin_path, "ext/compressors/snappy/.libs/libwiredtiger_snappy.so")
    )


def dump(host: str, wt_file: str, dump_file: str):
    """
    将指定的URI导出为DUMP文件
    :param host: MongoDB数据目录的绝对路径
    :param wt_file: 有线老虎文件
    :param dump_file: 需要备份的文件
    :return:
    """
    os.system(get_command(host) + " -R dump -f \"{0}\" \"{1}\"".format(dump_file, wt_file))


def load(host: str, wt_file: str, dump_file: str):
    """
    将指定的URI导出为DUMP文件
    :param host: MongoDB数据目录的绝对路径
    :param wt_file: 有线老虎文件
    :param dump_file: 需要备份的文件
    :return:
    """
    if wt_file.endswith(".wt"):
        wt_file = wt_file[:-3]
    os.system(get_command(host) + " -R load -f \"{0}\" -r \"{1}\"".format(dump_file, wt_file))

# 爬虫获取青年大学习的数据
import os.path
import shutil

from connector import Connector
from data_process import Processor

if __name__ == "__main__":
    # 检查config目录
    if not os.path.exists("../config"):
        os.mkdir("../config")

    # 检查 account.json 文件,如果不存在就拷贝template目录下的文件过去
    if not os.path.exists("../config/account.json"):
        shutil.copy("../template/account.json", "../config/account.json")

    connector = Connector()
    connector.get_major_study_data()
    connector.get_all_classes_data()
    processor = Processor()
    processor.merge_data()
    processor.find_not_study()

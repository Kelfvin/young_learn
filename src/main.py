# 爬虫获取青年大学习的数据
import getpass
import json
import os.path

from connector import Connector
from data_process import Processor

if __name__ == "__main__":
    # 检查config目录
    if not os.path.exists("../config"):
        os.mkdir("../config")

    # 检查 account.json 文件,如果不存在就拷贝template目录下的文件过去
    if not os.path.exists("../config/account.json"):
        username = input("请输入用户名：")
        # 获取用户输入的密码，不要明文显示
        password = getpass.getpass("请输入密码：")
        with open("../config/account.json", "w") as f:
            data = {}
            data["username"] = username
            data["password"] = password
            json.dump(data, f)

    connector = Connector()
    connector.get_major_study_data()
    connector.get_all_classes_data()
    processor = Processor()
    processor.merge_data()
    processor.find_not_study()

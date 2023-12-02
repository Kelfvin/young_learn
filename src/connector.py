import json
import os
import re
import shutil
import time

import pandas as pd
import requests
from tqdm import tqdm

from config import Config


class Connector:
    def __init__(self) -> None:
        self.header = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        }

        self.token = None
        self.uid = None
        self.orgId = None
        self.orgName = ""
        self.study_url = "https://dxx.scyol.com/backend/study/organize/list"

        self._init_data_dir()

        self._login()

    def _init_data_dir(self):
        """初始化数据目录"""

        self.save_data_dir = Config.save_data_dir
        # 检查是否存在data目录，如果不存在就创建
        if not os.path.exists(self.save_data_dir):
            os.mkdir(self.save_data_dir)

        # 获取时间戳
        self.timestamp = time.strftime("%Y-%m-%d", time.localtime())
        # 创建今天的数据目录
        self.today_data_dir = os.path.join(self.save_data_dir, self.timestamp)
        if not os.path.exists(self.today_data_dir):
            os.mkdir(self.today_data_dir)

        # 清空目录
        self._delete_directory_contents(self.today_data_dir)

        # 创建班级学习数据存放的目录
        self.classes_data_dir = os.path.join(self.today_data_dir, "班级学习数据")
        if not os.path.exists(self.classes_data_dir):
            os.mkdir(self.classes_data_dir)

    def _delete_directory_contents(self, directory_path):
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)

    def _login(self):
        """登录获取token"""
        self.login_url = "https://dxx.scyol.com/backend/adminUser/login"
        # 获取登录的密码配置文件
        # 读取配置文件
        with open(Config.admin_login_info_path, "r") as f:
            data = json.load(f)
        response = requests.post(
            self.login_url, data=json.dumps(data), headers=self.header
        )
        if response.json()["code"] != 200:
            raise Exception("登录失败")

        print("登录成功")
        # 保存token
        self.token = response.json()["data"]["token"]
        # 添加请求头
        self.header["token"] = self.token

        # 保存ordID
        self.orgId = response.json()["data"]["orgId"]

        # 保存uid
        self.uid = response.json()["data"]["uid"]

    def get_latest_stagesId(self):
        """获取最新的青年大学习的stagesId
        其实就是获取当前是第几期的id"""
        url = "https://dxx.scyol.com/backend/index/stat"
        response = requests.get(url, headers=self.header)

        latest_stagesId = response.json()["data"]["count"]
        # 由于是从首页获取的ID，首页的ID显示的是上一期的ID，所以需要加1，不知道是不是，没长时间测试过，后面可能要改
        self.latest_stagesId = latest_stagesId + 1
        print(f"当前是第{self.latest_stagesId}期")
        return self.latest_stagesId

    def get_major_study_data(self):
        """获取整个专业大学习的数据
        同时将下级组织的orgId保存到一个列表中"""
        payload_data = {
            "orgName": self.orgName,
            "pageNo": 1,
            "pageSize": 30,
            "pid": self.orgId,
            "stagesId": self.get_latest_stagesId(),
        }

        response = requests.post(
            self.study_url, data=json.dumps(payload_data), headers=self.header
        )
        classes_data = response.json()["data"]

        # 去除2019年的数据，因为我们2019支部没有删除
        classes_data = list(
            filter(lambda x: x["orgName"].find("2019") == -1, classes_data)
        )

        # 保存数据
        self.clases_data_json = classes_data
        df = pd.DataFrame(columns=["组织名", "学习人数"])

        for a_class_data in classes_data:
            df.loc[len(df)] = {
                "组织名": a_class_data["orgName"],
                "学习人数": a_class_data["orgStagesTotalNum"],
            }

        # 对组织名进行修改
        # 使用正则表达式，软件工程2020级1班团支部 -> 2020级1班
        df["组织名"] = df["组织名"].apply(lambda x: re.findall(r"([0-9]+级.*)团支部", x)[0])

        path = os.path.join(self.today_data_dir, "专业大学习数据.xlsx")
        df.to_excel(path, index=False)

    def get_all_classes_data(self):
        """获取各个班级的数据"""
        print("开始获取各个班级的数据")
        for a_class_data in tqdm(self.clases_data_json):
            self.get_a_class_data(
                a_class_data["orgName"],
                self.latest_stagesId,
                a_class_data["orgId"],
            )

    def get_a_class_data(
        self,
        orgName,
        stagesId,
        orgId,
    ):
        """获取一个班级的数据"""
        param = f"stagesId={stagesId}&orgId={orgId}&name=&token={self.token}"
        url = "https://dxx.scyol.com/backend//study/student/excel?"
        # 请求下载数据
        response = requests.get(url + param, headers=self.header)
        # 保存数据
        path = os.path.join(self.classes_data_dir, f"{orgName}.xlsx")
        with open(path, "wb") as f:
            f.write(response.content)


if __name__ == "__main__":
    df = pd.read_excel("../data/2023-12-02/专业大学习数据.xlsx")
    # 使用正则表达式，软件工程2020级1班团支部 -> 2020级1班，用团支部作为标志，且通过获取捕获组的方式获取班级名
    df["组织名"] = df["组织名"].apply(lambda x: re.findall(r"([0-9]+级.*)团支部", x)[0])
    print(df)

import json


class Admin:
    def __init__(self, name, age):
        # 从config中读取配置
        self.name = name
        self.age = age

    # 工厂方法
    @classmethod
    def from_config(cls):
        path = "../config/account.json"
        # 读取配置文件
        with open(path, "r") as f:
            config = json.load(f)
        # 返回一个对象
        return Admin(config["name"], config["age"])

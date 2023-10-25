# 用于处理数据

import os
import time
import warnings

import pandas as pd

from config import Config

warnings.simplefilter("ignore")
# 老是有警告，先忽略掉


class Processor:
    """一个用于数据处理的类"""

    def __init__(self) -> None:
        self.today_data_dir = os.path.join(
            Config.save_data_dir, time.strftime("%Y-%m-%d", time.localtime())
        )
        self.class_data_dir = os.path.join(self.today_data_dir, "班级学习数据")

    # 将数据合成一个文件
    def merge_data(self):
        """将数据合成一个文件"""
        # 获取所有文件名
        file_names = os.listdir(self.class_data_dir)
        # 创建合并后的文件
        dataframes = []
        for file_name in file_names:
            file_path = os.path.join(self.class_data_dir, file_name)
            df = pd.read_excel(file_path)
            dataframes.append(df)
        # 合并数据
        df = pd.concat(dataframes)
        # 删除电话字段，避免隐私泄漏
        df.drop(["电话"], axis=1, inplace=True)

        # 将班级字段进行分类，即不同的班级放在不同的sheet中
        # 获取班级名
        class_names = df["选择组织"].unique()
        # 创建writer
        date = time.strftime("%Y-%m-%d", time.localtime())
        writer = pd.ExcelWriter(
            os.path.join(self.today_data_dir, f"青年大学习名单-{date}.xlsx"),
            engine="xlsxwriter",
        )

        # 先放总表
        df.to_excel(writer, sheet_name="总学习情况", index=False)

        # 将数据写入excel
        for class_name in class_names:
            df[df["选择组织"] == class_name].to_excel(
                writer, sheet_name=class_name, index=False
            )
        # 关闭writer
        writer.close()

    # 找到还没有做青年大学习的团员
    def find_not_study(self):
        pass


if __name__ == "__main__":
    processor = Processor()
    processor.merge_data()

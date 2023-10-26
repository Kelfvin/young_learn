# 用于处理数据

import os
import time
import warnings

import matplotlib.pyplot as plt
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
        file_names = self._get_class_file_names_list()
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
        class_names.sort()
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

    def _get_class_file_names_list(self):
        """获取班级文件名的列表，返回的是排序过后的"""
        file_names = os.listdir(self.class_data_dir)
        file_names.sort()
        return file_names

    # 找到还没有做青年大学习的团员
    def find_not_study(self):
        pass

    # 画出学习情况的统计图
    def generate_statistics(self):
        """画出学习情况的统计图"""
        # 设置中文字体
        plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]
        # 遍历编辑文件，统计各个班级的学习人数
        study_record_list = []
        # 文件名
        file_names = self._get_class_file_names_list()
        for file_name in file_names:
            # 班级名称
            class_name = file_name.split(".")[0].replace("软件工程", "").replace("团支部", "")
            # 获取文件路径
            file_path = os.path.join(self.class_data_dir, file_name)
            # 读取数据
            df = pd.read_excel(file_path)
            # 获取数据的条数，即学习人数
            study_num = df.shape[0]
            # 添加到列表中
            study_record_list.append([class_name, study_num])
        # 将列表转换为DataFrame
        df = pd.DataFrame(study_record_list, columns=["班级", "学习人数"])
        # 画图
        plt.figure(figsize=(10, 5), dpi=150)
        plt.bar(df["班级"], df["学习人数"])
        plt.xlabel("班级")
        plt.ylabel("学习人数")
        plt.title("学习情况统计")
        # 显示数字
        for x, y in enumerate(df["学习人数"]):
            plt.text(x, y + 0.1, y, ha="center")
        # x轴标签旋转
        plt.xticks(rotation=30)
        # 解决文字显示不全的问题
        plt.tight_layout()
        plt.savefig(os.path.join(self.today_data_dir, "学习情况统计.png"))
        plt.close()


if __name__ == "__main__":
    processor = Processor()
    processor.merge_data()
    processor.generate_statistics()

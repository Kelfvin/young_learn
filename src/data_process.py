# 用于处理数据

import os
import re
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
        self.major_statistic_data_path = os.path.join(
            self.today_data_dir, "专业大学习数据.xlsx"
        )

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
        """找到还没有做青年大学习的团员"""
        # 所有团员的列表
        name_df = pd.read_excel(Config.name_list_path)
        # 将 组织全称 列的数据 ）前的东西去掉
        name_df["组织全称"] = name_df["组织全称"].apply(lambda x: x.split("系")[1])

        # 已经学习的团员的df
        date = time.strftime("%Y-%m-%d", time.localtime())
        learned_file_path = os.path.join(self.today_data_dir, f"青年大学习名单-{date}.xlsx")

        learned_df = pd.read_excel(learned_file_path, sheet_name="总学习情况")

        # 找到还没有学习的团员
        not_learned_df = name_df[~name_df["姓名"].isin(learned_df["姓名"])]

        # 只保留姓名和组织全称两列
        not_learned_df = not_learned_df[["姓名", "组织全称"]]

        # 根据组织全称进行分组，不同的名称放在不同的sheet中
        # 获取组织全称
        class_names = not_learned_df["组织全称"].unique()
        class_names.sort()
        # 先放总表
        not_learned_df.to_excel(
            os.path.join(self.today_data_dir, f"未学习团员名单-{date}.xlsx"),
            sheet_name="总未学习名单",
            index=False,
        )
        # 创建writer
        date = time.strftime("%Y-%m-%d", time.localtime())
        writer = pd.ExcelWriter(
            os.path.join(self.today_data_dir, f"未学习团员名单-{date}.xlsx"),
            engine="xlsxwriter",
        )

        # 将数据写入excel
        for class_name in class_names:
            not_learned_df[not_learned_df["组织全称"] == class_name].to_excel(
                writer, sheet_name=class_name, index=False
            )
        # 关闭writer
        writer.close()

    # 画出学习情况的统计图
    def generate_statistics(self):
        """画出学习情况的统计图"""
        # 设置中文字体
        # 根据不同的系统设置不同的字体
        if os.name == "nt":
            # windows
            plt.rcParams["font.sans-serif"] = ["SimHei"]
        else:
            plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]
        # 访问专业大学习的人数
        df = pd.read_excel(self.major_statistic_data_path)

        # 画图
        plt.figure(figsize=(10, 5), dpi=150)
        plt.bar(df["组织名"], df["学习人数"])
        plt.xlabel("组织名")
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

    def generate_study_rate_pie(self):
        """生成学习率的饼图"""
        # 读取团员名单
        name_list_df = pd.read_excel(Config.name_list_path)
        # 对组织名称进行简化，正则表达式
        name_list_df["组织全称"] = name_list_df["组织全称"].apply(
            lambda x: re.findall(r"([0-9]+级.*)团支部", x)[0]
        )

        # 读取专业大学习的数据
        major_study_df = pd.read_excel(self.major_statistic_data_path)
        # 统计name_list_df中的人数

        # 统计团员人数
        name_list_df = name_list_df.groupby("组织全称").count()
        name_list_df.reset_index(inplace=True)
        name_list_df.rename(columns={"姓名": "团员人数", "组织全称": "组织名"}, inplace=True)

        print(name_list_df)
        print(major_study_df)

        # 合并两个df
        df = pd.merge(major_study_df, name_list_df, on="组织名")
        # 计算学习率
        df["学习率"] = df["学习人数"] / df["团员人数"]
        # 画图

        # 设置中文字体
        # 根据不同的系统设置不同的字体
        if os.name == "nt":
            # windows
            plt.rcParams["font.sans-serif"] = ["SimHei"]
        else:
            plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]

        # 每个组织画一个饼状图，画在一张图上
        plt.figure(figsize=(10, 5), dpi=150)
        # 计算子图的行数和列数
        cols = df.shape[0] // 2 + 1
        rows = 2

        for i in range(df.shape[0]):
            plt.subplot(rows, cols, i + 1)
            plt.pie(
                [df["学习人数"][i], max(0, df["团员人数"][i] - df["学习人数"][i])],
                autopct="%1.1f%%",
            )
            #
            plt.title(df["组织名"][i])

        # 为整个图添加一个总的图标，蓝色的是学习人数，橙色的是未学习人数，要求有颜色
        plt.legend(
            ["学习", "未学习"],
            loc="upper center",
            bbox_to_anchor=(0.5, -0.05),
            fancybox=True,
            shadow=True,
            ncol=2,
        )
        # 添加标题
        plt.suptitle("各个组织学习率")
        plt.tight_layout()

        plt.savefig(os.path.join(self.today_data_dir, "学习率统计.png"))


if __name__ == "__main__":
    processor = Processor()
    processor.merge_data()
    processor.generate_statistics()
    processor.generate_study_rate_pie()
    processor.find_not_study()

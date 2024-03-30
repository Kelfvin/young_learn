# 关于本项目

项目用于一键拉取青年大学习后台数据，方便大家进行数据分析。

运行过程：

![Alt text](assets/image.png)

运行完成后生成文件：

![Alt text](assets/image-1.png)

生成统计图

![Alt text](assets/%E5%AD%A6%E4%B9%A0%E6%83%85%E5%86%B5%E7%BB%9F%E8%AE%A1.png)


# 使用

## 0. 安装依赖

```bash
pip install -r requirements.txt
```

## 1. 导入智慧团建导出名单

将名单文件(xlsx)放入config/ 目录下，文件名重命名为`name_list.xlsx`。

表格格式为:

| 学号* | 姓名 | 班级 |
| --- | --- | --- |

*表示可选

## 2. 运行

```bash
cd src
python main.py
```

## 3. 查看结果

结果在`data/`目录下。以日期命名的文件夹中，包含了当天的数据。

# 更新日志

## 2024-3-30

简化了名单的格式，方便自定义名单。
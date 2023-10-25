# 爬虫获取青年大学习的数据
from connector import Connector
from data_process import Processor

if __name__ == "__main__":
    connector = Connector()
    connector.get_major_study_data()
    connector.get_all_classes_data()
    processor = Processor()
    processor.merge_data()
    processor.find_not_study()

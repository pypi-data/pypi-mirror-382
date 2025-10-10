from typing import List, Union

"""
表格处理
"""


def format_list_index_rank(data_list, index=1, index_key="index"):
    for data in data_list:
        data[index_key] = str(index)
        index = index + 1


class TableChart:
    @staticmethod
    def list2table(dataSource: List[dict], columns: list, total: int = 0, count: int = 0, offset=0, sum: int = 0,
                   **kwargs):
        """
            list数据转换成表格
            :param sum: 实际总数
            :param offset: 序号跳过数量
            :param count: 实际总数(页面展示值)
            :param total: 实际数据总数
            :param dataSource: 列表数据
            :param columns: 表头，支持dict和list ，实例1：{"企业名称": "name"},实例2：[{"title": "企业名称","key:"name"}]
        """
        format_list_index_rank(dataSource, offset + 1)
        return {
            "chart_type": "Table",
            "count": count,
            "total": total,
            "sum": sum,
            "columns": columns,
            "dataSource": dataSource
        }

    @staticmethod
    def list2table_v2(data: List[dict], columns: Union[list, dict], total: int = 0, count: int = 0, page_number=0,
                      page_size=0, **kwargs):
        """
            list数据转换成表格
            :param page_size:
            :param page_number:
            :param count: 实际总数
            :param total: 实际数据总数
            :param data: 列表数据
            :param columns: 表头，支持dict和list ，实例1：{"企业名称": "name"},实例2：[{"title": "企业名称","key:"name"}]
        """
        offset = (page_number - 1) * page_size
        format_list_index_rank(data, offset + 1)
        new_columns = []
        if isinstance(columns, dict):
            for key, value in columns.items():
                new_columns.append({"title": key, "dataIndex": value})
        elif isinstance(columns, list):
            new_columns = columns
        return {
            "chart_type": "Table",
            "count": count,
            "total": total,
            "columns": new_columns,
            "dataSource": data
        }

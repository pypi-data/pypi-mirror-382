import copy
import importlib
from typing import List

"""
表格处理
"""


class TableChart:
    @staticmethod
    def list2table_with_page(data: List[dict], head, title: str = "", total: int = 0, count: int = 0,
                             index_enable: bool = False, index_name="序号", index_key="index",
                             page_num: int = 1, page_size: int = 10, column_covert: dict = None,
                             column_keys: dict = None, custom_head_enable: bool = False, **kwargs):
        """
            list数据转换成表格
            :param count: 实际总数
            :param custom_head_enable: 自定义表头开关
            :param index_key: 索引key
            :param index_name: 索引字段名
            :param column_covert: {"id":str}
            :param total: 实际数据总数
            :param page_size: 每页数量
            :param page_num: 页码
            :param index_enable: 是否带序号
            :param column_keys:数据对应点的keys，实例1：{"name1":"name2"} 说明：name1：接口返回字段名，name2:是数据的key,支持多层key，通过.连接，例如：basic.name
            :param data: 列表数据
            :param title: 表格标题，字符串类型
            :param head: 表头，支持dict和list ，实例1：{"企业名称": "name"},实例2：[{"title": "企业名称","key:"name"}]
        """
        try:
            common_utils = importlib.import_module("lesscode_utils.common_utils")
        except ImportError:
            raise Exception(f"lesscode_utils is not exist,run:pip install lesscode_utils")
        data = copy.copy(data)
        result = {
            "chart_type": "table",
            "title": title,
            "columns": [],
            "dataSource": [],
            "total": total,
            "count": count,
            "auth_count": total
        }
        if not custom_head_enable:
            if index_enable:
                result["columns"].append({"title": index_name,
                                          "dataIndex": index_key, "key": index_key})
            if isinstance(head, dict):
                for key, value in head.items():
                    result["columns"].append({"title": key,
                                              "dataIndex": value, "key": value})
            elif isinstance(head, list):
                for column in head:
                    result["columns"].append({"title": column.get("title"),
                                              "dataIndex": column.get("key"), "key": column.get("key")})
            else:
                raise Exception(f'head={head} is error')
        else:
            result["columns"] = head
        index_start = (page_num - 1) * page_size
        if column_keys:
            for item in data:
                data_item = {
                }
                for key, value in column_keys.items():
                    new_value = common_utils.get_value_from_dict(item, value)
                    if column_covert:
                        if key in column_covert:
                            new_value = common_utils.convert(new_value, column_covert.get(key))
                    data_item[key] = new_value
                if index_enable:
                    data_item[index_key] = index_start + 1
                result["dataSource"].append(data_item)
                index_start += 1
        else:
            if index_enable:
                for item in data:
                    item[index_key] = index_start + 1
                    result["dataSource"].append(item)
                    index_start += 1
            else:
                result["dataSource"] = data
        result["total"] = total
        if kwargs:
            result["pool"] = kwargs
        return result

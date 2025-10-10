import copy
from typing import List

"""
金字塔处理
"""


class PyramidChart:
    @staticmethod
    def pyramid(data: List[dict], unit="", title: str = "", decimal_place: int = 2, total: int = 0, name_key="name",
                value_key="value", **kwargs):
        """
        :param value_key: 值的key
        :param name_key: name的key
        :param total: 计算比例的总数
        :param data: 数据，示例:[{"name":"上市企业","value":1}]
        :param unit: 数据单位
        :param title: 图题
        :param decimal_place: 小数点位数
        :param kwargs: 设置pool
        :return:
        """
        data = copy.copy(data)
        if not total:
            total = sum([_.get("value") for _ in data if _.get("value")])
        if total == 0:
            total = 1
        result = {
            "chart_type": "pyramid",
            "title": title,
            "series": [
                {
                    "name": title,
                    "data": [
                        {"name": item.get(name_key), "value": item.get(value_key),
                         "proportion": round(item.get(value_key, 0) / total * 100, decimal_place)} for item in data],
                    "unit": unit
                }
            ]
        }
        if kwargs:
            result["pool"] = kwargs

        return result

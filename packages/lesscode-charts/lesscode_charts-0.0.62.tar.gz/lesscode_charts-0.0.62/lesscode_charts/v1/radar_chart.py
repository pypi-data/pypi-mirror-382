from typing import List

"""
雷达图
"""


class RadarChart:
    @staticmethod
    def radar(indicator_list: List[str], data_list: List[dict], title: str, unit_list: List[str], name_key="name",
              value_key="value", **kwargs):
        """
        :param value_key:
        :param name_key:
        :param indicator_list: 指标列表
        :param data_list: 数据，value字段为列表
        :param title: 图题
        :param unit_list: 单位列表
        :return:
        """
        result = {
            "chart_type": "radar",
            "indicator": indicator_list,
            "series": [
                {
                    "name": title,
                    "data": [
                        {"name": item.get(name_key), "value": item.get(value_key, [])} for item in data_list
                    ],
                    "unit": unit_list
                }
            ],
            "title": title
        }
        if kwargs:
            result["pool"] = kwargs
        return result

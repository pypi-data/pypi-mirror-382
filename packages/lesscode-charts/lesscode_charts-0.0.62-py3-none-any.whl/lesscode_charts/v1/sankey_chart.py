import copy
from typing import List

"""
桑基图
"""


class SankeyChart:
    @staticmethod
    def sankey(data: List[dict], name="", title: str = "", data_key="id", parent_key="parent_id", **kwargs):
        """
        :param name:
        :param parent_key: 父级key
        :param data_key: 数据key
        :param title: 图题
        :param data: 数据,示例：[{"id": "INB133001", "config": {"label": "感知设备与服务", "value": "value1", "depth": 2}, "parent_id": "INB1330"},
                                {"id": "INB1330", "config": {"label": "感知设备", "value": "value2", "depth": 1}, "parent_id": None}]
        :return:
        """
        data = copy.copy(data)
        data_list = []
        link_list = []
        data_map = {item.get(data_key): item for item in data if item.get(data_key)}
        tmp = dict()
        for item in data:
            tmp.setdefault(item.get(parent_key), []).append(item)
        for parent_id, children in tmp.items():
            if parent_id:
                for child in children:
                    link_info = {"source": data_map.get(parent_id, {}).get(data_key), "target": child.get(data_key)}
                    value = child.get("config", {}).get("value")
                    if value is not None:
                        link_info.update({"value": value})
                    link_list.append(link_info)
        for item in data:
            name = item.pop(data_key)
            config = item.pop("config", {})
            info = {
                "name": name
            }
            if config:
                info.update(config)
            data_list.append(info)
        result = {
            "chart_type": "sankey",
            "title": title,
            "series": [
                {
                    "name": name,
                    "data": data_list,
                    "links": link_list
                }
            ]
        }
        if kwargs:
            result["pool"] = kwargs

        return result

"""
矩形树图、旭日图
"""
import importlib


class RectChart:
    @staticmethod
    def render_rect_chart(data: list, key: str, parent_key: str, unit: str, name: str = "", title="", **kwargs):
        """

        :param title:
        :param data: 父子关系的数据字典，需要包含父子关系的字段
        :param key: 子key
        :param parent_key: 父key
        :param unit: 单位
        :param name: 名字
        :return:
        """
        try:
            common_utils = importlib.import_module("lesscode_utils.common_utils")
        except ImportError:
            raise Exception(f"lesscode_utils is not exist,run:pip install lesscode_utils")
        _data = common_utils.find_child(data, key=key, parent_key=parent_key)
        result = {
            "chart_type": "rect",
            "title": title,
            "series": {
                "name": name,
                "data": _data,
                "unit": unit
            }
        }
        if kwargs:
            result["pool"] = kwargs
        return result

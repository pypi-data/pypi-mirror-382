import copy
from collections import OrderedDict
from copy import deepcopy
from typing import List, Union

"""
柱状图/直方图/折线图
"""


class HistogramChart:
    @staticmethod
    def format_data(data, data_key="", name_key="", unit="", name="", default="", value_func=None,
                    chart_type: str = "bar", **kwargs):
        return {"data": data, "data_key": data_key, "name_key": name_key, "unit": unit,
                "name": name,
                "default": default, "value_func": value_func, "type": chart_type, **kwargs}

    @staticmethod
    def list2single_histogram(data: List[dict], title: str = "", unit: str = "",
                              x_name: str = "", y_name: str = "", x_key="key", y_key="value", chart_type="bar",
                              way=None, **kwargs):
        """
        单柱状图
        :param chart_type: bar：柱 line：线
        :param way: 扩展属性
        :param y_key:
        :param x_key:
        :param data: 数据，示例：[{"key":"2020","value":10}]
        :param title: 图题
        :param unit: 数据单位
        :param x_name: x轴名称
        :param y_name: y轴名称
        :param kwargs: 额外数据，放在pool里
        :return:
        """
        x = []
        y = []
        data = copy.copy(data)
        for item in data:
            x.append(item.get(x_key))
            y.append(item.get(y_key))
        result = {
            "chart_type": "histogram",
            "xName": x_name,
            "yName": y_name,
            "title": title,
            "x": x,
            "series": [
                {
                    "name": title,
                    "data": y,
                    "unit": unit,
                    "index": 0,
                    "isType": "1" if chart_type == "line" else "0",
                    "type": chart_type,
                    "way": way
                }
            ]
        }
        if kwargs:
            result["pool"] = kwargs

        return result

    @staticmethod
    def list2more_histogram(data: List[dict], title: str = "", unit: str = "",
                            x_name: str = "", y_name: str = "", x_key="key", y_key="value", chart_type="bar",
                            way=None, **kwargs):
        """
        多柱状图
        :param way: 扩展属性
        :param chart_type: bar:柱图，line：线图
        :param y_key:
        :param x_key:
        :param data: 数据，示例：[{"key":"2020","value":[10]}]
        :param title: 图题
        :param unit: 数据单位
        :param x_name: x轴名称
        :param y_name: y轴名称
        :param kwargs: 额外数据，放在pool里
        :return:
        """
        x = []
        y = []
        data = copy.copy(data)
        for item in data:
            x.append(item.get(x_key))
            y.append(item.get(y_key))
        result = {
            "chart_type": "histogram",
            "xName": x_name,
            "yName": y_name,
            "title": title,
            "x": x,
            "series": [
                {
                    "name": title,
                    "data": y,
                    "unit": unit,
                    "index": 0,
                    "isType": "1" if chart_type == "line" else "0",
                    "type": chart_type,
                    "way": way
                }
            ]
        }
        if kwargs:
            result["pool"] = kwargs

        return result

    @staticmethod
    def list2histogram(data: List[dict], title: str = "",
                       x_name: str = "", y_name: str = "", x_index: int = None, x_func=None,
                       x_order: Union[bool, type(None)] = None, **kwargs):
        """
        单/多柱状图
        :param x_order: x轴排序方式，False是正序，True是倒序
        :param x_func: x轴处理函数
        :param x_index: 用某个图数据的x轴作为所有数据的x轴
        :param data: [{"data":{"2020":200},"data_key":"","unit":"","name":"","default":""}] 或者
                     [{"data":{"2020":{"count":200}}, "data_key":"value","unit":"","name":"","default":""}] 或者
                     [{"data":[{"year":"2020","value":200}], "data_key":"value","name_key":"year","unit":"","name":"",
                       "default":"","value_func":None}]
        :param title:
        :param x_name:
        :param y_name:
        :param kwargs:
        :return:
        """
        data = copy.copy(data)
        result = {
            "chart_type": "histogram",
            "xName": x_name,
            "yName": y_name,
            "title": title,
            "x": [],
            "series": []
        }
        if data:
            x = []
            if x_index is None:
                for item in data:
                    _data = item.get("data")
                    if _data:
                        if isinstance(_data, dict) or isinstance(_data, OrderedDict):
                            for k in _data.keys():
                                if k not in x:
                                    x.append(k)
                        elif isinstance(_data, list):
                            name_key = item.get("name_key", "name")
                            for _ in _data:
                                k = _.get(name_key)
                                if k not in x:
                                    x.append(k)
            else:
                choose_data = data[x_index].get("data")
                if choose_data:
                    if isinstance(choose_data, dict) or isinstance(choose_data, OrderedDict):
                        x = list(choose_data.keys())
                    elif isinstance(choose_data, list):
                        name_key = data[x_index].get("name_key", "name")
                        x = [_.get(name_key) for _ in choose_data]
            if x_order is not None:
                x = sorted(x, key=lambda _: _, reverse=x_order)
            if x_func:
                x = x_func(x)
            result["x"] = x
            series = []
            for i, _ in enumerate(data):
                tmp = []
                data_key = _.get("data_key")
                unit = _.get("unit")
                name = _.get("name")
                default = _.get("default", 0)
                _data = _.get("data")
                name_key = _.get("name_key", "name")
                value_func = _.get("value_func")
                chart_type = _.get("type", "line")
                _chart_type = "1" if chart_type == "line" else "0"
                way = _.get("way")
                if isinstance(_data, list):
                    _data = {v.get(name_key): v.get(data_key, default) for v in _data}
                if isinstance(_data, dict):
                    for _i in x:
                        _value = _data.get(_i)
                        if isinstance(_value, dict):
                            _value = _value.get(data_key, default)
                        if _value is None:
                            _value = default
                        if value_func:
                            _value = value_func(_value)
                        tmp.append(_value)
                    series.append(
                        {"name": name, "unit": unit, "type": chart_type, "isType": _chart_type, "data": tmp, "index": i,
                         "way": way})
            result["series"] = series
        if kwargs:
            result["pool"] = kwargs

        return result

    @staticmethod
    def bar_chart(data: dict, detail_list: list):
        """
        字典转多柱
        :param data: {"INB1335":{"count":1,"sum":10}}
        :param detail_list: [{"name":"计数","unit":"个","data_key":"count","func":int},
                             {"name":"求和","unit":"万","data_key":"sum","func":lambda x:x/10000}   ]
        :return:
        """
        data = copy.copy(data)
        result = {"x": [], "series": detail_list, "chart_type": "histogram"}
        for detail in detail_list:
            detail["data"] = []
        for k, v in data.items():
            result.get("x").append(k)
            for index, item in enumerate(detail_list):
                data_key_list = item.get("data_key", "count").split("&")
                value: dict = deepcopy(v)
                for data_key in data_key_list:
                    # 若为int，只可能为0，不会在get处报错
                    value = value.get(data_key, 0) if value else 0
                if item.get("func"):
                    func = item.get("func")
                    item["data"].append(func(value))
                else:
                    item["data"].append(value)
        for item in detail_list:
            item.pop("func", None)
            item.pop("data_key", None)
        if not result.get("x"):
            result["series"] = []
        return result

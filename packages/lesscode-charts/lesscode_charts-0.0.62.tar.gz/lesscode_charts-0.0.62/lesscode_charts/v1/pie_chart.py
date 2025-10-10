"""
饼图处理
"""
import copy


class PieChart:
    @staticmethod
    def dict2pie(data: dict, unit: str = "", data_key: str = "count", total: int = None,
                 decimal_place: int = None, title: str = "", other_data_key: str = None, **kwargs):
        """
            @param data: 分组出来的数据 示例1: {"人工智能":{"count":1},"工业制造":{"count":1}} 示例2: {"人工智能":1,"工业制造":1}
            @param title: 图题
            @param unit: 数据单位
            @param data_key: 数据key
            @param total: 总数
            @param decimal_place: 保留小数位   None 表示取整
            @param other_data_key: 保留小数位   None 表示取整
            @return:
        """
        data = copy.copy(data)
        new_data = dict()
        other_data = dict()
        if data_key is not None:
            for key, value in data.items():
                if isinstance(value, dict):
                    new_data.update({key: value.get(data_key)})
                    other_data.update({key: value.get(other_data_key)})
                else:
                    new_data.update({key: value})
        else:
            new_data = data
        if total is None:
            total = sum([_ for _ in new_data.values()])
        if total == 0:
            total = 1
        result = {
            "chart_type": "pie",
            "title": title,
            "series": [
                {
                    "name": title,
                    "data": [
                        {"name": k, "value": v, "unit": unit,
                         "proportion": round(v / total * 100, decimal_place),
                         "other": other_data.get(k)} for k, v in
                        new_data.items()
                    ],
                    "unit": unit,
                }
            ],
        }
        if kwargs:
            result["pool"] = kwargs
        return result

    @staticmethod
    def list2pie(data: list, unit: str = "", name_key: str = "name", data_key: str = "count", total: int = None,
                 decimal_place: int = None, title: str = "", other_data_key: str = None, **kwargs):
        """
            @param data: 分组出来的数据 示例1: [{"name":"人工智能","count":0}]
            @param title: 图题
            @param name_key: 名称key
            @param unit: 数据单位
            @param data_key: 数据key
            @param total: 总数
            @param decimal_place: 保留小数位   None 表示取整
            @param other_data_key: 保留小数位   None 表示取整
            @return:
        """
        data = copy.copy(data)
        if total is None:
            total = sum([_.get(data_key, 0) for _ in data if _.get(data_key, 0)])
        if total == 0:
            total = 1
        result = {
            "chart_type": "pie",
            "title": title,
            "series": [
                {
                    "name": title,
                    "data": [
                        {"name": item.get(name_key, ""), "value": item.get(data_key, 0), "unit": unit,
                         "proportion": round(item.get(data_key, 0) / total * 100, decimal_place),
                         "other": item.get(other_data_key)} for item in data
                    ],
                    "unit": unit,
                }
            ],
        }
        if kwargs:
            result["pool"] = kwargs
        return result

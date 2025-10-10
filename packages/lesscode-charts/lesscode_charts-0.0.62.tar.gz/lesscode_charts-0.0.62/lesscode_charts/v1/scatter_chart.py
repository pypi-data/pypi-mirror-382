"""
散点图
"""


class ScatterChart:
    @staticmethod
    def format_check(data: list):
        for _ in data:
            if not isinstance(_, dict):
                raise Exception("data error")
            else:
                for key in ["name", "value", "unit"]:
                    if key not in _:
                        raise Exception("data error")

    @staticmethod
    def scatter(data: list, x_name: str = "", y_name: str = "", title="", **kwargs):
        """
            {
                xName: '默认 x 轴 / radius 轴名称，可用于放置指标名称或者单位',
                yName: '默认 y 轴 / angle 轴名称，同上',
                series: [
                    {
                        name: '系列名称，data 中数据项为单指标（单值）时也可用于显示指标名称',
                        data: [
                            { name: '点的名称，可不提供', value: [lng, lat, 100]}
                        ],
                        unit: '单位1', // 或者 unit: ['单位'], 单位将无视类目轴，从数值类型维度开始匹配
                    }
                ],
            }
        :return:
        """
        result = {
            "chart_type": "scatter",
            "xName": x_name,
            "yName": y_name,
            "series": data,
            "title": title,
        }
        if kwargs:
            result["pool"] = kwargs
        return result

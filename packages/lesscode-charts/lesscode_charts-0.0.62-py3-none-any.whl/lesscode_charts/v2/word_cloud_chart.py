import copy
from typing import List


class WordCloudChart:
    @staticmethod
    def word_cloud_chart(data: List[dict], title="", **kwargs):
        """
        :param title: 图题
        :param data:[{"name": "气压信号","value": 2},{"name": "织物张力","value": 2}]
        :param kwargs:
        :return:
        """
        data = copy.copy(data)
        total = sum([_.get("value") for _ in data if _.get("value")])
        if total == 0:
            total = 1
        result = {
            "chart_type": "NoCoordinateSystemSingle",
            "title": title,
            "series": [
                {
                    "name": title,
                    "data": [
                        {"name": item.get("name"), "value": item.get("value"),
                         "proportion": round(item.get("value", 0) / total * 100, 2)} for item in data]
                }
            ]
        }
        if kwargs:
            result["pool"] = kwargs

        return result

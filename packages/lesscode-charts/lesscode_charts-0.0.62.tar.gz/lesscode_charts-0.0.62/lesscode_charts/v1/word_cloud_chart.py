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
        result = {
            "title": title,
            "chart_type": "word_cloud",
            "data": data
        }
        if kwargs:
            result["pool"] = kwargs

        return result

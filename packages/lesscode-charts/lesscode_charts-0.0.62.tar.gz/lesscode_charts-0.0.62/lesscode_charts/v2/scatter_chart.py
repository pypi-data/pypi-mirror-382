"""
散点图
"""


class ScatterChart:

    @staticmethod
    def scatter(data: list, title=""):
        """
            {
                series: [
                    {
                        data: [
                            { name: '点的名称，可不提供',
                              value: [lon,lat,100]
                            }
                        ]
                    }
                ],
            }
        :return:
        """
        result = {
            "chart_type": "GeographicCoordinateSystem",
            "series": [{
                "data": data
            }],
            "title": title,
        }
        return result

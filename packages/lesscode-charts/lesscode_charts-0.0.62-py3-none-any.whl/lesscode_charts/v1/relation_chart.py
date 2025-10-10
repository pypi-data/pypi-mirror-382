"""
关系图
"""


class RelationChart:
    @staticmethod
    def relation_chart(data: list, x_name: str = "", y_name: str = "", title="", **kwargs):
        """
        {
            xName: '默认 x 轴 / radius 轴名称，可用于放置指标名称或者单位',
            yName: '默认 y 轴 / angle 轴名称，同上',
            x: ['2022-01-01', '2022-02-01'], // 默认类目轴0数据，x 会自动匹配类目轴0
            y: ['1a', '2a'],
            series: [
                {
                    name: '系列名称，data 中数据项为单指标（单值）时也可用于显示指标名称',
                    // data 单值时
                    data: [
                        { name: '1', value: 2 },
                        { name: '2', value: 3 },
                    ],
                    links: [
                        // value 为保留值，用于力导向图中计算边长度
                        { source: '1', target: '2', value: 10, label: '关系名称' },
                    ],
                    unit: '单位', // 或者 unit: ['单位'], 单位将无视类目轴，从数值类型维度开始匹配
                }
            ],
        }
        :return:
        """
        result = {
            "chart_type": "relation",
            "xName": x_name,
            "yName": y_name,
            "series": data,
        }
        if kwargs:
            result["pool"] = kwargs
        return result

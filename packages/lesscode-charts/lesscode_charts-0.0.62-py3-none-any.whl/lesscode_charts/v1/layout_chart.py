"""
布局图
"""


class LayoutChart:
    @staticmethod
    def layout_chart(data: list, title="", **kwargs):
        """
        样例1:{
            series: [
                {
                    name: '系列名称，data 中数据项为单指标（单值）时也可用于显示指标名称',
                    categories: ['A', 'B', 'C'], // 类目名称
                    data: [
                        { name: '1', value: 1, x: 10, y: 10, category: 0 },
                        { name: '2', value: 2, x: 10, y: 10, category: 1 },
                    ],
                    links: [
                        // value 为保留值，用于力导向图中计算边长度
                        { source: '1', target: '2', value: 10, label: '关系名称' },
                    ],
                    unit: ['单位1', '单位2'], // 或者 unit: ['单位'], 单位将无视类目轴，从数值类型维度开始匹配
                }
            ],
        }
        样例2:
        {
            series: [
                {
                    categories: ['A', 'B', 'C'], // 类目名称
                    name: '系列名称，data 中数据项为单指标（单值）时也可用于显示指标名称',
                    data: [
                        { name: '1', value: 1, category: 0, },
                        { name: '2', value: 2, category: 1 },
                    ],
                    links: [
                        // value 为保留值，用于力导向图中计算边长度
                        { source: '1', target: '2', value: 10 },
                    ],
                    unit: ['单位1', '单位2'], // 或者 unit: ['单位'], 单位将无视类目轴，从数值类型维度开始匹配
                }
            ],
        }
        :return:
        """
        result = {
            "chart_type": "layout",
            "title": title,
            "series": data
        }
        if kwargs:
            result["pool"] = kwargs
        return result

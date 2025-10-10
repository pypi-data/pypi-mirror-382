"""
地图处理
"""


class UnivalentGraphChart:

    # 单值图，适用于饼图，金字塔，词云以及地图色块类图表，地图
    @staticmethod
    def UnivalentGraph(data_list: list, title: str, name: str = "", unit: str = "", **kwargs):
        """
        地图
        :title 图表的标题
        :data_list [{'name': '长沙市', 'unit': '家', 'value': 1115890, 'center_latitude': 28.194089889526367, 'center_longitude': 112.9822769165039}, {'name': '株洲市', 'unit': '家', 'value': 233359, 'center_latitude': 27.835805892944336, 'center_longitude': 113.1517333984375}, {'name': '湘潭市', 'unit': '家', 'value': 144813, 'center_latitude': 27.829729080200195, 'center_longitude': 112.94405364990234}, {'name': '衡阳市', 'unit': '家', 'value': 251853, 'center_latitude': 26.900358200073242, 'center_longitude': 112.60769653320312}, {'name': '邵阳市', 'unit': '家', 'value': 226000, 'center_latitude': 27.237842559814453, 'center_longitude': 111.46923065185547}, {'name': '岳阳市', 'unit': '家', 'value': 255763, 'center_latitude': 29.370290756225586, 'center_longitude': 113.13285827636719}, {'name': '常德市', 'unit': '家', 'value': 284957, 'center_latitude': 29.040224075317383, 'center_longitude': 111.69134521484375}, {'name': '张家界市', 'unit': '家', 'value': 63471, 'center_latitude': 29.12740135192871, 'center_longitude': 110.47991943359375}, {'name': '益阳市', 'unit': '家', 'value': 165542, 'center_latitude': 28.570066452026367, 'center_longitude': 112.35504150390625}, {'name': '郴州市', 'unit': '家', 'value': 180530, 'center_latitude': 25.793588638305664, 'center_longitude': 113.03206634521484}, {'name': '永州市', 'unit': '家', 'value': 188563, 'center_latitude': 26.43451690673828, 'center_longitude': 111.60801696777344}, {'name': '怀化市', 'unit': '家', 'value': 155150, 'center_latitude': 27.550081253051758, 'center_longitude': 109.97824096679688}, {'name': '娄底市', 'unit': '家', 'value': 174220, 'center_latitude': 27.72813606262207, 'center_longitude': 112.00849914550781}, {'name': '湘西土家族苗族自治州', 'unit': '家', 'value': 93309, 'center_latitude': 28.31429672241211, 'center_longitude': 109.73973846435547}]
        :unit 单位
        :return:
        """
        result = {
            "chart_type": "univalent_graph",
            "title": title,
            "series": [
                {
                    "name": name,
                    "data": data_list,
                    "unit": unit,
                }
            ]
        }
        if kwargs:
            result["pool"] = kwargs
        return result

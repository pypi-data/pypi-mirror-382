import importlib
import logging
from typing import List

"""
热力图
"""


class HeatMapChart:
    @staticmethod
    def translate(x, y, method="bd2wgs"):
        """
        GCJ-02 高德坐标 gcj
        BD-09  百度坐标 bd
        WGS-84 GPS坐标 wgs
        :param x: lat
        :param y: lon
        :param method: 转换方法（wgs2gcj、wgs2bd、gcj2wgs、gcj2bd、bd2wgs、bd2gcj）
        :return: 转换结果
        """
        try:
            tf = importlib.import_module("coord_convert.transform")
        except ImportError:
            raise Exception(f"coord-convert is not exist,run:pip install coord-convert==0.2.1")
        try:
            x, y = getattr(tf, method)(float(x), float(y))
        except Exception as e:
            logging.warning(f"坐标转换失败：{str(e)}")
        return float(x), float(y)

    @staticmethod
    def heat_map(data_list: List[dict], date_key="reg_xy", method="wgs2bd", min_samples: int = 1, eps: float = 0.0001):
        """

        :param data_list: 数据，示例：[{"id":1,"name":"北京上奇数字科技有限公司","reg_xy":[0,0]}]
        :param date_key: 坐标所在的字段
        :param method: 转换方法见translate方法
        :param min_samples:构成一个核心点所需的最小邻域样本数（包括该点本身）
        :param eps:邻域的半径。如果一个点的邻域内包含的点数（包括该点本身）大于或等于 min_samples，那么该点被认为是核心点
        :return:
        """
        geo_list = []
        for _ in data_list:
            if date_key in _:
                x, y = HeatMapChart.translate(_[date_key][0], _[date_key][1],
                                              method=method)
                geo_list.append([x, y])
        try:
            cluster = importlib.import_module("sklearn.cluster")
        except ImportError:
            raise Exception(f"sklearn is not exist,run:pip install sklearn==0.0")
        try:
            clustering = cluster.DBSCAN(eps=eps, min_samples=min_samples).fit(geo_list)
        except Exception as e:
            logging.warning(f"数据处理失败：{str(e)}")
            return []
        cluster_count = len(set(clustering.labels_)) - (1 if -1 in clustering.labels_ else 0)
        count_list = [[0, 0.0, 0.0] for _ in range(cluster_count)]
        for i in range(len(clustering.labels_)):
            label = int(clustering.labels_[i])
            if label != -1:
                count_list[label][0] += 1
                count_list[label][1] += geo_list[i][0]
                count_list[label][2] += geo_list[i][1]
        result_list = []
        for item in count_list:
            if item[0]:
                insert_dict = {
                    "value": [item[1] / item[0], item[2] / item[0], item[0]],
                }
            else:
                insert_dict = {
                    "value": [0, 0, 0],
                }
            result_list.append(insert_dict)
        return result_list

    @staticmethod
    def new_heat_map(data_list: List[dict], date_key="reg_xy", title="", method="wgs2bd", min_samples: int = 1,
                     eps: float = 0.0001, **kwargs):
        result = {
            "title": title,
            "chart_type": "heat_map",
            "data": HeatMapChart.heat_map(data_list, date_key=date_key, method=method, min_samples=min_samples,
                                          eps=eps),
        }
        if kwargs:
            result["pool"] = kwargs

        return result

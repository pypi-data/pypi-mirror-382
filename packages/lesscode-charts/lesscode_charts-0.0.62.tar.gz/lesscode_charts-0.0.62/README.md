# lesscode_charts

lesscode_charts是数据图标转换工具



## 森林或者树图
```json
{
  "title": "",
  "chart_type": "forest",
  "series": [],
  "pool": {}
}
```

## 热力图
```json
{
  "title": "",
  "chart_type": "heat_map",
  "data": [],
  "pool": {}
}
```

## 柱状图/直方图/折线图
```json
{
  "chart_type": "histogram",
  "xName": "",
  "yName": "",
  "title": "",
  "x": [],
  "series": [],
  "pool": {}
}
```

## K线图
```json
{
  "chart_type": "k_line",
  "xName": "",
  "yName": "",
  "title": "",
  "x": "",
  "y": "",
  "series": [
    {
      "name": "",
      "data": [],
      "unit": ""
    }
  ],
  "pool": {}
}
```

## 布局图
```json
{
  "chart_type": "layout",
  "title": "",
  "series": [],
  "pool": {}
}
```

## 列表
```json
{
  "chart_type": "list",
  "title": "",
  "columns": [],
  "data": [],
  "total": 0,
  "count": 0,
  "pool": {}
}
```

## 饼图
```json
{
  "chart_type": "pie",
  "title": "",
  "series": [
    {
      "name": "",
      "data": [
        {
          "name": "",
          "value": 0,
          "unit": "",
          "proportion": 0,
          "other": ""
        }
      ],
      "unit": ""
    }
  ],
  "pool": {}
}
```

## 金字塔
```json
{
  "chart_type": "pyramid",
  "title": "",
  "series": [
    {
      "name": "",
      "data": [
        {
          "name": "",
          "value": 1,
          "proportion": 0
        }
      ],
      "unit": ""
    }
  ],
  "pool": {}
}
```

## 雷达图
```json
{
  "chart_type": "radar",
  "indicator": [],
  "series": [
    {
      "name": "",
      "data": [
        {
          "name": "",
          "value": 1
        }
      ],
      "unit": ""
    }
  ],
  "title": "",
  "pool": {}
}
```

## 矩形树图、旭日图
```json
{
  "chart_type": "rect",
  "title": "",
  "series": {
    "name": "",
    "data": [],
    "unit": ""
  },
  "pool": {}
}
```

## 关系图
```json
{
  "chart_type": "relation",
  "xName": "",
  "yName": "",
  "series": [],
  "pool": {}
}
```

## 桑基图
```json
{
  "chart_type": "sankey",
  "title": "",
  "series": [
    {
      "name": "",
      "data": [],
      "links": []
    }
  ],
  "pool": {}
}
```

## 散点图
```json
{
  "chart_type": "scatter",
  "xName": "",
  "yName": "",
  "series": [
    {
      "name": "系列名称，data 中数据项为单指标（单值）时也可用于显示指标名称",
      "data": [
        {
          "name": "点的名称，可不提供",
          "value": [
            1,
            1,
            100
          ]
        }
      ],
      "unit": "单位1"
    }
  ],
  "title": "",
  "pool": {}
}
```

## 表格
```json
{
  "chart_type": "table",
  "title": "",
  "columns": [
    {
      "title": "",
      "dataIndex": "",
      "key": ""
    }
  ],
  "dataSource": [],
  "total": 0,
  "count": 0,
  "auth_count": 0,
  "pool": {}
}
```

## 地图
```json
{
  "chart_type": "univalent_graph",
  "title": "",
  "series": [
    {
      "name": "",
      "data": [],
      "unit": ""
    }
  ],
  "pool": {}
}
```

## 词云
```json
{
  "title": "",
  "chart_type": "word_cloud",
  "data": [
    {
      "name": "气压信号",
      "value": 2
    },
    {
      "name": "织物张力",
      "value": 2
    }
  ]
}
```
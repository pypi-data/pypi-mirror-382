"""
数据处理辅助功能模块
提供数据处理相关的辅助函数
"""

import logging

logger = logging.getLogger(__name__)


def get_indicator_unit(indicator, config=None):
    """
    根据指标名称获取单位

    Args:
        indicator: 指标名称
        config: 配置字典，包含指标单位信息

    Returns:
        指标单位字符串
    """
    # 常见指标单位映射表
    default_units = {
        "Turb": "NTU",
        "SS": "mg/L",
        "Chla": "μg/L",
        "DO": "mg/L",
        "pH": "",
        "Temp": "°C",
        "EC": "μS/cm",
        "COD": "mg/L",
        "CODMn": "mg/L",
        "BOD": "mg/L",
        "NH3-N": "mg/L",
        "TN": "mg/L",
        "TP": "mg/L",
        "BGA": "%",
        "Chroma": "Hazen",
        "SD": "cm"
    }

    # 从配置中读取单位信息
    if (
        config
        and "indicators" in config
        and indicator in config["indicators"]
        and "unit" in config["indicators"][indicator]
    ):
        return config["indicators"][indicator]["unit"]

    # 如果配置中没有，使用默认单位
    return default_units.get(indicator, "")

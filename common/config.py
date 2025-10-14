# coding:utf-8
"""
配置管理模块
"""
from qfluentwidgets import QConfig, ConfigItem, OptionsConfigItem, BoolValidator, OptionsValidator, RangeValidator
from enum import Enum

class Theme(Enum):
    """主题枚举"""
    LIGHT = "Light"
    DARK = "Dark"
    AUTO = "Auto"

class Config(QConfig):
    """应用配置类"""
    
    # 应用设置
    micaEnabled = ConfigItem("General", "MicaEnabled", True, BoolValidator())
    language = OptionsConfigItem("General", "Language", "zh_CN", OptionsValidator(["zh_CN", "en_US"]))
    theme = OptionsConfigItem("General", "Theme", Theme.AUTO.value, OptionsValidator([t.value for t in Theme]))
    
    # 数据库配置
    sqlHost = ConfigItem("Database", "Host", "127.0.0.1")
    sqlPort = ConfigItem("Database", "Port", "1433")
    sqlUser = ConfigItem("Database", "User", "sa")
    sqlPassword = ConfigItem("Database", "Password", "123")
    brokenDbName = ConfigItem("Database", "BrokenDbName", "broken")
    originDbName = ConfigItem("Database", "OriginDbName", "origin")
    spareDbName = ConfigItem("Database", "SpareDbName", "origin1")
    
    # 文件路径配置
    brokenSavePath = ConfigItem("FilePaths", "BrokenSavePath", ".\\broken")
    originSavePath = ConfigItem("FilePaths", "OriginSavePath", ".\\origin")
    repairSavePath = ConfigItem("FilePaths", "RepairSavePath", ".\\repaired")
    spareSavePath = ConfigItem("FilePaths", "SpareSavePath", ".\\origin1")
    brokenLogicPath = ConfigItem("FilePaths", "BrokenLogicPath", ".\\broken\\data")
    originLogicPath = ConfigItem("FilePaths", "OriginLogicPath", ".\\origin\\data")
    spareLogicPath = ConfigItem("FilePaths", "SpareLogicPath", ".\\origin1\\data")
    
    # 其他配置
    repairMode = OptionsConfigItem("Other", "RepairMode", 0, OptionsValidator([0, 1]))
    dataClearMode = OptionsConfigItem("Other", "DataClearMode", 1, OptionsValidator([0, 1]))
    autoUpdate = OptionsConfigItem("Other", "AutoUpdate", 0, OptionsValidator([0, 1]))

# 创建全局配置实例
cfg = Config()
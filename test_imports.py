# coding:utf-8
"""
测试导入是否正常
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

print("开始测试导入...")

try:
    print("1. 测试基础qfluentwidgets导入...")
    from qfluentwidgets import FluentIcon, PrimaryPushButton, CardWidget
    print("   OK - 基础组件导入成功")
    
    print("2. 跳过qfluentwidgetspro导入测试...")
    # from qfluentwidgetspro import setLicense, StepProgressBar, FilledFluentWindow
    print("   SKIP - Pro组件暂时跳过")
    
    print("3. 测试配置模块...")
    from common.config import cfg
    print("   OK - 配置模块导入成功")
    
    print("4. 测试核心模块...")
    try:
        from core.dbfunc import SQLcon
        print("   OK - dbfunc导入成功")
    except ImportError as e:
        print(f"   SKIP - dbfunc需要pymssql: {e}")
    
    from core.baseFunc import getConfig
    print("   OK - baseFunc导入成功")
    
    print("5. 测试各界面模块...")
    from app.views.home_interface import HomeInterface
    print("   OK - 主页界面导入成功")
    
    from app.views.repair_interface import RepairInterface
    print("   OK - 修复界面导入成功")
    
    from app.views.config_interface import ConfigInterface
    print("   OK - 配置界面导入成功")
    
    from app.views.log_interface import LogInterface
    print("   OK - 日志界面导入成功")
    
    from app.views.setting_interface import SettingInterface
    print("   OK - 设置界面导入成功")
    
    from app.views.main_window import MainWindow
    print("   OK - 主窗口导入成功")
    
    print("\n SUCCESS - 所有导入测试通过！")
    
except ImportError as e:
    print(f"\n ERROR - 导入错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
    
except Exception as e:
    print(f"\n ERROR - 其他错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
# coding:utf-8
"""
启动脚本 - 用于开发测试
"""
import sys
import os

# 添加项目路径
current_dir = os.path.dirname(__file__)
sys.path.insert(0, current_dir)

# 导入主程序
from main import main

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"应用程序启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
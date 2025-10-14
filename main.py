# coding:utf-8
import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

# 添加项目路径到Python路径
sys.path.append(os.path.dirname(__file__))

from app.views.main_window import MainWindow
from common.config import cfg
# from qfluentwidgetspro import setLicense, ProTranslator
# 暂时注释掉pro功能

def main():
    """主函数"""
    # 设置高DPI支持
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 创建应用程序
    app = QApplication(sys.argv)
    
    # 设置许可证 (暂时注释掉)
    # setLicense('...')
    
    # 安装翻译器 (暂时注释掉)
    # translator = ProTranslator()
    # app.installTranslator(translator)
    
    # 设置应用信息
    app.setOrganizationName("TplusDBMend")
    app.setOrganizationDomain("tplus.dbmend")
    app.setApplicationName("T+数据库修复工具")
    app.setApplicationVersion("3.0")
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
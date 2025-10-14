# coding:utf-8
"""
主窗口模块
"""
import sys
import os
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget

from qfluentwidgets import (NavigationItemPosition, FluentIcon as FIF, 
                           SplashScreen, setTheme, Theme, FluentWindow)

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from common.config import cfg
from .home_interface import HomeInterface
from .repair_interface import RepairInterface
from .config_interface import ConfigInterface
from .log_interface import LogInterface


class MainWindow(FluentWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.initWindow()
        self.initInterfaces()
        self.initNavigation()
        
        # 显示启动画面
        self.splashScreen.finish()
    
    def initWindow(self):
        """初始化窗口"""
        self.resize(1200, 800)
        self.setMinimumSize(900, 600)
        self.setWindowTitle('T+数据库修复工具 v3.0')
        
        # 设置窗口图标
        if os.path.exists('./resources/icon/logo.png'):
            self.setWindowIcon(QIcon('./resources/icon/logo.png'))
        
        # 设置主题
        # setTheme(Theme.LIGHT)
        
        # 创建启动画面
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(102, 102))
        self.splashScreen.raise_()
        
        # 居中显示
        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        
        self.show()
        QApplication.processEvents()
    
    def initInterfaces(self):
        """初始化界面"""
        self.homeInterface = HomeInterface(self)
        self.repairInterface = RepairInterface(self)
        self.configInterface = ConfigInterface(self)
        self.logInterface = LogInterface(self)
    
    def initNavigation(self):
        """初始化导航栏"""
        # 主要功能区域
        self.addSubInterface(
            self.homeInterface, 
            FIF.HOME, 
            '主页'
        )
        
        self.addSubInterface(
            self.repairInterface, 
            FIF.DEVELOPER_TOOLS, 
            '数据修复'
        )
        
        self.addSubInterface(
            self.configInterface, 
            FIF.SETTING, 
            '配置管理'
        )
        
        self.addSubInterface(
            self.logInterface, 
            FIF.DOCUMENT, 
            '日志查看'
        )
        
        
        # 设置默认界面
        self.switchToSample(self.homeInterface)
    
    def switchToSample(self, interface):
        """切换到指定界面"""
        self.stackedWidget.setCurrentWidget(interface)
    
    def resizeEvent(self, e):
        """重写窗口大小改变事件"""
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())
    
    def closeEvent(self, e):
        """重写窗口关闭事件"""
        # 清理InfoBar管理器，避免析构错误
        try:
            from qfluentwidgets import InfoBarManager
            InfoBarManager.clear()
        except:
            pass
        
        # 停止所有正在运行的线程
        if hasattr(self, 'configInterface') and hasattr(self.configInterface, 'testThread'):
            if self.configInterface.testThread and self.configInterface.testThread.isRunning():
                self.configInterface.testThread.quit()
                self.configInterface.testThread.wait()
        
        if hasattr(self, 'repairInterface'):
            # 停止修复线程
            if hasattr(self.repairInterface, 'repairThread'):
                if self.repairInterface.repairThread and self.repairInterface.repairThread.isRunning():
                    self.repairInterface.repairThread.quit()
                    self.repairInterface.repairThread.wait()
        
        super().closeEvent(e)
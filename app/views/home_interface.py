# coding:utf-8
"""
主页界面模块
"""
import sys
import os
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from qfluentwidgets import (ScrollArea, PrimaryPushButton, PushButton, 
                           TitleLabel, SubtitleLabel, BodyLabel, CardWidget,
                           FluentIcon as FIF, InfoBar, InfoBarPosition)

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from common.config import cfg


class WelcomeCard(CardWidget):
    """欢迎卡片"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 200)
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # 标题
        titleLabel = TitleLabel("欢迎使用 T+数据库修复工具", self)
        titleLabel.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        
        # 描述
        descLabel = BodyLabel("专业的T+系列产品数据库修复解决方案", self)
        descLabel.setWordWrap(True)
        
        # 版本信息
        versionLabel = BodyLabel("版本: 3.0.0 (基于qfluentwidgets重构)", self)
        versionLabel.setStyleSheet("color: #666666")
        
        layout.addWidget(titleLabel)
        layout.addWidget(descLabel)
        layout.addStretch()
        layout.addWidget(versionLabel)


class QuickActionCard(CardWidget):
    """快速操作卡片"""
    
    # 信号
    repairClicked = pyqtSignal()
    configClicked = pyqtSignal()
    logClicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 200)
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # 标题
        titleLabel = SubtitleLabel("快速操作", self)
        titleLabel.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        
        # 按钮
        self.repairBtn = PrimaryPushButton(FIF.DEVELOPER_TOOLS, "开始修复", self)
        self.repairBtn.setFixedSize(200, 36)
        
        self.configBtn = PushButton(FIF.SETTING, "配置管理", self)
        self.configBtn.setFixedSize(200, 36)
        
        self.logBtn = PushButton(FIF.DOCUMENT, "查看日志", self)
        self.logBtn.setFixedSize(200, 36)
        
        # 连接信号
        self.repairBtn.clicked.connect(self.repairClicked.emit)
        self.configBtn.clicked.connect(self.configClicked.emit)
        self.logBtn.clicked.connect(self.logClicked.emit)
        
        layout.addWidget(titleLabel)
        layout.addWidget(self.repairBtn)
        layout.addWidget(self.configBtn)
        layout.addWidget(self.logBtn)
        layout.addStretch()


class StatusCard(CardWidget):
    """状态信息卡片"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(350, 200)
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # 标题
        titleLabel = SubtitleLabel("系统状态", self)
        titleLabel.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        
        # 状态信息
        self.dbStatusLabel = BodyLabel("数据库连接: 未测试", self)
        self.configStatusLabel = BodyLabel("配置状态: 正常", self)
        self.lastRepairLabel = BodyLabel("上次修复: 无记录", self)
        
        layout.addWidget(titleLabel)
        layout.addWidget(self.dbStatusLabel)
        layout.addWidget(self.configStatusLabel)
        layout.addWidget(self.lastRepairLabel)
        layout.addStretch()
    
    def updateDatabaseStatus(self, connected: bool):
        """更新数据库连接状态"""
        status = "已连接" if connected else "连接失败"
        self.dbStatusLabel.setText(f"数据库连接: {status}")


class HomeInterface(ScrollArea):
    """主页界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('HomeInterface')
        
        # 创建主部件
        self.scrollWidget = QWidget()
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        
        # 设置样式
        self.setStyleSheet("HomeInterface { background-color: transparent; border: none; }")
        
        self.initUI()
        
    def initUI(self):
        """初始化界面"""
        # 主布局
        mainLayout = QVBoxLayout(self.scrollWidget)
        mainLayout.setSpacing(24)
        mainLayout.setContentsMargins(36, 36, 36, 36)
        
        # 页面标题
        titleLabel = TitleLabel("主页", self.scrollWidget)
        titleLabel.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))
        mainLayout.addWidget(titleLabel)
        
        # 卡片容器布局
        cardsLayout = QHBoxLayout()
        cardsLayout.setSpacing(24)
        
        # 创建卡片
        self.welcomeCard = WelcomeCard(self.scrollWidget)
        self.quickActionCard = QuickActionCard(self.scrollWidget)
        self.statusCard = StatusCard(self.scrollWidget)
        
        # 连接信号
        self.quickActionCard.repairClicked.connect(self._onRepairClicked)
        self.quickActionCard.configClicked.connect(self._onConfigClicked)
        self.quickActionCard.logClicked.connect(self._onLogClicked)
        
        cardsLayout.addWidget(self.welcomeCard)
        cardsLayout.addWidget(self.quickActionCard)
        cardsLayout.addWidget(self.statusCard)
        cardsLayout.addStretch()
        
        mainLayout.addLayout(cardsLayout)
        mainLayout.addStretch()
        
        # 显示欢迎信息
        self._showWelcomeMessage()
    
    def _showWelcomeMessage(self):
        """显示欢迎消息"""
        InfoBar.success(
            title="欢迎！",
            content="T+数据库修复工具已成功启动",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )
    
    def _onRepairClicked(self):
        """修复按钮点击"""
        # 获取主窗口并切换到修复界面
        main_window = self.window()
        if hasattr(main_window, 'repairInterface'):
            main_window.switchToSample(main_window.repairInterface)
    
    def _onConfigClicked(self):
        """配置按钮点击"""
        # 获取主窗口并切换到配置界面
        main_window = self.window()
        if hasattr(main_window, 'configInterface'):
            main_window.switchToSample(main_window.configInterface)
    
    def _onLogClicked(self):
        """日志按钮点击"""
        # 获取主窗口并切换到日志界面
        main_window = self.window()
        if hasattr(main_window, 'logInterface'):
            main_window.switchToSample(main_window.logInterface)
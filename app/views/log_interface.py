# coding:utf-8
"""
日志查看界面模块
"""
import sys
import os
from datetime import datetime
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from qfluentwidgets import (ScrollArea, TitleLabel, SubtitleLabel, 
                           PushButton, ComboBox, LineEdit, TextEdit,
                           CardWidget, InfoBar, InfoBarPosition,
                           FluentIcon as FIF)

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from common.config import cfg


class LogViewerCard(CardWidget):
    """日志查看器卡片"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.loadSampleLogs()
    
    def initUI(self):
        """初始化界面"""
        self.setMinimumHeight(400)
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 20, 24, 20)
        
        # 控制区域
        controlLayout = QHBoxLayout()
        
        # 日志级别过滤
        self.levelCombo = ComboBox(self)
        self.levelCombo.addItems(["全部", "DEBUG", "INFO", "WARNING", "ERROR"])
        self.levelCombo.setCurrentText("全部")
        self.levelCombo.currentTextChanged.connect(self._onFilterChanged)
        
        # 搜索框
        self.searchEdit = LineEdit(self)
        self.searchEdit.setPlaceholderText("搜索日志内容...")
        self.searchEdit.textChanged.connect(self._onFilterChanged)
        
        # 刷新按钮
        self.refreshBtn = PushButton(FIF.SYNC, "刷新", self)
        self.refreshBtn.clicked.connect(self._onRefresh)
        
        # 清空按钮
        self.clearBtn = PushButton(FIF.DELETE, "清空", self)
        self.clearBtn.clicked.connect(self._onClear)
        
        controlLayout.addWidget(SubtitleLabel("级别:", self))
        controlLayout.addWidget(self.levelCombo)
        controlLayout.addWidget(SubtitleLabel("搜索:", self))
        controlLayout.addWidget(self.searchEdit, 1)
        controlLayout.addWidget(self.refreshBtn)
        controlLayout.addWidget(self.clearBtn)
        
        # 日志显示区域
        self.logTextEdit = TextEdit(self)
        self.logTextEdit.setReadOnly(True)
        self.logTextEdit.setFont(QFont("Consolas", 9))
        
        layout.addLayout(controlLayout)
        layout.addWidget(self.logTextEdit, 1)
    
    def loadSampleLogs(self):
        """加载示例日志"""
        sample_logs = [
            "2024-01-15 10:30:15 - INFO - 应用程序启动成功",
            "2024-01-15 10:30:16 - INFO - 配置文件加载完成",
            "2024-01-15 10:30:17 - DEBUG - 初始化数据库连接池",
            "2024-01-15 10:30:18 - INFO - UI界面初始化完成",
            "2024-01-15 10:32:45 - INFO - 用户开始数据修复操作",
            "2024-01-15 10:32:46 - INFO - 开始读取配置",
            "2024-01-15 10:32:47 - DEBUG - 数据库配置校验通过",
            "2024-01-15 10:32:48 - INFO - 开始解压数据",
            "2024-01-15 10:32:49 - INFO - 解压成功",
            "2024-01-15 10:32:50 - INFO - 开始比对版本",
            "2024-01-15 10:32:51 - INFO - 版本比对通过",
            "2024-01-15 10:32:52 - INFO - 开始恢复数据库",
            "2024-01-15 10:32:55 - INFO - 恢复成功",
            "2024-01-15 10:32:56 - INFO - 开始检测损坏表名",
            "2024-01-15 10:32:57 - WARNING - 检测到损坏的表: Table_1, Table_2",
            "2024-01-15 10:32:58 - INFO - 用户选择继续修复",
            "2024-01-15 10:33:01 - INFO - 空账解体成功",
            "2024-01-15 10:33:05 - INFO - 导入数据成功",
            "2024-01-15 10:33:08 - INFO - 重建表结构成功",
            "2024-01-15 10:33:10 - INFO - 重建账套成功",
            "2024-01-15 10:33:11 - INFO - 清理数据成功",
            "2024-01-15 10:33:12 - INFO - 修复完成！",
        ]
        
        self.allLogs = sample_logs
        self.displayLogs()
    
    def displayLogs(self):
        """显示日志"""
        filtered_logs = self._filterLogs()
        self.logTextEdit.setPlainText("\n".join(filtered_logs))
        
        # 滚动到底部
        cursor = self.logTextEdit.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.logTextEdit.setTextCursor(cursor)
    
    def _filterLogs(self):
        """过滤日志"""
        level_filter = self.levelCombo.currentText()
        search_text = self.searchEdit.text().lower()
        
        filtered = []
        for log in self.allLogs:
            # 级别过滤
            if level_filter != "全部" and level_filter not in log:
                continue
            
            # 搜索过滤
            if search_text and search_text not in log.lower():
                continue
            
            filtered.append(log)
        
        return filtered
    
    def _onFilterChanged(self):
        """过滤条件改变"""
        self.displayLogs()
    
    def _onRefresh(self):
        """刷新日志"""
        # 这里应该重新读取日志文件
        # 现在只是添加一条新日志演示
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_log = f"{current_time} - INFO - 日志已刷新"
        self.allLogs.append(new_log)
        self.displayLogs()
        
        InfoBar.success(
            title="刷新完成",
            content="日志已更新",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=1500,
            parent=self.parent()
        )
    
    def _onClear(self):
        """清空日志"""
        self.allLogs.clear()
        self.logTextEdit.clear()
        
        InfoBar.info(
            title="清空完成",
            content="日志已清空",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=1500,
            parent=self.parent()
        )


class LogStatsCard(CardWidget):
    """日志统计卡片"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        """初始化界面"""
        self.setFixedHeight(120)
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 20, 24, 20)
        
        # 标题
        titleLabel = SubtitleLabel("日志统计", self)
        
        # 统计信息
        statsLayout = QHBoxLayout()
        
        self.totalLabel = SubtitleLabel("总计: 22", self)
        self.infoLabel = SubtitleLabel("信息: 18", self)
        self.infoLabel.setStyleSheet("color: #0078D4")
        
        self.warningLabel = SubtitleLabel("警告: 1", self)
        self.warningLabel.setStyleSheet("color: #FF8C00")
        
        self.errorLabel = SubtitleLabel("错误: 0", self)
        self.errorLabel.setStyleSheet("color: #D13438")
        
        statsLayout.addWidget(self.totalLabel)
        statsLayout.addWidget(self.infoLabel)
        statsLayout.addWidget(self.warningLabel)
        statsLayout.addWidget(self.errorLabel)
        statsLayout.addStretch()
        
        layout.addWidget(titleLabel)
        layout.addLayout(statsLayout)


class LogInterface(ScrollArea):
    """日志查看界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('LogInterface')
        
        # 创建主部件
        self.scrollWidget = QWidget()
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        
        # 设置样式
        self.setStyleSheet("LogInterface { background-color: transparent; border: none; }")
        
        self.initUI()
        self._setupTimer()
    
    def initUI(self):
        """初始化界面"""
        # 主布局
        mainLayout = QVBoxLayout(self.scrollWidget)
        mainLayout.setSpacing(24)
        mainLayout.setContentsMargins(36, 36, 36, 36)
        
        # 页面标题
        titleLabel = TitleLabel("日志查看", self.scrollWidget)
        titleLabel.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))
        mainLayout.addWidget(titleLabel)
        
        # 统计卡片
        self.statsCard = LogStatsCard(self.scrollWidget)
        mainLayout.addWidget(self.statsCard)
        
        # 日志查看器
        self.logViewerCard = LogViewerCard(self.scrollWidget)
        mainLayout.addWidget(self.logViewerCard, 1)
    
    def _setupTimer(self):
        """设置定时器自动刷新"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._autoRefresh)
        self.timer.start(30000)  # 30秒自动刷新一次
    
    def _autoRefresh(self):
        """自动刷新"""
        # 这里可以实现自动读取新的日志内容
        pass
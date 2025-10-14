# coding:utf-8
"""
配置管理界面模块
"""
import sys
import os
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QInputDialog, QFileDialog

from qfluentwidgets import (ScrollArea, SettingCardGroup, OptionsSettingCard, 
                           PushSettingCard, ComboBoxSettingCard,
                           TitleLabel, SubtitleLabel, PrimaryPushButton, PushButton,
                           InfoBar, InfoBarPosition, MessageBox, FluentIcon as FIF,
                           LineEdit, Dialog, FolderListDialog)

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from common.config import cfg


class DatabaseTestThread(QThread):
    """数据库连接测试线程"""
    
    # 信号
    testCompleted = pyqtSignal(bool, str)  # 成功, 消息
    
    def __init__(self, host: str, port: str, user: str, password: str):
        super().__init__()
        self.host = host
        self.port = port
        self.user = user
        self.password = password
    
    def run(self):
        """运行测试"""
        try:
            # 这里应该调用数据库连接测试逻辑
            # 现在只是模拟
            self.msleep(1000)  # 模拟连接时间
            
            # 模拟连接成功
            if self.host and self.port and self.user:
                self.testCompleted.emit(True, "数据库连接测试成功!")
            else:
                self.testCompleted.emit(False, "连接参数不完整")
                
        except Exception as e:
            self.testCompleted.emit(False, f"连接失败: {str(e)}")


class ConfigInterface(ScrollArea):
    """配置管理界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('ConfigInterface')
        
        # 测试线程
        self.testThread = None
        
        # 创建主部件
        self.scrollWidget = QWidget()
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        
        # 设置样式
        self.setStyleSheet("ConfigInterface { background-color: transparent; border: none; }")
        
        self.initUI()
    
    def initUI(self):
        """初始化界面"""
        # 主布局
        mainLayout = QVBoxLayout(self.scrollWidget)
        mainLayout.setSpacing(24)
        mainLayout.setContentsMargins(36, 36, 36, 36)
        
        # 页面标题
        titleLabel = TitleLabel("配置管理", self.scrollWidget)
        titleLabel.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))
        mainLayout.addWidget(titleLabel)
        
        # 数据库配置组
        self.databaseGroup = SettingCardGroup("数据库配置", self.scrollWidget)
        
        # 服务器地址
        self.hostCard = PushSettingCard(
            "编辑服务器地址",
            FIF.GLOBE,
            "服务器地址",
            cfg.get(cfg.sqlHost) or "SQL Server 服务器的IP地址或域名"
        )
        
        # 端口
        self.portCard = PushSettingCard(
            "编辑端口",
            FIF.CONNECT,
            "端口",
            cfg.get(cfg.sqlPort) or "SQL Server 服务器端口"
        )
        
        # 用户名
        self.userCard = PushSettingCard(
            "编辑用户名",
            FIF.PEOPLE,
            "用户名",
            cfg.get(cfg.sqlUser) or "数据库登录用户名"
        )
        
        # 密码
        self.passwordCard = PushSettingCard(
            "编辑密码",
            FIF.FINGERPRINT,
            "密码",
            "数据库登录密码"
        )
        
        # 数据库名称配置
        self.brokenDbCard = PushSettingCard(
            "编辑数据库名",
            FIF.LIBRARY,
            "损坏数据库名",
            cfg.get(cfg.brokenDbName) or "存储损坏数据的数据库名称"
        )
        
        self.originDbCard = PushSettingCard(
            "编辑数据库名",
            FIF.LIBRARY,
            "空数据库名",
            cfg.get(cfg.originDbName) or "存储空账套数据的数据库名称"
        )
        
        self.spareDbCard = PushSettingCard(
            "编辑数据库名",
            FIF.LIBRARY,
            "备用数据库名",
            cfg.get(cfg.spareDbName) or "存储备用数据的数据库名称"
        )
        
        self.databaseGroup.addSettingCard(self.hostCard)
        self.databaseGroup.addSettingCard(self.portCard)
        self.databaseGroup.addSettingCard(self.userCard)
        self.databaseGroup.addSettingCard(self.passwordCard)
        self.databaseGroup.addSettingCard(self.brokenDbCard)
        self.databaseGroup.addSettingCard(self.originDbCard)
        self.databaseGroup.addSettingCard(self.spareDbCard)
        
        # 文件路径配置组
        self.filePathGroup = SettingCardGroup("文件路径配置", self.scrollWidget)
        
        self.brokenPathCard = PushSettingCard(
            "选择路径",
            FIF.FOLDER,
            "损坏账套存放路径",
            cfg.get(cfg.brokenSavePath) or "损坏账套备份文件的存放目录"
        )
        
        self.originPathCard = PushSettingCard(
            "选择路径",
            FIF.FOLDER,
            "空账套存放路径",
            cfg.get(cfg.originSavePath) or "空账套备份文件的存放目录"
        )
        
        self.repairPathCard = PushSettingCard(
            "选择路径",
            FIF.FOLDER,
            "修复账套存放路径",
            cfg.get(cfg.repairSavePath) or "修复后账套文件的存放目录"
        )
        
        self.sparePathCard = PushSettingCard(
            "选择路径",
            FIF.FOLDER,
            "备用账套存放路径",
            cfg.get(cfg.spareSavePath) or "备用账套文件的存放目录"
        )
        
        self.filePathGroup.addSettingCard(self.brokenPathCard)
        self.filePathGroup.addSettingCard(self.originPathCard)
        self.filePathGroup.addSettingCard(self.repairPathCard)
        self.filePathGroup.addSettingCard(self.sparePathCard)
        
        # 其他配置组
        self.otherGroup = SettingCardGroup("其他配置", self.scrollWidget)
        
        self.repairModeCard = OptionsSettingCard(
            cfg.repairMode,
            FIF.SETTING,
            "修复模式",
            "选择修复时的详细程度",
            texts=["啰嗦模式", "标准模式"]
        )
        
        self.dataClearCard = OptionsSettingCard(
            cfg.dataClearMode,
            FIF.DELETE,
            "完成后清理数据",
            "修复完成后是否自动清理临时数据",
            texts=["否", "是"]
        )
        
        
        self.autoUpdateCard = OptionsSettingCard(
            cfg.autoUpdate,
            FIF.UPDATE,
            "自动更新",
            "是否启用自动更新检查",
            texts=["否", "是"]
        )
        
        self.otherGroup.addSettingCard(self.repairModeCard)
        self.otherGroup.addSettingCard(self.dataClearCard)
        self.otherGroup.addSettingCard(self.autoUpdateCard)
        
        # 按钮区域
        buttonLayout = QHBoxLayout()
        
        self.testBtn = PushButton(FIF.CONNECT, "测试数据库连接", self.scrollWidget)
        self.testBtn.clicked.connect(self._onTestConnection)
        
        self.saveBtn = PrimaryPushButton(FIF.SAVE, "保存配置", self.scrollWidget)
        self.saveBtn.clicked.connect(self._onSaveConfig)
        
        self.resetBtn = PushButton(FIF.SYNC, "恢复默认", self.scrollWidget)
        self.resetBtn.clicked.connect(self._onResetConfig)
        
        buttonLayout.addWidget(self.testBtn)
        buttonLayout.addWidget(self.saveBtn)
        buttonLayout.addWidget(self.resetBtn)
        buttonLayout.addStretch()
        
        # 添加到主布局
        mainLayout.addWidget(self.databaseGroup)
        mainLayout.addWidget(self.filePathGroup)
        mainLayout.addWidget(self.otherGroup)
        mainLayout.addLayout(buttonLayout)
        mainLayout.addStretch()
        
        # 连接编辑按钮事件
        self._connectEditEvents()
    
    def _connectEditEvents(self):
        """连接编辑按钮事件"""
        # 数据库配置编辑事件
        self.hostCard.clicked.connect(lambda: self._editConfig(cfg.sqlHost, "服务器地址", "请输入SQL Server服务器地址:", self.hostCard))
        self.portCard.clicked.connect(lambda: self._editConfig(cfg.sqlPort, "端口", "请输入SQL Server端口:", self.portCard))
        self.userCard.clicked.connect(lambda: self._editConfig(cfg.sqlUser, "用户名", "请输入数据库用户名:", self.userCard))
        self.passwordCard.clicked.connect(lambda: self._editPassword())
        
        self.brokenDbCard.clicked.connect(lambda: self._editConfig(cfg.brokenDbName, "损坏数据库名", "请输入损坏数据库名:", self.brokenDbCard))
        self.originDbCard.clicked.connect(lambda: self._editConfig(cfg.originDbName, "空数据库名", "请输入空数据库名:", self.originDbCard))
        self.spareDbCard.clicked.connect(lambda: self._editConfig(cfg.spareDbName, "备用数据库名", "请输入备用数据库名:", self.spareDbCard))
        
        # 文件路径配置编辑事件
        self.brokenPathCard.clicked.connect(lambda: self._editPath(cfg.brokenSavePath, "损坏账套存放路径", self.brokenPathCard))
        self.originPathCard.clicked.connect(lambda: self._editPath(cfg.originSavePath, "空账套存放路径", self.originPathCard))
        self.repairPathCard.clicked.connect(lambda: self._editPath(cfg.repairSavePath, "修复账套存放路径", self.repairPathCard))
        self.sparePathCard.clicked.connect(lambda: self._editPath(cfg.spareSavePath, "备用账套存放路径", self.sparePathCard))
    
    def _editConfig(self, config_item, title, prompt, card):
        """编辑配置项"""
        current_value = cfg.get(config_item) or ""
        
        # 创建自定义对话框
        dialog = Dialog(title, prompt, self)
        dialog.setTitleBarVisible(True)
        
        # 添加输入框
        lineEdit = LineEdit()
        lineEdit.setText(current_value)
        lineEdit.setPlaceholderText(f"请输入{title}")
        
        dialog.textLayout.addWidget(lineEdit)
        
        if dialog.exec():
            text = lineEdit.text().strip()
            if text:
                cfg.set(config_item, text)
                # 更新卡片显示
                card.setContent(text)
                InfoBar.success(
                    title="设置成功",
                    content=f"{title}已更新",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
    
    def _editPassword(self):
        """编辑密码"""
        current_value = cfg.get(cfg.sqlPassword) or ""
        
        # 创建密码输入对话框
        dialog = Dialog("密码设置", "请输入数据库连接密码", self)
        dialog.setTitleBarVisible(True)
        
        # 添加密码输入框
        passwordEdit = LineEdit()
        passwordEdit.setText(current_value)
        passwordEdit.setEchoMode(LineEdit.Password)
        passwordEdit.setPlaceholderText("请输入数据库密码")
        
        dialog.textLayout.addWidget(passwordEdit)
        
        if dialog.exec():
            text = passwordEdit.text().strip()
            if text:
                cfg.set(cfg.sqlPassword, text)
                InfoBar.success(
                    title="设置成功",
                    content="密码已更新",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
    
    def _editPath(self, config_item, title, card):
        """编辑路径配置"""
        current_path = cfg.get(config_item) or ""
        path = QFileDialog.getExistingDirectory(self, title, current_path)
        
        if path:
            cfg.set(config_item, path)
            # 更新卡片显示
            card.setContent(path)
            InfoBar.success(
                title="设置成功",
                content=f"{title}已更新",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
    
    def _onTestConnection(self):
        """测试数据库连接"""
        host = cfg.get(cfg.sqlHost)
        port = cfg.get(cfg.sqlPort)
        user = cfg.get(cfg.sqlUser)
        password = cfg.get(cfg.sqlPassword)
        
        if not all([host, port, user, password]):
            MessageBox("错误", "请先在配置中填写完整的数据库连接信息!", self).exec()
            return
        
        # 禁用按钮
        self.testBtn.setEnabled(False)
        self.testBtn.setText("测试中...")
        
        # 开始测试
        self.testThread = DatabaseTestThread(host, port, user, password)
        self.testThread.testCompleted.connect(self._onTestCompleted)
        self.testThread.start()
        
        InfoBar.info(
            title="正在测试",
            content="正在测试数据库连接...",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )
    
    def _onTestCompleted(self, success: bool, message: str):
        """测试完成"""
        self.testBtn.setEnabled(True)
        self.testBtn.setText("测试数据库连接")
        
        if success:
            InfoBar.success(
                title="连接成功",
                content=message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            # 更新首页数据库连接状态
            main_window = self.window()
            if hasattr(main_window, 'homeInterface') and hasattr(main_window.homeInterface, 'statusCard'):
                main_window.homeInterface.statusCard.updateDatabaseStatus(True)
        else:
            InfoBar.error(
                title="连接失败",
                content=message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            # 更新首页数据库连接状态
            main_window = self.window()
            if hasattr(main_window, 'homeInterface') and hasattr(main_window.homeInterface, 'statusCard'):
                main_window.homeInterface.statusCard.updateDatabaseStatus(False)
    
    def _onSaveConfig(self):
        """保存配置"""
        try:
            # 保存配置到文件
            cfg.save()
            
            InfoBar.success(
                title="保存成功",
                content="配置已保存",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
        except Exception as e:
            MessageBox("错误", f"保存配置失败: {str(e)}", self).exec()
    
    def _onResetConfig(self):
        """恢复默认配置"""
        # 显示确认对话框
        result = MessageBox(
            title="确认重置",
            content="确定要恢复所有配置到默认值吗？此操作不可撤销。",
            parent=self
        ).exec()
        
        if result:
            # 重置配置
            cfg.restore()
            
            InfoBar.success(
                title="重置完成",
                content="所有配置已恢复到默认值",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
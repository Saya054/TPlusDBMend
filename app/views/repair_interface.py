# coding:utf-8
"""
数据修复界面模块
"""
import sys
import os
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QDragEnterEvent, QDropEvent, QIcon
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QFileDialog, QLabel)

from qfluentwidgets import (ScrollArea, CardWidget, TitleLabel, SubtitleLabel,
                           BodyLabel, PrimaryPushButton, PushButton, RadioButton,
                           LineEdit, ProgressBar, InfoBar, InfoBarPosition,
                           MessageBox, FluentIcon as FIF, SettingCardGroup,
                           ComboBox)
# from qfluentwidgetspro import StepProgressBar, DropSingleFileWidget
# 暂时使用基础组件替代

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from common.config import cfg


class ModeSelectorCard(CardWidget):
    """修复模式选择卡片"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mode = "zip"  # 默认ZIP模式
        self.initUI()
    
    def initUI(self):
        """初始化界面"""
        self.setFixedHeight(150)
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 20, 24, 20)
        
        # 标题
        titleLabel = SubtitleLabel("修复模式选择", self)
        titleLabel.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        
        # 模式选择
        modeLayout = QHBoxLayout()
        modeLayout.setSpacing(40)
        
        # ZIP模式
        self.zipRadio = RadioButton("ZIP文件模式", self)
        self.zipRadio.setChecked(True)  # 默认选中
        self.zipRadio.toggled.connect(self._onModeChanged)
        
        # 数据库模式
        self.dbRadio = RadioButton("数据库模式", self)
        self.dbRadio.toggled.connect(self._onModeChanged)
        
        modeLayout.addWidget(self.zipRadio)
        modeLayout.addWidget(self.dbRadio)
        modeLayout.addStretch()
        
        # 说明文字
        self.modeDescLabel = BodyLabel("ZIP模式：通过ZIP备份文件进行数据修复（推荐）", self)
        self.modeDescLabel.setStyleSheet("color: #666666")
        
        layout.addWidget(titleLabel)
        layout.addLayout(modeLayout)
        layout.addWidget(self.modeDescLabel)
    
    def _onModeChanged(self):
        """模式改变事件"""
        if self.zipRadio.isChecked():
            self.mode = "zip"
            self.modeDescLabel.setText("ZIP模式：通过ZIP备份文件进行数据修复（推荐）")
        else:
            self.mode = "db"
            self.modeDescLabel.setText("数据库模式：直接连接数据库进行修复（需要数据库访问权限）")
    
    def getMode(self):
        """获取当前选择的模式"""
        return self.mode


class FilePickerCard(CardWidget):
    """文件选择卡片"""
    
    def __init__(self, title: str, description: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.description = description
        self.filePath = ""
        
        self.initUI()
    
    def initUI(self):
        """初始化界面"""
        self.setMinimumHeight(120)
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 20, 24, 20)
        
        # 标题和描述
        titleLabel = SubtitleLabel(self.title, self)
        descLabel = BodyLabel(self.description, self)
        descLabel.setStyleSheet("color: #666666")
        
        # 文件选择区域
        fileLayout = QHBoxLayout()
        self.fileLineEdit = LineEdit(self)
        self.fileLineEdit.setPlaceholderText("请选择文件或拖拽文件到此处...")
        self.fileLineEdit.setReadOnly(True)
        
        self.browseBtn = PushButton(FIF.FOLDER, "浏览", self)
        self.browseBtn.clicked.connect(self._onBrowseClicked)
        
        fileLayout.addWidget(self.fileLineEdit, 1)
        fileLayout.addWidget(self.browseBtn)
        
        layout.addWidget(titleLabel)
        layout.addWidget(descLabel)
        layout.addLayout(fileLayout)
        
        # 启用拖拽
        self.setAcceptDrops(True)
    
    def _onBrowseClicked(self):
        """浏览按钮点击"""
        filePath, _ = QFileDialog.getOpenFileName(
            self, f"选择{self.title}", "", "ZIP文件 (*.zip)")
        if filePath:
            self.filePath = filePath
            self.fileLineEdit.setText(filePath)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile().endswith('.zip'):
                event.acceptProposedAction()
                self.setStyleSheet("""
                    FilePickerCard {
                        border: 2px dashed #0078D4;
                        background-color: rgba(0, 120, 212, 0.1);
                    }
                """)
    
    def dragLeaveEvent(self, event):
        """拖拽离开事件"""
        self.setStyleSheet("")
    
    def dropEvent(self, event: QDropEvent):
        """拖拽放下事件"""
        self.setStyleSheet("")
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            filePath = url.toLocalFile()
            if filePath.endswith('.zip'):
                self.filePath = filePath
                self.fileLineEdit.setText(filePath)
                event.acceptProposedAction()
    
    def getFilePath(self):
        """获取文件路径"""
        return self.filePath
    
    def clear(self):
        """清空文件路径"""
        self.filePath = ""
        self.fileLineEdit.clear()


class RepairProgressCard(CardWidget):
    """修复进度卡片"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        """初始化界面"""
        self.setMinimumHeight(200)
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 20, 24, 20)
        
        # 标题
        titleLabel = SubtitleLabel("修复进度", self)
        
        # 总进度条
        self.totalProgressBar = ProgressBar(self)
        self.totalProgressBar.setValue(0)
        
        self.progressLabel = BodyLabel("等待开始修复...", self)
        
        # 步骤显示 (暂时用标签替代StepProgressBar)
        self.stepLabel = SubtitleLabel("当前步骤: 等待开始", self)
        self.steps = ["比对版本", "检测坏表", "空账解体", "数据导入", "结构重建", "新账生成"]
        self.currentStep = -1
        
        layout.addWidget(titleLabel)
        layout.addWidget(self.totalProgressBar)
        layout.addWidget(self.progressLabel)
        layout.addWidget(self.stepLabel)
        layout.addStretch()
    
    def updateProgress(self, value: int, message: str = ""):
        """更新进度"""
        self.totalProgressBar.setValue(value)
        if message:
            self.progressLabel.setText(message)
    
    def updateStepProgress(self, step: int):
        """更新步骤进度"""
        self.currentStep = step
        if 0 <= step < len(self.steps):
            self.stepLabel.setText(f"当前步骤: {self.steps[step]}")
        else:
            self.stepLabel.setText("当前步骤: 等待开始")
    
    def reset(self):
        """重置进度"""
        self.totalProgressBar.setValue(0)
        self.progressLabel.setText("等待开始修复...")
        self.currentStep = -1
        self.stepLabel.setText("当前步骤: 等待开始")


class RepairThread(QThread):
    """修复线程"""
    
    # 信号
    progressChanged = pyqtSignal(int, str)  # 进度值, 消息
    stepChanged = pyqtSignal(int)  # 步骤
    finished = pyqtSignal(bool, str)  # 成功, 消息
    errorOccurred = pyqtSignal(str, str)  # 错误码, 错误消息
    
    def __init__(self, brokenPath: str, originPath: str, sparePath: str):
        super().__init__()
        self.brokenPath = brokenPath
        self.originPath = originPath
        self.sparePath = sparePath
    
    def run(self):
        """运行修复"""
        try:
            # 这里应该调用原有的修复逻辑
            # 现在只是模拟修复过程
            
            steps = [
                ("比对版本", 15),
                ("检测坏表", 30),
                ("空账解体", 50),
                ("数据导入", 70),
                ("结构重建", 85),
                ("新账生成", 100)
            ]
            
            for i, (step_name, progress) in enumerate(steps):
                self.progressChanged.emit(progress, f"正在{step_name}...")
                self.stepChanged.emit(i)
                self.msleep(1000)  # 模拟处理时间
            
            self.finished.emit(True, "修复完成!")
            
        except Exception as e:
            self.errorOccurred.emit("1000", str(e))


class RepairInterface(ScrollArea):
    """数据修复界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('RepairInterface')
        
        # 修复线程
        self.repairThread = None
        
        # 创建主部件
        self.scrollWidget = QWidget()
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        
        # 设置样式
        self.setStyleSheet("RepairInterface { background-color: transparent; border: none; }")
        
        self.initUI()
    
    def initUI(self):
        """初始化界面"""
        # 主布局
        mainLayout = QVBoxLayout(self.scrollWidget)
        mainLayout.setSpacing(24)
        mainLayout.setContentsMargins(36, 36, 36, 36)
        
        # 页面标题
        titleLabel = TitleLabel("数据修复", self.scrollWidget)
        titleLabel.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))
        mainLayout.addWidget(titleLabel)
        
        # 修复模式选择
        self.modeSelector = ModeSelectorCard(self.scrollWidget)
        self.modeSelector.zipRadio.toggled.connect(self._onModeChanged)
        self.modeSelector.dbRadio.toggled.connect(self._onModeChanged)
        mainLayout.addWidget(self.modeSelector)
        
        # ZIP模式界面
        self.zipModeWidget = QWidget()
        self.zipModeLayout = QVBoxLayout(self.zipModeWidget)
        self.zipModeLayout.setSpacing(24)
        
        # ZIP模式文件选择
        zipFileLayout = QHBoxLayout()
        zipFileLayout.setSpacing(24)
        
        self.brokenCard = FilePickerCard(
            "损坏的账套", 
            "选择需要修复的损坏账套ZIP备份文件",
            self.zipModeWidget
        )
        
        self.originCard = FilePickerCard(
            "空账套", 
            "选择同版本的空账套ZIP备份文件",
            self.zipModeWidget
        )
        
        self.spareCard = FilePickerCard(
            "备用账套", 
            "选择用于替换损坏数据的备用账套ZIP备份文件",
            self.zipModeWidget
        )
        
        zipFileLayout.addWidget(self.brokenCard)
        zipFileLayout.addWidget(self.originCard)
        zipFileLayout.addWidget(self.spareCard)
        
        self.zipModeLayout.addLayout(zipFileLayout)
        
        # 数据库模式界面
        self.dbModeWidget = QWidget()
        self.dbModeLayout = QVBoxLayout(self.dbModeWidget)
        self.dbModeLayout.setSpacing(24)
        
        # 三数据库连接配置卡片
        self.dbConnectionCard = CardWidget(self.dbModeWidget)
        self.dbConnectionCard.setMinimumHeight(300)
        dbConnectionLayout = QVBoxLayout(self.dbConnectionCard)
        dbConnectionLayout.setContentsMargins(24, 20, 24, 20)
        
        dbConnectionTitle = SubtitleLabel("数据库连接配置", self.dbConnectionCard)
        dbConnectionTitle.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        
        # 损坏的账套数据库
        brokenDbLayout = QHBoxLayout()
        brokenDbLayout.setSpacing(10)
        
        self.brokenDbLabel = BodyLabel("损坏的账套:", self.dbConnectionCard)
        self.brokenDbLabel.setFixedWidth(100)
        
        self.brokenDbCombo = ComboBox(self.dbConnectionCard)
        self.brokenDbCombo.setEnabled(False)
        self.brokenDbCombo.setPlaceholderText("请先连接后选择数据库")
        
        self.brokenDbConnectBtn = PushButton(FIF.CONNECT, "连接", self.dbConnectionCard)
        self.brokenDbConnectBtn.clicked.connect(lambda: self._onConnectDatabase("broken"))
        self.brokenDbConnectBtn.setFixedWidth(120)
        
        brokenDbLayout.addWidget(self.brokenDbLabel)
        brokenDbLayout.addWidget(self.brokenDbCombo)
        brokenDbLayout.addWidget(self.brokenDbConnectBtn)
        
        # 新建的空账数据库
        originDbLayout = QHBoxLayout()
        originDbLayout.setSpacing(10)
        
        self.originDbLabel = BodyLabel("新建的空账:", self.dbConnectionCard)
        self.originDbLabel.setFixedWidth(100)
        
        self.originDbCombo = ComboBox(self.dbConnectionCard)
        self.originDbCombo.setEnabled(False)
        self.originDbCombo.setPlaceholderText("请先连接后选择数据库")
        
        self.originDbConnectBtn = PushButton(FIF.CONNECT, "连接", self.dbConnectionCard)
        self.originDbConnectBtn.clicked.connect(lambda: self._onConnectDatabase("origin"))
        self.originDbConnectBtn.setFixedWidth(120)
        
        originDbLayout.addWidget(self.originDbLabel)
        originDbLayout.addWidget(self.originDbCombo)
        originDbLayout.addWidget(self.originDbConnectBtn)
        
        # 备用的账套数据库
        backupDbLayout = QHBoxLayout()
        backupDbLayout.setSpacing(10)
        
        self.backupDbLabel = BodyLabel("备用的账套:", self.dbConnectionCard)
        self.backupDbLabel.setFixedWidth(100)
        
        self.backupDbCombo = ComboBox(self.dbConnectionCard)
        self.backupDbCombo.setEnabled(False)
        self.backupDbCombo.setPlaceholderText("请先连接后选择数据库")
        
        self.backupDbConnectBtn = PushButton(FIF.CONNECT, "连接", self.dbConnectionCard)
        self.backupDbConnectBtn.clicked.connect(lambda: self._onConnectDatabase("backup"))
        self.backupDbConnectBtn.setFixedWidth(120)
        
        backupDbLayout.addWidget(self.backupDbLabel)
        backupDbLayout.addWidget(self.backupDbCombo)
        backupDbLayout.addWidget(self.backupDbConnectBtn)
        
        dbConnectionLayout.addWidget(dbConnectionTitle)
        dbConnectionLayout.addLayout(brokenDbLayout)
        dbConnectionLayout.addLayout(originDbLayout)
        dbConnectionLayout.addLayout(backupDbLayout)
        
        # 数据库修复配置卡片
        self.dbConfigCard = CardWidget(self.dbModeWidget)
        self.dbConfigCard.setMinimumHeight(200)
        dbConfigLayout = QVBoxLayout(self.dbConfigCard)
        dbConfigLayout.setContentsMargins(24, 20, 24, 20)
        
        dbConfigTitle = SubtitleLabel("数据库修复配置", self.dbConfigCard)
        dbConfigTitle.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        
        # 修复模式选择
        repairModeLayout = QHBoxLayout()
        repairModeLayout.setSpacing(20)
        
        self.verboseRadio = RadioButton("详细模式", self.dbConfigCard)
        self.verboseRadio.setChecked(True)
        self.standardRadio = RadioButton("标准模式", self.dbConfigCard)
        
        repairModeLayout.addWidget(BodyLabel("修复模式:", self.dbConfigCard))
        repairModeLayout.addWidget(self.verboseRadio)
        repairModeLayout.addWidget(self.standardRadio)
        repairModeLayout.addStretch()
        
        # 数据清理选择
        dataClearLayout = QHBoxLayout()
        dataClearLayout.setSpacing(20)
        
        self.clearYesRadio = RadioButton("是", self.dbConfigCard)
        self.clearYesRadio.setChecked(True)
        self.clearNoRadio = RadioButton("否", self.dbConfigCard)
        
        dataClearLayout.addWidget(BodyLabel("完成后清理数据:", self.dbConfigCard))
        dataClearLayout.addWidget(self.clearYesRadio)
        dataClearLayout.addWidget(self.clearNoRadio)
        dataClearLayout.addStretch()
        
        dbConfigLayout.addWidget(dbConfigTitle)
        dbConfigLayout.addLayout(repairModeLayout)
        dbConfigLayout.addLayout(dataClearLayout)
        dbConfigLayout.addStretch()
        
        # 数据库修复说明
        self.dbInstructionCard = CardWidget(self.dbModeWidget)
        self.dbInstructionCard.setMinimumHeight(150)
        dbInstructionLayout = QVBoxLayout(self.dbInstructionCard)
        dbInstructionLayout.setContentsMargins(24, 20, 24, 20)
        
        dbInstructionTitle = SubtitleLabel("修复说明", self.dbInstructionCard)
        dbInstructionTitle.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        
        dbInstructionText = BodyLabel(
            "数据库修复模式将执行以下步骤：\n"
            "1. 验证数据库连接和配置\n"
            "2. 检查损坏表和数据完整性\n"
            "3. 备份原始数据\n"
            "4. 执行数据修复和重建操作\n"
            "5. 验证修复结果\n\n"
            "注意：修复过程中请不要关闭程序或断开数据库连接。",
            self.dbInstructionCard
        )
        dbInstructionText.setWordWrap(True)
        dbInstructionText.setStyleSheet("color: #666666")
        
        dbInstructionLayout.addWidget(dbInstructionTitle)
        dbInstructionLayout.addWidget(dbInstructionText)
        
        self.dbModeLayout.addWidget(self.dbConnectionCard)
        self.dbModeLayout.addWidget(self.dbConfigCard)
        self.dbModeLayout.addWidget(self.dbInstructionCard)
        
        # 添加到主布局
        mainLayout.addWidget(self.zipModeWidget)
        mainLayout.addWidget(self.dbModeWidget)
        
        # 默认显示ZIP模式，隐藏DB模式
        self.dbModeWidget.hide()
        
        # 控制按钮区域
        controlLayout = QHBoxLayout()
        
        self.startBtn = PrimaryPushButton(FIF.PLAY, "开始修复", self.scrollWidget)
        self.startBtn.clicked.connect(self._onStartRepair)
        
        self.resetBtn = PushButton(FIF.SYNC, "重置", self.scrollWidget)
        self.resetBtn.clicked.connect(self._onReset)
        
        controlLayout.addWidget(self.startBtn)
        controlLayout.addWidget(self.resetBtn)
        controlLayout.addStretch()
        
        mainLayout.addLayout(controlLayout)
        
        # 修复进度区域
        self.progressCard = RepairProgressCard(self.scrollWidget)
        mainLayout.addWidget(self.progressCard)
        
        mainLayout.addStretch()
    
    def _onModeChanged(self):
        """修复模式切换"""
        mode = self.modeSelector.getMode()
        if mode == "zip":
            self.zipModeWidget.show()
            self.dbModeWidget.hide()
        else:
            self.zipModeWidget.hide()
            self.dbModeWidget.show()
    
    def _onStartRepair(self):
        """开始修复"""
        mode = self.modeSelector.getMode()
        
        if mode == "zip":
            # ZIP模式 - 检查文件是否都已选择
            brokenPath = self.brokenCard.getFilePath()
            originPath = self.originCard.getFilePath()
            sparePath = self.spareCard.getFilePath()
            
            if not all([brokenPath, originPath, sparePath]):
                MessageBox("错误", "请选择所有必需的文件!", self).exec()
                return
            
            # 开始ZIP修复
            self.startBtn.setEnabled(False)
            self.resetBtn.setEnabled(False)
            self.progressCard.reset()
            
            # 创建修复线程
            self.repairThread = RepairThread(brokenPath, originPath, sparePath)
            self.repairThread.progressChanged.connect(self.progressCard.updateProgress)
            self.repairThread.stepChanged.connect(self.progressCard.updateStepProgress)
            self.repairThread.finished.connect(self._onRepairFinished)
            self.repairThread.errorOccurred.connect(self._onRepairError)
            
            self.repairThread.start()
        
        else:
            # 数据库模式 - 开始数据库修复
            self._startDatabaseRepair()
    
    def _onConnectDatabase(self, db_type):
        """连接数据库并获取数据库列表"""
        host = cfg.get(cfg.sqlHost)
        port = cfg.get(cfg.sqlPort)
        user = cfg.get(cfg.sqlUser)
        password = cfg.get(cfg.sqlPassword)
        
        if not all([host, port, user, password]):
            MessageBox("配置错误", "请先在配置页面中设置完整的数据库连接信息!", self).exec()
            return
        
        # 获取对应的按钮和组合框
        if db_type == "broken":
            btn = self.brokenDbConnectBtn
            combo = self.brokenDbCombo
        elif db_type == "origin":
            btn = self.originDbConnectBtn
            combo = self.originDbCombo
        else:  # backup
            btn = self.backupDbConnectBtn
            combo = self.backupDbCombo
        
        # 如果按钮显示"已连接"，询问是否重新连接
        if btn.text() == "已连接":
            dialog = MessageBox("重新连接", "数据库已连接，是否重新连接？", self)
            dialog.yesButton.setText("是")
            dialog.cancelButton.setText("否")
            if dialog.exec() == dialog.Rejected:
                return
        
        # 重置组合框状态
        combo.clear()
        combo.setEnabled(False)
        combo.setPlaceholderText("请先连接数据库")
        
        # 设置连接中状态
        btn.setEnabled(False)
        btn.setText("连接中...")
        btn.setIcon(FIF.SYNC)  # 使用同步图标表示连接中
        btn.setStyleSheet("")  # 清除之前的样式
        
        try:
            # 尝试导入新版本的数据库驱动
            from core.DataDrivers import TsDBdriver, PYMSSQL_AVAILABLE
            
            # 根据可用性选择驱动
            if PYMSSQL_AVAILABLE:
                driver = "pymssql driver"
            else:
                # 尝试使用ODBC驱动作为备选
                from core.basicFunc import GetOdbcdriver
                odbc_drivers = GetOdbcdriver()
                if odbc_drivers:
                    driver = odbc_drivers[0]
                else:
                    InfoBar.error(
                        title="驱动不可用",
                        content="未找到可用的数据库驱动。请安装 pymssql 或配置 ODBC 驱动",
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=5000,
                        parent=self
                    )
                    return
            
            connection = TsDBdriver(host, user, password, driver, 'master')
            
            # 获取数据库列表
            databases = connection.getAllDatabases()
            if databases and databases != 'Unconnect':
                # 更新组合框
                combo.clear()
                combo.addItems(databases)
                combo.setEnabled(True)
                combo.setPlaceholderText("请选择数据库")
                
                # 设置连接成功状态
                btn.setEnabled(True)
                btn.setText("已连接")
                btn.setIcon(QIcon())  # 移除图标，避免遮挡文字
                btn.setStyleSheet("QPushButton { background-color: #10893E; color: white; }")  # 绿色背景
                
                InfoBar.success(
                    title="连接成功",
                    content=f"{db_type}数据库连接成功，已获取数据库列表！",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
            else:
                # 设置连接失败状态
                btn.setEnabled(True)
                btn.setText("连接失败")
                btn.setIcon(FIF.CANCEL)  # 使用取消图标表示失败
                btn.setStyleSheet("QPushButton { background-color: #C42B1C; color: white; }")  # 红色背景
                
                InfoBar.error(
                    title="获取失败",
                    content="连接成功但无法获取数据库列表！",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                
        except ImportError as e:
            error_msg = str(e)
            
            # 设置连接失败状态
            btn.setEnabled(True)
            btn.setText("连接失败")
            btn.setIcon(FIF.CANCEL)
            btn.setStyleSheet("QPushButton { background-color: #C42B1C; color: white; }")
            
            if "pymssql" in error_msg:
                InfoBar.error(
                    title="pymssql缺失",
                    content="pymssql模块未安装。请运行：pip install pymssql",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=5000,
                    parent=self
                )
            else:
                InfoBar.error(
                    title="模块缺失",
                    content=f"数据库驱动模块未找到：{error_msg}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=5000,
                    parent=self
                )
        except Exception as e:
            # 设置连接失败状态
            btn.setEnabled(True)
            btn.setText("连接失败")
            btn.setIcon(FIF.CANCEL)
            btn.setStyleSheet("QPushButton { background-color: #C42B1C; color: white; }")
            
            InfoBar.error(
                title="连接失败",
                content=f"连接失败: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
    
    def _startDatabaseRepair(self):
        """开始数据库修复"""
        # 获取数据库配置
        host = cfg.get(cfg.sqlHost)
        port = cfg.get(cfg.sqlPort)
        user = cfg.get(cfg.sqlUser)
        password = cfg.get(cfg.sqlPassword)
        
        if not all([host, port, user, password]):
            MessageBox("配置错误", "请先在配置页面中设置完整的数据库连接信息!", self).exec()
            return
        
        # 获取选择的数据库
        broken_db = self.brokenDbCombo.currentText()
        origin_db = self.originDbCombo.currentText()
        backup_db = self.backupDbCombo.currentText()
        
        if not all([broken_db, origin_db, backup_db]):
            MessageBox("配置错误", "请先连接数据库并选择所有必需的数据库!", self).exec()
            return
        
        # 检查数据库名称是否重复
        if broken_db == origin_db or broken_db == backup_db or origin_db == backup_db:
            MessageBox("配置错误", "数据库名称不能重复，请选择不同的数据库!", self).exec()
            return
        
        # 获取修复配置
        repair_mode = 0 if self.verboseRadio.isChecked() else 1
        data_clear = 1 if self.clearYesRadio.isChecked() else 0
        
        # 禁用界面
        self.startBtn.setEnabled(False)
        self.resetBtn.setEnabled(False)
        self.brokenDbConnectBtn.setEnabled(False)
        self.originDbConnectBtn.setEnabled(False)
        self.backupDbConnectBtn.setEnabled(False)
        
        # 重置进度
        self.progressCard.reset()
        
        try:
            # 导入修复模块
            from core.DBRepair import PreDBrepair, NowDBRepair
            
            # 使用pymssql驱动
            driver = "pymssql driver"
            
            InfoBar.info(
                title="修复开始",
                content="数据库修复已开始，正在执行预检验...",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            
            # 执行修复前校验
            pre_result = PreDBrepair(host, user, password, driver, 'master', 
                                   broken_db, origin_db, backup_db)
            
            if pre_result[0]:  # 校验成功
                InfoBar.success(
                    title="预检验成功",
                    content="数据库预检验通过，开始执行修复...",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                
                # 执行修复
                repair_result = NowDBRepair(host, user, password, driver, 'master',
                                          broken_db, origin_db, backup_db)
                
                if repair_result[0]:  # 修复成功
                    InfoBar.success(
                        title="修复完成",
                        content="数据库修复已完成！",
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=5000,
                        parent=self
                    )
                else:  # 修复失败
                    InfoBar.error(
                        title="修复失败",
                        content=f"修复失败: {repair_result[1]}",
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=5000,
                        parent=self
                    )
            else:  # 校验失败
                InfoBar.error(
                    title="预检验失败",
                    content=f"预检验失败: {pre_result[1]}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=5000,
                    parent=self
                )
                
        except ImportError as e:
            InfoBar.error(
                title="模块错误",
                content="修复功能模块未找到，请检查安装！",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        except Exception as e:
            InfoBar.error(
                title="修复异常",
                content=f"修复过程中发生异常: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )
        finally:
            # 恢复界面状态
            self.startBtn.setEnabled(True)
            self.resetBtn.setEnabled(True)
            self.brokenDbConnectBtn.setEnabled(True)
            self.originDbConnectBtn.setEnabled(True)
            self.backupDbConnectBtn.setEnabled(True)
    
    def _onReset(self):
        """重置"""
        # 重置ZIP模式相关
        self.brokenCard.clear()
        self.originCard.clear()
        self.spareCard.clear()
        self.progressCard.reset()
        
        # 重置数据库模式相关
        self._resetDatabaseConnections()
        
        self.startBtn.setEnabled(True)
        self.resetBtn.setEnabled(True)
        
        InfoBar.success(
            title="重置完成",
            content="界面已重置",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=1500,
            parent=self
        )
    
    def _resetDatabaseConnections(self):
        """重置数据库连接状态"""
        # 重置所有连接按钮到初始状态
        for btn, combo in [
            (self.brokenDbConnectBtn, self.brokenDbCombo),
            (self.originDbConnectBtn, self.originDbCombo),
            (self.backupDbConnectBtn, self.backupDbCombo)
        ]:
            btn.setEnabled(True)
            btn.setText("连接")
            btn.setIcon(FIF.CONNECT)
            btn.setStyleSheet("")  # 清除样式
            
            combo.clear()
            combo.setEnabled(False)
            combo.setPlaceholderText("请先连接数据库")
    
    def _onRepairFinished(self, success: bool, message: str):
        """修复完成"""
        self.startBtn.setEnabled(True)
        self.resetBtn.setEnabled(True)
        
        if success:
            InfoBar.success(
                title="修复成功!",
                content=message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )
        else:
            InfoBar.error(
                title="修复失败",
                content=message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )
    
    def _onRepairError(self, errorCode: str, errorMessage: str):
        """修复错误"""
        self.startBtn.setEnabled(True)
        self.resetBtn.setEnabled(True)
        
        MessageBox("修复失败", f"错误代码: {errorCode}\n错误信息: {errorMessage}", self).exec()
        
        InfoBar.error(
            title="修复失败",
            content=f"发生错误: {errorCode}",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=self
        )
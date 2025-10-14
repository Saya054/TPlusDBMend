# coding:utf-8
"""
设置界面模块
"""
import sys
import os
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont, QDesktopServices
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from qfluentwidgets import (ScrollArea, SettingCardGroup, OptionsSettingCard,
                           SwitchSettingCard, HyperlinkCard, PrimaryPushSettingCard,
                           TitleLabel, InfoBar, InfoBarPosition,
                           FluentIcon as FIF, Theme, setTheme)

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from common.config import cfg, Theme as ConfigTheme


class SettingInterface(ScrollArea):
    """设置界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('SettingInterface')
        
        # 创建主部件
        self.scrollWidget = QWidget()
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        
        # 设置样式
        self.setStyleSheet("SettingInterface { background-color: transparent; border: none; }")
        
        self.initUI()
    
    def initUI(self):
        """初始化界面"""
        # 主布局
        mainLayout = QVBoxLayout(self.scrollWidget)
        mainLayout.setSpacing(24)
        mainLayout.setContentsMargins(36, 36, 36, 36)
        
        # 页面标题
        titleLabel = TitleLabel("设置", self.scrollWidget)
        titleLabel.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))
        mainLayout.addWidget(titleLabel)
        
        # 外观设置组
        self.appearanceGroup = SettingCardGroup("外观设置", self.scrollWidget)
        
        # 主题设置
        self.themeCard = OptionsSettingCard(
            cfg.theme,
            FIF.BRUSH,
            "应用主题",
            "选择应用程序的外观主题",
            texts=["浅色", "深色", "跟随系统"]
        )
        self.themeCard.optionChanged.connect(self._onThemeChanged)
        
        # 云母效果
        self.micaCard = SwitchSettingCard(
            FIF.TRANSPARENT,
            "云母效果",
            "启用半透明云母背景效果",
            cfg.micaEnabled
        )
        
        self.appearanceGroup.addSettingCard(self.themeCard)
        self.appearanceGroup.addSettingCard(self.micaCard)
        
        # 语言设置组
        self.languageGroup = SettingCardGroup("语言设置", self.scrollWidget)
        
        self.languageCard = OptionsSettingCard(
            cfg.language,
            FIF.LANGUAGE,
            "界面语言",
            "选择应用程序的显示语言",
            texts=["简体中文", "English"]
        )
        
        self.languageGroup.addSettingCard(self.languageCard)
        
        # 关于设置组
        self.aboutGroup = SettingCardGroup("关于", self.scrollWidget)
        
        # 应用信息
        self.aboutCard = HyperlinkCard(
            "https://github.com/yourusername/tplus-dbmend",
            "T+数据库修复工具 v3.0",
            FIF.INFO,
            "关于应用",
            "基于 qfluentwidgets 重构的数据库修复工具"
        )
        
        # 反馈
        self.feedbackCard = PrimaryPushSettingCard(
            "提供反馈",
            FIF.FEEDBACK,
            "反馈与建议",
            "帮助我们改进这个应用程序"
        )
        self.feedbackCard.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/yourusername/tplus-dbmend/issues")))
        
        # 检查更新
        self.updateCard = HyperlinkCard(
            "https://github.com/yourusername/tplus-dbmend/releases",
            "检查更新",
            FIF.UPDATE,
            "应用更新",
            "检查是否有新版本可用"
        )
        
        self.aboutGroup.addSettingCard(self.aboutCard)
        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.updateCard)
        
        # 高级设置组
        self.advancedGroup = SettingCardGroup("高级设置", self.scrollWidget)
        
        # 开发者选项
        self.developerCard = SwitchSettingCard(
            FIF.DEVELOPER_TOOLS,
            "开发者模式",
            "启用调试功能和详细日志输出"
        )
        
        # 自动保存配置
        self.autoSaveCard = SwitchSettingCard(
            FIF.SAVE,
            "自动保存",
            "更改设置时自动保存配置文件"
        )
        self.autoSaveCard.switchButton.setChecked(True)
        self.autoSaveCard.switchButton.checkedChanged.connect(self._onAutoSaveChanged)
        
        self.advancedGroup.addSettingCard(self.developerCard)
        self.advancedGroup.addSettingCard(self.autoSaveCard)
        
        # 添加到主布局
        mainLayout.addWidget(self.appearanceGroup)
        mainLayout.addWidget(self.languageGroup)
        mainLayout.addWidget(self.aboutGroup)
        mainLayout.addWidget(self.advancedGroup)
        mainLayout.addStretch()
    
    def _onThemeChanged(self, theme: str):
        """主题改变事件"""
        # 映射主题名称到配置值
        theme_map = {
            "浅色": ConfigTheme.LIGHT.value,
            "深色": ConfigTheme.DARK.value,
            "跟随系统": ConfigTheme.AUTO.value
        }
        
        if theme in theme_map:
            # 保存配置
            cfg.set(cfg.theme, theme_map[theme])
            
            # 应用主题
            fluent_theme_map = {
                ConfigTheme.LIGHT.value: Theme.LIGHT,
                ConfigTheme.DARK.value: Theme.DARK,
                ConfigTheme.AUTO.value: Theme.AUTO
            }
            setTheme(fluent_theme_map[theme_map[theme]])
            
            InfoBar.success(
                title="主题已更改",
                content=f"已切换到{theme}主题",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
    
    def _onAutoSaveChanged(self, checked: bool):
        """自动保存设置改变"""
        if checked:
            # 启用自动保存时立即保存当前配置
            cfg.save()
            
            InfoBar.info(
                title="自动保存已启用",
                content="设置更改将自动保存",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
# coding:utf-8
"""
简化测试 - 只使用基础qfluentwidgets组件
"""
import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# 测试基础qfluentwidgets组件
try:
    from qfluentwidgets import (PrimaryPushButton, PushButton, TitleLabel, 
                               CardWidget, FluentIcon as FIF, ScrollArea)
    print("OK - 基础qfluentwidgets组件导入成功")
    
    # 创建简单的测试窗口
    class SimpleTest(QWidget):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("qfluentwidgets 测试")
            self.resize(400, 300)
            
            layout = QVBoxLayout(self)
            
            # 添加一些基础组件
            title = TitleLabel("qfluentwidgets 测试", self)
            layout.addWidget(title)
            
            card = CardWidget(self)
            card.setFixedHeight(100)
            layout.addWidget(card)
            
            btn1 = PrimaryPushButton("主要按钮", self)
            btn2 = PushButton(FIF.SETTING, "设置按钮", self)
            
            layout.addWidget(btn1)
            layout.addWidget(btn2)
    
    # 运行测试应用
    if __name__ == '__main__':
        app = QApplication(sys.argv)
        
        # 设置高DPI支持
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        window = SimpleTest()
        window.show()
        
        print("OK - 测试窗口已启动")
        print("如果看到窗口，说明qfluentwidgets基础组件工作正常")
        
        # 自动关闭以便继续测试
        app.processEvents()
        window.close()
        
        print("OK - 基础测试完成")
        
except ImportError as e:
    print(f"ERROR - 基础qfluentwidgets导入失败: {e}")
    sys.exit(1)
except Exception as e:
    print(f"ERROR - 其他错误: {e}")
    sys.exit(1)
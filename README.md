# T+数据库修复工具 v3.0

基于 qfluentwidgets 重构的T+系列产品数据库修复工具。

##预览
<img width="1196" height="798" alt="image" src="https://github.com/user-attachments/assets/67029509-1b88-4c84-8c32-936f508cd5ac" />

## 特性

- 🎨 **现代化界面**: 采用 Fluent Design 设计语言
- 🔧 **数据修复**: 专业的T+数据库修复功能
- ⚙️ **配置管理**: 直观的配置界面
- 📊 **日志查看**: 实时日志监控和过滤
- 🌙 **主题支持**: 浅色/深色主题切换
- 🌐 **多语言**: 支持中文/英文界面

## 技术栈

- **UI框架**: PyQt5 + qfluentwidgets Pro
- **数据库**: Microsoft SQL Server (pymssql)
- **配置管理**: QConfig
- **架构**: MVC模式

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行程序

```bash
python run.py
```

## 项目结构

```
datarepairV4/
├── app/                    # 应用程序主体
│   ├── views/             # 界面模块
│   │   ├── main_window.py # 主窗口
│   │   ├── home_interface.py # 主页
│   │   ├── repair_interface.py # 修复界面
│   │   ├── config_interface.py # 配置界面
│   │   ├── log_interface.py # 日志界面
│   │   └── setting_interface.py # 设置界面
│   └── components/        # 自定义组件
├── common/                # 公共模块
│   └── config.py         # 配置管理
├── core/                  # 核心业务逻辑
│   ├── dbfunc.py         # 数据库操作
│   ├── baseFunc.py       # 基础功能
│   ├── repairstep.py     # 修复步骤
│   ├── zippack.py        # ZIP处理
│   └── CheckXML.py       # XML检查
├── resources/            # 资源文件
├── main.py              # 主程序入口
└── run.py               # 启动脚本
```

## 界面预览

### 主页
- 欢迎信息和快速操作
- 系统状态展示
- 现代化卡片布局

### 数据修复
- 文件拖拽选择
- 进度可视化
- 步骤追踪

### 配置管理
- 数据库连接配置
- 文件路径设置
- 实时配置验证

### 日志查看
- 日志级别过滤
- 内容搜索
- 自动刷新

## 开发说明

### 添加新界面
1. 在 `app/views/` 创建新的界面文件
2. 继承适当的基类 (如 `ScrollArea`)
3. 在 `main_window.py` 中注册新界面

### 修改配置项
1. 在 `common/config.py` 添加配置项
2. 在相应界面中添加设置卡片
3. 测试配置保存和加载

### 自定义组件
- 在 `app/components/` 创建可复用组件
- 遵循 qfluentwidgets 设计规范

## 许可证


本项目基于原 T+数据库修复工具重构，保留原有核心功能的同时提供现代化的用户界面。

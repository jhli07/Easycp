# Easycp

一个简单实用的 Windows 剪贴板图片粘贴工具，让你可以直接将截图粘贴到文件夹中！

## ✨ 功能特点

- 🖼️ **截图直接粘贴**：使用 Windows 截图工具（Win+Shift+S）截取图片后，直接按 Ctrl+V 即可保存到当前文件夹
- 📂 **智能路径识别**：自动识别当前资源管理器窗口的路径，支持多窗口切换
- 🔄 **自动刷新**：保存图片后自动刷新文件夹显示
- 💼 **后台运行**：系统托盘常驻，不占用桌面空间
- ⚡ **不影响正常操作**：仅在剪贴板有图片且当前窗口是资源管理器时触发，不干扰正常的复制粘贴

## 🚀 快速开始

### 方法一：直接运行（推荐）

1. 下载最新版本的 `Easycp.exe`（从 Releases 页面）
2. 双击运行，程序会在系统托盘显示蓝色图标
3. 使用 Win+Shift+S 截图
4. 在资源管理器窗口中按 Ctrl+V，图片会自动保存

### 方法二：从源码运行

```bash
# 克隆项目
git clone https://github.com/yourusername/Easycp.git
cd Easycp

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

### 方法三：打包为可执行文件

```bash
# 安装依赖
pip install -r requirements.txt

# 使用 PyInstaller 打包
pyinstaller --onefile --windowed --name Easycp main.py

# 生成的可执行文件在 dist 目录中
```

## 📖 使用说明

1. **启动程序**：双击 `Easycp.exe`，系统托盘会出现蓝色图标
2. **截图**：按 Win+Shift+S 截取屏幕
3. **粘贴到文件夹**：
   - 打开资源管理器窗口，确保它是当前活动窗口
   - 按 Ctrl+V
   - 图片会自动保存为 `screenshot_时间戳.png`
4. **退出程序**：右键点击系统托盘图标，选择"退出"

## 📁 项目结构

```
Easycp/
├── main.py          # 主程序代码
├── requirements.txt # 依赖列表
├── README.md        # 项目说明文档
├── .gitignore       # Git 忽略文件
└── dist/            # 打包后的可执行文件目录
```

## 🔧 技术栈

- Python 3.8+
- pywin32 - Windows API 操作
- Pillow - 图片处理
- pystray - 系统托盘图标
- keyboard - 全局热键监听
- uiautomation - UI 自动化（读取资源管理器路径）

## ⚠️ 注意事项

1. **管理员权限**：首次运行可能需要管理员权限以安装全局热键监听
2. **Windows 版本**：支持 Windows 10 和 Windows 11
3. **杀毒软件**：部分杀毒软件可能会误报，可将程序添加到信任列表
4. **日志文件**：日志保存在 `%APPDATA%\Easycp\easypaste.log`，可通过右键菜单查看

## 📝 更新日志

### v1.0.0
- 初始版本发布
- 支持截图直接粘贴到资源管理器文件夹
- 支持多窗口切换识别
- 系统托盘常驻运行

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，请在 GitHub Issues 中提出。
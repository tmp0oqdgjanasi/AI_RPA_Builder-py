# AI RPA Builder Ultimate (零依赖终极自动化构建器)

这是一个基于 Gemini 3 Flash 大模型多模态视觉能力的“极客级 RPA 母程序”。

**终极版的绝对优势：彻底移除了对 Tesseract 等外部 OCR 软件的依赖！** 它内置纯 Python 的轻量级 AI 视觉库 `ddddocr`，配合全自动的后台编译工厂，为你生成一个**随时随地、无需配置任何环境**即可在任意 Windows 电脑上双击运行的独立自动化 EXE。

---

## ✨ 核心升级特性

* **真正的零外部依赖**：生成的 EXE 纯净且独立，告别繁琐的外部 OCR 引擎安装与系统环境变量配置。
* **配置一次，永久记忆**：首次启动自动弹窗配置 API Key，随后安全加密保存在本地 `config.json` 中，二次启动实现无感体验。
* **GUI 图形化交互**：告别纯黑框命令行，启动后提供优雅的弹窗菜单，自由勾选所需的输出格式（Python / EXE纯净版 / Java）。
* **多模态视觉与智能算术**：截取屏幕关键帧交由大模型分析，自动锁定动态算术题区域，子程序实现循环截图、离线识别、计算并自动输入。
* **全自动后台流水线**：脚本内置 Subprocess 命令流，自动安装打包依赖、编译独立 EXE 并智能清理构建现场的临时文件。

---

## 🔑 免费获取 Gemini API 密钥

本工具的“视觉与编程大脑”依赖于 Google Gemini 大模型，Google 提供了非常慷慨的免费调用额度。

**获取步骤：**
1. 确保你的网络环境可以顺畅访问 Google 服务。
2. 访问 Google AI Studio 官网: [https://aistudio.google.com/](https://aistudio.google.com/)
3. 登录你的 Google 账号，在页面左侧导航栏点击 **"Get API key"**。
4. 点击 **"Create API key"** 按钮，生成一串以 `AQ.Q` 或 `AIza` 开头的密钥并复制。
5. **首次运行本程序时**，在弹出的配置窗口中粘贴该密钥即可。

---

## 🛠️ 环境准备与安装 (仅限运行母程序)

要运行这个“造物主”母程序，你只需要准备基础的 Python 环境即可（它造出来的子程序则完全不需要任何环境）。

### 1. Python 环境
请确保电脑已安装 Python 3.8 或以上版本，并在安装时勾选了“添加至系统环境变量”。

### 2. 一键安装依赖
打开终端（CMD 或 PowerShell），执行以下命令一次性安装所有需要的纯 Python 库：
```bash
pip install mss pynput google-generativeai Pillow pyinstaller pyautogui ddddocr

# AI RPA Builder Ultimate

这是一个基于 Gemini 3 Flash 大模型多模态视觉能力的“RPA 母程序”。

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
### 1. Python 环境
请确保电脑已安装 Python 3.8 或以上版本，并在安装时勾选了“添加至系统环境变量”。

### 2. 一键安装依赖
打开终端（CMD 或 PowerShell），执行以下命令一次性安装所有需要的纯 Python 库：
```bash
pip install mss pynput google-generativeai Pillow pyinstaller pyautogui ddddocr
```
bcbn

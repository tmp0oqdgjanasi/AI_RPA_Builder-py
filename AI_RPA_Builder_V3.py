import time
import os
import mss
import re
import json
from pynput import mouse, keyboard
import google.generativeai as genai
from PIL import Image
import subprocess
import tkinter as tk
from tkinter import messagebox

# ================= 配置文件与 API Key 持久化 =================
CONFIG_FILE = "config.json"

def load_or_prompt_api_key():
    api_key = ""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                api_key = config.get("api_key", "").strip()
        except Exception:
            pass

    if api_key:
        print("[配置加载] 已成功从本地 config.json 读取 API Key。")
        return api_key

    root = tk.Tk()
    root.title("首次运行 - 配置 Gemini API Key")
    window_width, window_height = 380, 200
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    root.attributes('-topmost', True)

    tk.Label(root, text="欢迎使用 AI RPA 构建器！", font=("Arial", 12, "bold")).pack(pady=(15, 5))
    tk.Label(root, text="检测到首次运行，请输入您的 Gemini API Key：\n(配置后将永久保存至 config.json)", font=("Arial", 9), fg="#666666").pack(pady=5)
    
    entry = tk.Entry(root, width=42, show="*")
    entry.pack(pady=10)
    entry.focus()

    saved_key = []

    def on_save():
        key = entry.get().strip()
        if not key:
            messagebox.showwarning("警告", "API Key 不能为空！")
            return
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump({"api_key": key}, f, indent=4)
            saved_key.append(key)
            messagebox.showinfo("成功", "API Key 已成功保存！以后启动无需再次输入。")
            root.destroy()
        except Exception as e:
            messagebox.showerror("保存失败", f"无法写入配置文件: {e}")

    tk.Button(root, text="保存配置并继续", width=18, command=on_save, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(pady=10)
    root.mainloop()

    if saved_key:
        return saved_key[0]
    else:
        print("未输入 API Key，程序退出。")
        exit()

API_KEY = load_or_prompt_api_key()
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-3-flash') 

# 全局变量
recorded_actions = []
screenshots = []
sct = mss.mss()

# 录制状态控制: 
# 0 = 未开始第一次录制
# 1 = 正在进行第一次录制
# 2 = 第一次录制已结束，等待开始第二次
# 3 = 正在进行第二次录制
# 4 = 第二次录制已结束，准备提交处理
recording_stage = 0 

# ================= 弹窗菜单：选择输出格式 =================
def get_user_choice():
    root = tk.Tk()
    root.title("AI RPA 构建器 Ultimate")
    window_width, window_height = 320, 240
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    root.attributes('-topmost', True)

    var_py = tk.BooleanVar(value=False)
    var_exe = tk.BooleanVar(value=True)
    var_java = tk.BooleanVar(value=False)
    
    tk.Label(root, text="请选择需要生成的格式（可多选）：", font=("Arial", 11, "bold")).pack(pady=15)
    tk.Checkbutton(root, text="1. Python 源码 (.py)", variable=var_py).pack(anchor='w', padx=70)
    tk.Checkbutton(root, text="2. 独立运行程序 (.exe) [纯净版]", variable=var_exe).pack(anchor='w', padx=70)
    tk.Checkbutton(root, text="3. Java Maven 项目", variable=var_java).pack(anchor='w', padx=70)
    
    selected_targets = []
    
    def on_confirm():
        if var_py.get(): selected_targets.append('1')
        if var_exe.get(): selected_targets.append('2')
        if var_java.get(): selected_targets.append('3')
        if not selected_targets:
            messagebox.showwarning("提示", "请至少勾选一种输出格式！")
            return
        root.destroy()
        
    tk.Button(root, text="确认并开始", width=15, command=on_confirm, bg="#2196F3", fg="white", font=("Arial", 10, "bold")).pack(pady=20)
    root.mainloop()
    return selected_targets

targets = get_user_choice()
if not targets:
    exit()

print(f"[就绪] 已选择格式: {targets}")
print("\n==================================================")
print("【提示】请切换到目标界面：")
print("1. 按下【空格键】 -> 弹出提示，开始【第一次录制】")
print("2. 再次按下【空格键】 -> 弹出提示，结束【第一次录制】")
print("3. 再次按下【空格键】 -> 弹出提示，开始【第二次录制】")
print("4. 最后按下【空格键】 -> 弹出提示，结束【第二次录制】并提交AI生成！")
print("==================================================\n")

# 辅助弹窗提示函数
def show_popup(title, message):
    def _show():
        root = tk.Tk()
        root.withdraw() # 隐藏主窗口
        root.attributes('-topmost', True)
        messagebox.showinfo(title, message)
        root.destroy()
    # 开启小线程弹窗，避免阻塞键盘监听
    import threading
    threading.Thread(target=_show).start()

# ================= 监听逻辑 (键盘空格 + 鼠标轨迹) =================
def on_press(key):
    global recording_stage
    try:
        if key == keyboard.Key.space:
            if recording_stage == 0:
                recording_stage = 1
                print("\n[状态] 开始【第一次录制】...")
                show_popup("提示", "【第一次录制】已开始！请执行您的动作。")
            elif recording_stage == 1:
                recording_stage = 2
                print("\n[状态] 结束【第一次录制】。")
                show_popup("提示", "【第一次录制】已结束！\n准备好后，可再次按空格开始第二次录制。")
            elif recording_stage == 2:
                recording_stage = 3
                print("\n[状态] 开始【第二次录制】...")
                show_popup("提示", "【第二次录制】已开始！请继续执行您的动作。")
            elif recording_stage == 3:
                recording_stage = 4
                print("\n[状态] 结束【第二次录制】。准备提交生成...")
                show_popup("提示", "【第二次录制】已结束！\n程序正在后台呼叫 Gemini 编译代码，请稍候...")
                return False # 停止键盘监听，开始进入生成环节
    except Exception as e:
        print("监听异常:", e)

def on_click(x, y, button, pressed):
    # 只有在阶段 1 或 3（录制中）时才记录鼠标点击和截图
    if (recording_stage == 1 or recording_stage == 3) and pressed:
        action = f"Clicked {button} at ({x}, {y})"
        recorded_actions.append(action)
        print(f"记录动作: {action}")
        
        try:
            monitor = sct.monitors[1]
        except Exception:
            monitor = sct.monitors[0]
            
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        screenshots.append(img)

# 同时启动鼠标监听和键盘监听
def start_listeners():
    with keyboard.Listener(on_press=on_press) as k_listener, \
         mouse.Listener(on_click=on_click) as m_listener:
        k_listener.join()
        m_listener.join()

start_listeners()

# ================= 核心：生成与自动打包 =================
def generate_and_build():
    print("[代码生成中] AI 正在编写无需外置依赖的 OCR 自动化脚本...")
    
    prompt = f'''
    我刚才执行了点击动作序列：{recorded_actions}。
    截图中的特定区域包含动态算术题。请通过视觉识别判断出算术题所在的屏幕区域，给出精确的 bbox (x1, y1, x2, y2) 坐标。
    请严格根据以下要求输出完整的代码，**不要输出任何解释性的 Markdown 文本**。
    '''
    
    if '1' in targets or '2' in targets:
        prompt += '''
        使用 <python> 和 </python> 标签包裹完整的 Python 代码。
        要求：
        1. 监听鼠标左键启动，开启死循环执行上述点击动作。
        2. 引入 io 和 PIL.ImageGrab。在循环体内使用 `ImageGrab.grab(bbox)` 重新截图。
        3. 引入 ddddocr。实例化 `ocr = ddddocr.DdddOcr(show_ad=False)`。利用 io.BytesIO() 将截图存为 PNG 格式的 bytes，并传入 `ocr.classification()` 进行离线识别。
        4. 使用正则过滤提取数字和运算符，使用 `eval()` 计算结果。
        5. 使用 `pyautogui.typewrite()` 输入结果，并模拟点击确认。纯本地运行，不要调用外部 OCR 引擎。
        '''
    if '3' in targets:
        prompt += '''
        使用 <pom> 和 </pom> 标签包裹完整的 Maven pom.xml 代码。
        使用 <java> 和 </java> 标签包裹完整的 Java 代码。
        要求：类名为 AutoWorker，实现死循环截图、算术题识别计算与输入逻辑。
        '''
    
    inputs = [prompt]
    if screenshots: inputs.append(screenshots[0])
    
    try:
        response = model.generate_content(inputs)
        result_text = response.text
    except Exception as e:
        print(f"[API 错误] {e}")
        return
    
    if '1' in targets or '2' in targets:
        py_match = re.search(r'<python>(.*?)</python>', result_text, re.DOTALL | re.IGNORECASE)
        if py_match:
            py_code = py_match.group(1).strip().replace('```python', '').replace('```', '')
            with open("AutoWorker.py", "w", encoding="utf-8") as f:
                f.write(py_code)
            
            if '2' in targets:
                print("[自动编译] 正在调用 PyInstaller 封装独立 EXE...")
                subprocess.run("pip install pyautogui pynput ddddocr Pillow pyinstaller >nul 2>&1", shell=True)
                subprocess.run("pyinstaller --onefile --noconsole AutoWorker.py", shell=True)
                
                if os.path.exists(r"dist\AutoWorker.exe"):
                    if os.path.exists("AutoWorker_Final.exe"): os.remove("AutoWorker_Final.exe")
                    os.rename(r"dist\AutoWorker.exe", "AutoWorker_Final.exe")
                
                subprocess.run("rmdir /s /q build dist __pycache__ 2>nul & del AutoWorker.spec 2>nul", shell=True)
                
                if '1' not in targets:
                    os.remove("AutoWorker.py")
                print("\n🎉 [大功告成] 子程序已成功出厂！")
                print("👉 请在当前目录查找并双击运行：AutoWorker_Final.exe")
        else:
            print("[警告] AI 格式错误。")
            
    if '3' in targets:
        pom_match = re.search(r'<pom>(.*?)</pom>', result_text, re.DOTALL | re.IGNORECASE)
        java_match = re.search(r'<java>(.*?)</java>', result_text, re.DOTALL | re.IGNORECASE)
        if pom_match and java_match:
            os.makedirs(r"JavaWorker\src\main\java", exist_ok=True)
            with open(r"JavaWorker\pom.xml", "w", encoding="utf-8") as f:
                f.write(pom_match.group(1).strip().replace('```xml', '').replace('```', ''))
            with open(r"JavaWorker\src\main\java\AutoWorker.java", "w", encoding="utf-8") as f:
                f.write(java_match.group(1).strip().replace('```java', '').replace('```', ''))
            print("👉 Java Maven 项目已生成至：./JavaWorker")

if __name__ == "__main__":
    generate_and_build()

import os
import time
import threading
import queue
import keyboard
import win32clipboard
import win32gui
import win32com.client
import pythoncom
import ctypes
from ctypes import wintypes
from PIL import ImageGrab
import pystray
from pystray import MenuItem as item
from PIL import Image
import logging
import uiautomation

APP_NAME = "Easycp"
VERSION = "1.0.0"
running = True
last_paste_time = 0
is_resending = False

paste_queue = queue.Queue()

log_dir = os.path.join(os.environ.get("APPDATA", ""), APP_NAME)
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "easypaste.log"), encoding="utf-8"),
        logging.StreamHandler()
    ]
)

WM_GETTEXT = 0x000D
WM_GETTEXTLENGTH = 0x000E

def get_clipboard_image():
    try:
        image = ImageGrab.grabclipboard()
        if isinstance(image, Image.Image):
            logging.info(f"检测到剪贴板图片: {image.size}")
            return image
        logging.debug("剪贴板中没有图片")
        return None
    except Exception as e:
        logging.error(f"获取剪贴板图片失败: {e}")
        return None

def get_window_text(hwnd):
    try:
        length = win32gui.SendMessage(hwnd, WM_GETTEXTLENGTH, 0, 0)
        if length <= 0:
            return ""
        buffer = ctypes.create_unicode_buffer(length + 1)
        win32gui.SendMessage(hwnd, WM_GETTEXT, length + 1, ctypes.byref(buffer))
        return buffer.value
    except Exception:
        return ""

def get_current_explorer_path():
    try:
        foreground_hwnd = win32gui.GetForegroundWindow()
        class_name = win32gui.GetClassName(foreground_hwnd)
        window_title = get_window_text(foreground_hwnd)
        
        logging.info(f"前台窗口: HWND={foreground_hwnd}, ClassName={class_name}, Title={window_title}")
        
        if class_name not in ('CabinetWClass', 'ExploreWClass'):
            logging.info(f"不是资源管理器窗口，类名: {class_name}")
            return None
        
        return get_path_by_uiautomation(foreground_hwnd) or get_path_by_shell_windows(foreground_hwnd)
    except Exception as e:
        logging.error(f"获取资源管理器路径失败: {e}")
        return None

def get_path_by_uiautomation(hwnd):
    try:
        window = uiautomation.ControlFromHandle(hwnd)
        
        address_bar = window.FindFirstChild(
            lambda c: c.ControlType == uiautomation.ControlType.EditControl and 
                      c.ClassName == 'Edit'
        )
        if address_bar:
            try:
                path = address_bar.GetValuePattern().Value
                if path and os.path.isdir(path):
                    logging.info(f"通过UI自动化获取路径: {path}")
                    return path
            except Exception:
                pass
        
        for child in window.FindAllChildren():
            try:
                if 'Address' in getattr(child, 'ClassName', ''):
                    for subchild in child.FindAllChildren():
                        text = getattr(subchild, 'Name', '')
                        if text and os.path.isdir(text):
                            logging.info(f"通过面包屑获取路径: {text}")
                            return text
            except Exception:
                pass
        
        return None
    except Exception as e:
        logging.error(f"UI自动化获取路径失败: {e}")
        return None

def get_path_by_shell_windows(foreground_hwnd):
    try:
        pythoncom.CoInitialize()
        shell = win32com.client.Dispatch("Shell.Application")
        
        for window in shell.Windows():
            try:
                window_hwnd = window.HWND
                if window_hwnd == foreground_hwnd:
                    url = window.LocationURL
                    if url.startswith("file:///"):
                        path = url[8:].replace("/", "\\")
                        if os.path.isdir(path):
                            logging.info(f"从Shell获取路径(匹配HWND): {path}")
                            pythoncom.CoUninitialize()
                            return path
            except Exception:
                pass
        
        for window in shell.Windows():
            try:
                url = window.LocationURL
                if url.startswith("file:///"):
                    path = url[8:].replace("/", "\\")
                    if os.path.isdir(path):
                        logging.info(f"从Shell获取路径(备用): {path}")
                        pythoncom.CoUninitialize()
                        return path
            except Exception:
                pass
        
        pythoncom.CoUninitialize()
        return None
    except Exception as e:
        logging.error(f"Shell获取路径失败: {e}")
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass
        return None

def save_image_to_folder(image, folder_path):
    if not os.path.exists(folder_path):
        logging.error(f"文件夹不存在: {folder_path}")
        return None
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}.png"
    filepath = os.path.join(folder_path, filename)
    
    counter = 1
    while os.path.exists(filepath):
        filename = f"screenshot_{timestamp}_{counter}.png"
        filepath = os.path.join(folder_path, filename)
        counter += 1
    
    try:
        image.save(filepath, "PNG")
        logging.info(f"图片保存成功: {filepath}")
        return filepath
    except Exception as e:
        logging.error(f"保存图片失败: {e}")
        return None

def process_paste_request():
    global is_resending
    
    image = get_clipboard_image()
    if not image:
        logging.info("剪贴板无图片，执行普通粘贴")
        is_resending = True
        time.sleep(0.05)
        keyboard.send('ctrl+v')
        time.sleep(0.05)
        is_resending = False
        return
    
    folder_path = get_current_explorer_path()
    if not folder_path:
        logging.info("当前不是资源管理器窗口，执行普通粘贴")
        is_resending = True
        time.sleep(0.05)
        keyboard.send('ctrl+v')
        time.sleep(0.05)
        is_resending = False
        return
    
    saved_path = save_image_to_folder(image, folder_path)
    if saved_path:
        time.sleep(0.1)
        keyboard.send('f5')

def worker_thread():
    pythoncom.CoInitialize()
    
    while running:
        try:
            request = paste_queue.get(timeout=0.1)
            if request == 'paste':
                process_paste_request()
            paste_queue.task_done()
        except queue.Empty:
            continue
    
    pythoncom.CoUninitialize()

def on_paste():
    global last_paste_time, is_resending
    
    if is_resending:
        return
    
    current_time = time.time()
    
    if current_time - last_paste_time < 0.3:
        return
    
    last_paste_time = current_time
    
    paste_queue.put('paste')

def setup_tray_icon():
    icon_image = Image.new('RGB', (64, 64), color=(30, 144, 255))
    
    def quit_action(icon, item):
        global running
        running = False
        icon.stop()
        keyboard.unhook_all()
    
    def show_log(icon, item):
        import subprocess
        try:
            log_path = os.path.join(log_dir, "easypaste.log")
            subprocess.Popen(f"notepad.exe {log_path}")
        except Exception as e:
            logging.error(f"打开日志文件失败: {e}")
    
    menu = (
        item('查看日志', show_log),
        item('退出', quit_action),
    )
    icon = pystray.Icon(APP_NAME, icon_image, APP_NAME, menu)
    
    return icon

def main():
    logging.info(f"{APP_NAME} v{VERSION} 启动")
    
    keyboard.add_hotkey('ctrl+v', on_paste, suppress=True)
    
    worker = threading.Thread(target=worker_thread, daemon=True)
    worker.start()
    
    icon = setup_tray_icon()
    
    icon_thread = threading.Thread(target=icon.run, daemon=True)
    icon_thread.start()
    
    while running:
        time.sleep(0.1)
    
    logging.info(f"{APP_NAME} 退出")

if __name__ == "__main__":
    main()
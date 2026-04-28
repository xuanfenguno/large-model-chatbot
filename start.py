import subprocess
import sys
import os
import threading
import time

base_dir = os.path.dirname(os.path.abspath(__file__))

print("=" * 50)
print("正在启动项目...")
print("=" * 50)

# 启动 Django 后端
backend = subprocess.Popen(
    [sys.executable, "manage.py", "runserver", "8080"],
    cwd=os.path.join(base_dir, "backend"),
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    encoding='utf-8'
)

# 等1秒确保后端先初始化
time.sleep(1)

# 启动 Vue 前端（Windows 需要 shell=True）
frontend = subprocess.Popen(
    ["npm", "run", "dev"],
    cwd=os.path.join(base_dir, "frontend"),
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    encoding='utf-8',
    shell=True
)

print(f"\n✅ 后端已启动 (PID: {backend.pid}) → http://127.0.0.1:8080/")
print(f"✅ 前端已启动 (PID: {frontend.pid}) → http://127.0.0.1:5173/")
print("\n按 Ctrl+C 或点击 PyCharm 红色停止按钮关闭所有服务\n")

def log_output(proc, tag):
    try:
        for line in proc.stdout:
            print(f"[{tag}] {line}", end="")
    except Exception:
        pass

# 开两个线程分别打印前后端日志
threading.Thread(target=log_output, args=(backend, "DJANGO"), daemon=True).start()
threading.Thread(target=log_output, args=(frontend, "VUE"), daemon=True).start()

# 保持主线程运行
try:
    backend.wait()
    frontend.wait()
except KeyboardInterrupt:
    print("\n\n正在关闭服务...")
    backend.terminate()
    frontend.terminate()
    print("已停止")
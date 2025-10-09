import subprocess
from pathlib import Path
import time
import psutil
import os
from blues_lib.sele.browser.driver.installer.CFTInstaller import CFTInstaller   

class DebugChrome:
  """
  一个用于启动和管理带有远程调试功能的 Chrome 实例的类。
  
  使用示例 (推荐):
  chrome_debugger = DebugChrome(chrome_path, port, user_dir)
  if chrome_debugger.start():
    # 在这里编写你的 Selenium 连接代码
    # ...
    chrome_debugger.close()

  使用示例 (上下文管理器，自动关闭):
  with DebugChrome(chrome_path, port, user_dir) as chrome_debugger:
    if chrome_debugger.is_running():
      # 在这里编写你的 Selenium 连接代码
      # ...
  """

  def __init__(self, chrome_path: str='', port: str = '9222', user_dir: str = ''):
    self.chrome_path = chrome_path or self.get_cft_chrome_path()
    self.port = port
    self.user_dir = user_dir
    self.chrome_proc = None
    
  def get_cft_chrome_path(self) -> str:
    cft_result:dict = CFTInstaller.install()
    if cft_result.get('error'):
      raise Exception(f"安装CFT ChromeDriver失败: {cft_result.get('error')}")

    # CFT chrome和driver必须匹配使用
    return Path(cft_result.get('chrome_path')).as_posix()

  def start(self) -> bool:
    """
    启动 Chrome 调试实例。

    Returns:
      bool: 如果启动成功返回 True，否则返回 False。
    """
    if self.is_running():
      print("[INFO] Chrome 实例已经在运行。")
      return True

    # 1. 检查 Chrome 可执行文件是否存在
    if not os.path.exists(self.chrome_path):
      print(f"错误: Chrome 可执行文件未找到于 '{self.chrome_path}'")
      return False

    # 2. 检查端口是否已被占用
    if self._is_port_in_use():
      print(f"错误: 端口 {self.port} 已被占用，无法启动 Chrome。")
      return False

    if self.user_dir:
      # 3. 尝试关闭使用相同用户数据目录的现有 Chrome 进程
      self._close_chromes_with_same_profile()

      # 4. 确保用户数据目录存在
      os.makedirs(self.user_dir, exist_ok=True)

    # 5. 构建并执行启动命令
    command = [
      self.chrome_path,
      f"--remote-debugging-port={self.port}",
    ]
    if self.user_dir:
      command.append(f"--user-data-dir={self.user_dir}")

    print(f"[INFO] 正在启动 Chrome 调试实例: {' '.join(command)}")
    try:
      self.chrome_proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
      )
      
      # 6. 等待 Chrome 启动并监听端口
      print(f"[INFO] 等待 Chrome 在端口 {self.port} 上开始监听...")
      if self._wait_for_port_to_listen(timeout=10):
        print(f"[INFO] Chrome 已成功启动并在端口 {self.port} 上监听。")
        return True
      else:
        print("[ERROR] 启动超时或 Chrome 未能在指定端口上监听。")
        self.close()
        return False

    except Exception as e:
      print(f"[ERROR] 启动 Chrome 时发生未知错误: {e}")
      self.close()
      return False

  def close(self):
    """关闭由该实例启动的 Chrome 进程。"""
    if self.chrome_proc and self.chrome_proc.poll() is None:
      print(f"[INFO] 正在关闭 Chrome 进程 (PID: {self.chrome_proc.pid})...")
      self.chrome_proc.terminate()
      try:
        self.chrome_proc.wait(timeout=10)
        print("[INFO] Chrome 已成功关闭。")
      except subprocess.TimeoutExpired:
        print("[WARN] Chrome 关闭超时，强制终止。")
        self.chrome_proc.kill()
    self.chrome_proc = None

  def is_running(self) -> bool:
    """检查 Chrome 进程是否正在运行。"""
    return self.chrome_proc is not None and self.chrome_proc.poll() is None

  # --- 上下文管理器支持 (可选，但推荐) ---
  def __enter__(self):
    self.start()
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    self.close()

  # --- 私有辅助函数 ---
  def _is_port_in_use(self) -> bool:
    try:
      port_int = int(self.port)
      for conn in psutil.net_connections(kind='inet'):
        if conn.laddr.port == port_int:
          return True
      return False
    except ValueError:
      print(f"错误: 无效的端口号 '{self.port}'")
      return True

  def _wait_for_port_to_listen(self, timeout: int = 10) -> bool:
    start_time = time.time()
    port_int = int(self.port)
    while time.time() - start_time < timeout:
      for conn in psutil.net_connections(kind='inet'):
        if conn.laddr.ip == '127.0.0.1' and conn.laddr.port == port_int and conn.status == 'LISTEN':
          return True
      time.sleep(0.5)
    return False

  def _close_chromes_with_same_profile(self):
    print(f"[INFO] 检查并关闭使用用户目录 '{self.user_dir}' 的现有 Chrome 进程...")
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
      try:
        if proc.info['name'] and 'chrome' in proc.info['name'].lower():
          cmdline = proc.info.get('cmdline', [])
          for i, arg in enumerate(cmdline):
            if arg.startswith('--user-data-dir'):
              dir_path = arg.split('=', 1)[1] if '=' in arg else cmdline[i+1]
              if dir_path == self.user_dir:
                print(f"[INFO] 发现并终止进程 {proc.info['pid']} (使用相同的用户目录)")
                proc.terminate()
                proc.wait(timeout=5)
                break
      except (psutil.NoSuchProcess, psutil.AccessDenied, IndexError):
        continue
import os,sys
from pathlib import Path
import re
import subprocess
from blues_lib.logger.LoggerFactory import LoggerFactory
from blues_lib.sele.browser.driver.installer.ChromeVersion import ChromeVersion
from blues_lib.config.ConfigManager import config
# 必须在安装前设置环境变量
LoggerFactory.set('WDM','info') # 注意名称是 WDM, 显示安装信息
# ✅ 旧版镜像变量（在 3.5.4 中完全支持）
os.environ["PLAYWRIGHT_DOWNLOAD_HOST"] = "https://npmmirror.com/mirrors/playwright"
from playwright.sync_api import sync_playwright

class DriverInstaller:
  _CONFIG_DRIVER_PATH = config.get("webdriver.executable_path")
  _CONFIG_CHROME_PATH = config.get("webdriver.sel_args.binary_location")
  _DEFAULT_CHROME_PATH:str = ChromeVersion.get_default_path()

  @classmethod
  def download_chromedriver(cls,mirror_host: str = "https://npmmirror.com/mirrors/playwright"):
    """
    下载 chromedriver（通过 Playwright 的 chromium 浏览器）
    
    Args:
        mirror_host: 镜像地址，如阿里云
    
    Returns:
        chromedriver 的本地路径 (str)
    """
    # 设置国内镜像
    os.environ["PLAYWRIGHT_DOWNLOAD_HOST"] = mirror_host

    with sync_playwright() as p:
        # 触发浏览器下载（如果未下载过）
        # 注意：这会下载整个 Chromium 浏览器（包含 chromedriver）
        browser_type = p.chromium
        browser_type.install()

    # Playwright 会把浏览器（含 driver）安装到缓存目录
    # 通常位于:
    #   macOS: ~/Library/Caches/ms-playwright/
    #   Linux: ~/.cache/ms-playwright/
    #   Windows: C:\Users\<user>\AppData\Local\ms-playwright\

    # 根据系统确定路径
    if sys.platform == "win32":
        cache_dir = Path.home() / "AppData" / "Local" / "ms-playwright"
    elif sys.platform == "darwin":
        cache_dir = Path.home() / "Library" / "Caches" / "ms-playwright"
    else:
        cache_dir = Path.home() / ".cache" / "ms-playwright"

    # Chromium 的目录名通常是 chromium-xxxxx
    chromium_dir = None
    for d in cache_dir.glob("chromium-*"):
        if d.is_dir():
            chromium_dir = d
            break

    if not chromium_dir:
        raise RuntimeError("未找到已下载的 Chromium 目录")

    # 拼接 chromedriver 路径
    if sys.platform == "win32":
        driver_path = chromium_dir / "chrome-win" / "chromedriver.exe"
    elif sys.platform == "darwin":
        driver_path = chromium_dir / "chrome-mac" / "Chromium.app" / "Contents" / "MacOS" / "Chromium"
    else:
        driver_path = chromium_dir / "chrome-linux" / "chromedriver"

    if not driver_path.exists():
        raise RuntimeError(f"未找到 chromedriver: {driver_path}")

    return str(driver_path)

  @classmethod
  def install(cls,driver_path:str='',chrome_path:str='')->str:
    # 一般不要传入或在config配置chrome path，因为manager会根据系统chrome路径下载对应版本的driver，如果手动指定了chrome_path要保证是最新版本chrome 
    if not driver_path:
      driver_path = cls._CONFIG_DRIVER_PATH
    if not chrome_path:
      chrome_path = cls._CONFIG_CHROME_PATH or cls._DEFAULT_CHROME_PATH
      
    if not driver_path or not chrome_path:
      raise ValueError("driver_path and chrome_path must be provided")

    if cls.need_to_install(driver_path,chrome_path):
      
      print(f"更新 WebDriver: {driver_path}...")
      
      
      # 从driver_path中提取目录路径
      target_dir = os.path.dirname(driver_path)
      
      # 确保目标目录存在
      os.makedirs(target_dir, exist_ok=True)
      
      # 创建 ChromeDriverManager 实例，不需要额外设置url参数
      driver_manager = ChromeDriverManager()
      
      # 设置自定义安装目录
      driver_manager.installation_path = target_dir
      
      # 执行安装
      installed_path = driver_manager.install()
      
      # 如果安装路径与目标路径不同，则复制驱动到目标位置
      if driver_path != installed_path:
        try:
          # 复制驱动文件到目标路径
          import shutil
          shutil.copy2(installed_path, driver_path)
          return driver_path
        except Exception:
          # 如果复制失败，返回原始安装路径
          return installed_path
      
      return installed_path
    return driver_path

  @classmethod 
  def need_to_install(cls,driver_path:str,chrome_path:str)->bool:
    """判断当前的 Chrome 与 WebDriver 版本是否匹配
    Args:
        chrome_path: Chrome 浏览器的路径
        driver_path: WebDriver 的路径
    Returns:
        bool: 如果需要安装，则返回 True；否则返回 False
    """
    # 检查路径是否存在
    if not os.path.exists(chrome_path):
      print(f"Chrome 路径不存在: {chrome_path}")
      return False

    if not os.path.exists(driver_path):
      print(f"WebDriver 路径不存在: {driver_path}")
      return True

    try:
      # 获取 Chrome 版本
      chrome_version = ChromeVersion.get(chrome_path)
      if not chrome_version:
        print(f"无法获取 Chrome 版本: {chrome_path}")
        return False
        
      # 获取 WebDriver 版本
      driver_version = cls.get_driver_version(driver_path)
      if not driver_version:
        print(f"无法获取 WebDriver 版本: {driver_path}")
        return True
        
      # 比较主版本号是否匹配
      chrome_main_version = cls._extract_main_version(chrome_version)
      driver_main_version = cls._extract_main_version(driver_version)
      if not driver_main_version:
        print(f"无法提取 WebDriver 主版本号: {driver_version}")
        return False
      
      if not chrome_main_version:
        print(f"无法提取 Chrome 主版本号: {chrome_version}")
        return False
      
      print(f"Chrome 版本: {chrome_version}")
      print(f"WebDriver 版本: {driver_version}")
      
      # 如果主版本号不匹配，则需要安装
      return chrome_main_version != driver_main_version
      
    except Exception as e:
      print(f"获取 Chrome 或 WebDriver 版本时出错: {e}")
      # 发生任何异常，都返回需要安装
      return False
     
  @classmethod
  def get_driver_version(cls, driver_path:str)->str:
    """获取 WebDriver 的版本号"""
    try:
      # 对于 chromedriver，使用 --version 参数获取版本
      cmd = f'"{driver_path}" --version'
      result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
      version_line = result.stdout.strip()
      
      # 提取版本号，如 "ChromeDriver 117.0.5938.92 (1e0e3868ee06e91ad636a874420e3ca3ae3756ac-refs/branch-heads/5938@{#1097})" -> "117.0.5938.92"
      version_match = re.search(r'\d+\.\d+\.\d+\.\d+', version_line)
      if version_match:
        return version_match.group(0)
      return ''
      
    except Exception:
      return ''
     
  @classmethod
  def _extract_main_version(cls, version:str)->str:
    """提取版本号的主版本部分，如 "117.0.5938.92" -> "117"
    
    注意：在 ChromeDriver 与 Chrome 版本匹配策略中，通常只需要主版本号一致即可。
    ChromeDriver 采用向后兼容的策略，同一主版本号的 ChromeDriver 通常可以兼容
    该主版本号下的所有次版本、修订版本和构建版本。这种策略可以减少不必要的更新频率。
    """
    try:
      # 拆分版本号，获取第一个数字作为主版本号
      main_version = version.split('.')[0]
      return main_version
    except Exception:
      return ''

import os
import platform
import requests
import zipfile
import shutil
import json
from blues_lib.config.ConfigManager import config

class CFTInstaller:
  '''
  Chrome for testing: https://googlechromelabs.github.io/chrome-for-testing/#stable
  此网页由google官方提供了国内可直接下载的 chrome chromedriver chrome-headless-shell zip下载链接
  - chrome不会自动升级
  - chromedriver与chrome版本号一致且完全匹配
  - 国内可以直接下载

  比如：Version: 141.0.7390.54 (r1509326)
  chrome下载地址：
  linux64 https://storage.googleapis.com/chrome-for-testing-public/141.0.7390.54/linux64/chrome-linux64.zip
  mac-arm64	https://storage.googleapis.com/chrome-for-testing-public/141.0.7390.54/mac-arm64/chrome-mac-arm64.zip
  mac-x64	https://storage.googleapis.com/chrome-for-testing-public/141.0.7390.54/mac-x64/chrome-mac-x64.zip
  win64	https://storage.googleapis.com/chrome-for-testing-public/141.0.7390.54/win64/chrome-win64.zip
  win32	https://storage.googleapis.com/chrome-for-testing-public/141.0.7390.54/win32/chrome-win32.zip
  
  chromedriver下载地址：
  linux64	https://storage.googleapis.com/chrome-for-testing-public/141.0.7390.54/linux64/chromedriver-linux64.zip
  mac-arm64	https://storage.googleapis.com/chrome-for-testing-public/141.0.7390.54/mac-arm64/chromedriver-mac-arm64.zip
  mac-x64	https://storage.googleapis.com/chrome-for-testing-public/141.0.7390.54/mac-x64/chromedriver-mac-x64.zip
  win64	https://storage.googleapis.com/chrome-for-testing-public/141.0.7390.54/win64/chromedriver-win64.zip
  win32	https://storage.googleapis.com/chrome-for-testing-public/141.0.7390.54/win32/chromedriver-win32.zip
  
  可以看到地址格式是规范的，只要有2个变量：
  - 系统
  - 版本号
  可以基于这些固定的下载地址，创建方法，按照版本号和系统下载到指定目录。
  '''

  _VERSION = '141.0.7390.54' # 下载目标版本
  _LOCATION = config.get("webdriver.cft")
  # 国内镜像地址（来自npmmirror镜像站）
  _MIRROR_URL = 'https://npmmirror.com/mirrors/chrome-for-testing'

  @classmethod
  def _check_installed(cls, version: str, location: str, os_type: str) -> tuple[bool, dict]:
    '''检查是否已存在相同版本的安装'''    
    installed_json_path = os.path.join(location, 'installed.json')
    if os.path.exists(installed_json_path):
      try:
        with open(installed_json_path, 'r', encoding='utf-8') as f:
          installed_info = json.load(f)
        
        # 检查版本是否一致，并且可执行文件是否存在
        if (installed_info.get('version') == version and 
            installed_info.get('os') == os_type and 
            os.path.exists(installed_info.get('chrome_path', '')) and 
            os.path.exists(installed_info.get('driver_path', ''))):
          return True, installed_info
      except (json.JSONDecodeError, Exception) as e:
        print(f"读取installed.json文件失败: {str(e)}，将重新安装。")
    return False, {}
  
  @classmethod
  def _create_or_clean_dir(cls, location: str) -> None:
    '''创建目录'''    
    if not os.path.exists(location):
      os.makedirs(location, exist_ok=True)
    else:
      cls._clean_dir(location)
      
  @classmethod  
  def _clean_dir(cls, location: str) -> None:
    '''清空目录'''    
    print(f"清空安装目录: {location}")
    for item in os.listdir(location):
      item_path = os.path.join(location, item)
      if os.path.isfile(item_path):
        os.remove(item_path)
      elif os.path.isdir(item_path):
        shutil.rmtree(item_path)
        
  @classmethod
  def _save_install_info(cls, location: str, install_info: dict) -> None:
    '''保存安装信息到json文件'''    
    installed_json_path = os.path.join(location, 'installed.json')
    try:
      with open(installed_json_path, 'w', encoding='utf-8') as f:
        json.dump(install_info, f, ensure_ascii=False, indent=2)
      print(f"已将安装信息保存到 {installed_json_path}")
    except Exception as e:
      print(f"保存installed.json文件失败: {str(e)}")
      
  @classmethod
  def install(cls, version: str = '', location: str = '') -> dict:
    f'''
    根据系统/版本下载chrome和chromedriver到指定目录

    @param {str} version : 版本号，如果为空使用 _VERSION
    @param {str} location : 下载目录的决定路径，如果为空使用 _LOCATION
    
    @returns {dict} : 包含安装路径信息的字典
    '''
    try:
      # 使用提供的值或默认值
      version = version if version else cls._VERSION
      location = location if location else cls._LOCATION
      os_type = cls.get_os()
      
      # 验证系统类型
      valid_os_types = ['linux64', 'win64', 'win32', 'mac-x64', 'mac-arm64']
      if os_type not in valid_os_types:
        raise ValueError(f"不支持的系统类型: {os_type}")
      
      # 检查是否已经安装过相同版本
      is_installed, installed_info = cls._check_installed(version, location, os_type)
      if is_installed:
        print(f"已检测到版本 {version} 的Chrome和ChromeDriver已安装，直接返回安装信息。")
        return installed_info
      
      # 创建下载目录或清空目录
      cls._create_or_clean_dir(location)

      # 构建下载URL - 优先使用国内镜像地址
      print(f"使用国内镜像地址下载: {cls._MIRROR_URL}")
      chrome_url = f"{cls._MIRROR_URL}/{version}/{os_type}/chrome-{os_type}.zip"
      driver_url = f"{cls._MIRROR_URL}/{version}/{os_type}/chromedriver-{os_type}.zip"
      
      # 下载并解压Chrome
      chrome_dir = os.path.join(location, f"chrome-{os_type}")
      cls._download_extract(chrome_url, location, f"chrome-{os_type}.zip", chrome_dir)
      
      # 下载并解压ChromeDriver
      driver_dir = os.path.join(location, f"chromedriver-{os_type}")
      cls._download_extract(driver_url, location, f"chromedriver-{os_type}.zip", driver_dir)
      
      # 查找可执行文件
      chrome_exe = cls._find_exe(chrome_dir, "chrome")
      driver_exe = cls._find_exe(driver_dir, "chromedriver")
      
      # 构建安装信息
      install_info = {
        'location': location,
        'version': version,
        'os': os_type,
        'chrome_path': chrome_exe,
        'driver_path': driver_exe
      }
      
      # 保存安装信息
      cls._save_install_info(location, install_info)
      
      return install_info
      
    except Exception as e:
      print(f"安装失败: {str(e)}")
      return {
        'error': str(e)
      }
  
  @classmethod
  def get_os(cls)->str:
    f'''
    获取当前系统标识: 可用值有：linux64 win64 win32 mac-x64 mac-arm64
    @returns {str} : 系统标识字符串
    '''
    system = platform.system().lower()
    architecture = platform.architecture()[0]
    machine = platform.machine().lower()
    
    # 处理Windows系统
    if system == 'windows':
      if '64' in architecture or 'amd64' in machine or 'x86_64' in machine:
        return 'win64'
      else:
        return 'win32'
    
    # 处理macOS系统
    elif system == 'darwin':
      if 'arm' in machine or 'aarch64' in machine:
        return 'mac-arm64'
      else:
        return 'mac-x64'
    
    # 处理Linux系统
    elif system == 'linux':
      if '64' in architecture or 'amd64' in machine or 'x86_64' in machine:
        return 'linux64'
      else:
        # 假设Linux只有64位版本可用
        return 'linux64'
    
    # 不支持的系统
    else:
      raise NotImplementedError(f"不支持的操作系统: {system}")
  
  @classmethod
  def _download_extract(cls, url: str, save_dir: str, zip_filename: str, extract_dir: str):
    '''下载并解压文件'''    
    # 下载文件
    zip_path = os.path.join(save_dir, zip_filename)
    print(f"下载 {url} 到 {zip_path}")
    
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(zip_path, 'wb') as f:
      for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)
    
    # 解压文件
    print(f"解压 {zip_path} 到 {extract_dir}")
    
    if os.path.exists(extract_dir):
      shutil.rmtree(extract_dir)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
      zip_ref.extractall(save_dir)
    
    # 清理zip文件
    os.remove(zip_path)
  
  @classmethod
  def _find_exe(cls, directory: str, base_name: str) -> str:
    '''在目录中查找可执行文件'''    
    is_windows = platform.system() == 'Windows'
    extension = '.exe' if is_windows else ''
    
    for root, _, files in os.walk(directory):
      for file in files:
        if is_windows:
          # Windows下不区分大小写
          if file.lower() == base_name.lower() + extension:
            return os.path.join(root, file)
        else:
          if file == base_name + extension:
            # 在非Windows系统上设置可执行权限
            exe_path = os.path.join(root, file)
            os.chmod(exe_path, 0o755)
            return exe_path
    
    raise FileNotFoundError(f"未找到 {base_name} 可执行文件")
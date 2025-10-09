import os
from blues_lib.type.factory.Factory import Factory
from blues_lib.sele.browser.chrome.Chrome import Chrome
from blues_lib.type.file.File import File

class ChromeFactory(Factory):
  
  _DEFAULT_MODE = 'standard'

  def __init__(self,
      std_args=None, # {dict} standard args
      exp_args=None, # {dict} experimentalargs
      cdp_args=None, # {dict} chrome devtools protocal args
      sel_args=None, # {dict} selenium args
      ext_args=None, # {dict} extension args
    ):
    self._std_args = std_args or []
    self._exp_args = exp_args or {}
    self._cdp_args = cdp_args or {}
    self._sel_args = sel_args or {}
    self._ext_args = ext_args or {}
    
  def create(self,driver_config:dict|None=None):
    '''
    根据配置创建Chrome实例
    
    :param driver_config: 驱动配置，包含以下键值对：
      - headless: 是否无头模式，默认False
      - imageless: 是否无图模式，默认False

    :return: Chrome实例
    '''
    conf:dict = driver_config or {}
    # 默认配置
    self._set_infoless()
    self._set_download()
    
    # 加载策略
    if strategy := conf.get('strategy'):
      self._set_strategy(strategy)

    # 无图
    if conf.get('imageless',False):
      self._set_imageless()

    # 无头
    if conf.get('headless',False):
      self._set_headless()
      
    # 移动设备
    if conf.get('mobile',False):
      self._set_mobile()
      
    # debug
    if conf.get('debug',False):
      self._set_debugger(conf)

    return self._create(conf)
    
  def _create(self,driver_config:dict):
    # 默认使用 undetectd_chromedriver
    executable_path:str = driver_config.get('executable_path','')
    undetected:bool = driver_config.get('undetected',True) 
    page_load_timeout:int|None = driver_config.get('page_load_timeout')
    script_timeout:int|None = driver_config.get('script_timeout')

    chrome = Chrome(
      self._std_args,
      self._exp_args,
      self._cdp_args,
      self._sel_args,
      self._ext_args,
      executable_path,
      undetected,
      page_load_timeout,
      script_timeout)

    # 会打开一个新的窗口在前面，但url还是在旧的实例访问，待解决
    if driver_config.get('debug',False):
      chrome.interactor.window.switch_to_latest()

    return chrome
  
  def _set_headless(self):
    self._std_args.append('--headless')

  def _set_infoless(self):
    # 禁止显示自动化提示信息，如："Chrome 正在被自动化测试软件控制"
    self._std_args.append('--disable-infobars')

  def _set_imageless(self):
    # 禁用图片加载。在爬虫或测试中，禁用图片可以加快页面加载速度。完全禁用所有图片（包括 CSS 背景）
    self._std_args.append('--blink-settings=imagesEnabled=false')
    
  def _set_strategy(self,strategy:str='normal'):
    # 设置页面加载策略， 可选值有：'normal' -默认 'eager' 'none'
    self._sel_args['page_load_strategy'] = strategy.lower()  

  def _set_mobile(self):
    # 模拟移动设备
    cdp_args = {
      'Emulation.setDeviceMetricsOverride': {
        "width": 430,
        "height": 932,
        "deviceScaleFactor": 3.0,  # iPhone 12 Pro 的缩放比例
        "mobile": True,
        "screenOrientation": {"angle": 0, "type": "portraitPrimary"}
      },
      'Emulation.setUserAgentOverride': {
        "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
      },
    }
    self._cdp_args.update(cdp_args)

  def _set_debugger(self,driver_config:dict):
    # 连接已有的 Chrome 实例
    addr = driver_config.get('debugger_address') or '127.0.0.1'
    port = driver_config.get('debugger_port') or '9222'
    self._sel_args.update({
      'debugger_address' : '%s:%s' % (addr,port)
    })
    
  def _set_download(self):
    # 设置下载目录
    download_dir = os.path.normpath(File.get_dir_path('browser_download'))
    download_prefs = {
      'download.default_directory':download_dir, # 下载目录, 默认 "C:\\Users\\Downloads"
      'download.prompt_for_download':False, # 是否提示下载路径, False（禁用提示，直接下载到默认目录）
      'download.directory_upgrade':True, # 自动升级下载目录权限
      'download.extensions_to_open':'', # 移除所有直接打开文件类型, such as: "pdf"（直接打开 PDF 文件，不下载）
      'safebrowsing.enabled':False, # 启用安全浏览（屏蔽危险文件）
      "safebrowsing.disable_download_protection": True,   # 允许下载"危险文件"（如 .exe）
    }
    prefs = self._exp_args.get('prefs') or {}
    prefs.update(download_prefs)
    self._exp_args.update({
      'prefs': prefs,
    })
    
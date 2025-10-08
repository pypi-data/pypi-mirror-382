import psutil
from blues_lib.type.factory.Factory import Factory
from blues_lib.sele.browser.chrome.Chrome import Chrome

class ChromeFactory(Factory):
  
  _DEFAULT_MODE = 'standard'

  def __init__(self,
      std_args=None, # {dict} standard args
      exp_args=None, # {dict} experimentalargs
      cdp_args=None, # {dict} chrome devtools protocal args
      sel_args=None, # {dict} selenium args
      ext_args=None, # {dict} extension args
      executable_path=None, # {str} driver.exe path: 'env' - using the env; 'xxx' - the local path; None - using the driver manager
      udc=True, # {bool} 是否使用 undetected_chromedriver
      page_load_timeout=None, # {int} 页面加载超时时间
    ):
    self._std_args = std_args or []
    self._exp_args = exp_args or {}
    self._cdp_args = cdp_args or {}
    self._sel_args = sel_args or {}
    self._ext_args = ext_args or {}
    self._executable_path = executable_path
    self._udc = udc
    self._page_load_timeout = page_load_timeout
    
  def create(self,mode:str="",headless=False,**kwargs):
    mode = mode or self._DEFAULT_MODE
    # override
    if headless:
      self._set_headless()

    return super().create(mode,**kwargs)
    
  def create_standard(self):
    return Chrome(
      self._std_args,
      self._exp_args,
      self._cdp_args,
      self._sel_args,
      self._ext_args,
      self._executable_path,
      self._udc,
      self._page_load_timeout)
  
  def create_mobile(self):
    self._set_mobile()
    return self.create_standard()
  
  def create_debugger(self,addr:str='',port:str=''):
    # selenium会基于手动chrome创建一个新的实例，不会关闭手动chrome
    self._set_debugger(addr,port)
    chrome = self.create_standard()
    chrome.interactor.window.switch_to_latest()
    return chrome
  
  def _set_headless(self):
    self._std_args.append('--headless')
    
  def _set_mobile(self):
    self._std_args.append("--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1")
    self._cdp_args['Emulation.setDeviceMetricsOverride'] = {
      "width": 390,
      "height": 844,
      "deviceScaleFactor": 3.0,  # iPhone 12 Pro 的缩放比例
      "mobile": True,
      "screenOrientation": {"angle": 0, "type": "portraitPrimary"}
    }

  def _set_debugger(self,addr:str,port:str):
    addr = addr or "127.0.0.1"
    port = port or "9222"
    self._sel_args.update({
      'debugger_address' : '%s:%s' % (addr,port)
    })
    
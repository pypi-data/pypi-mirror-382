from selenium import webdriver
import undetected_chromedriver as udc_driver
from selenium.webdriver.chrome.service import Service
from pathlib import Path
from blues_lib.sele.browser.Browser import Browser
from blues_lib.sele.browser.chrome.OptionsCreator import OptionsCreator
from blues_lib.sele.browser.driver.installer.CFTInstaller import CFTInstaller   

class Chrome(Browser):
  
  _DEFAULT_PAGE_LOAD_TIMEOUT = 60 # 页面加载超时时间
  _DEFAULT_SCRIPT_TIMEOUT = 60 # 脚本执行超时时间

  def __init__(self,
      std_args=None, # {dict} standard args
      exp_args=None, # {dict} experimentalargs
      cdp_args=None, # {dict} chrome devtools protocal args
      sel_args=None, # {dict} selenium args
      ext_args=None, # {dict} extension args
      executable_path=None, # {str} driver.exe path: 'env' - using the env; 'xxx' - the local path; None - using the driver manager
      undetected=True, # {bool} 是否使用 undetected_chromedriver
      page_load_timeout=None, # {int} 页面加载超时时间
      script_timeout=None, # {int} 脚本执行超时时间
    ):
    self._std_args = std_args or {}
    self._exp_args = exp_args or {}
    self._cdp_args = cdp_args or {}
    self._sel_args = sel_args or {}
    self._ext_args = ext_args or {}
    self._executable_path = executable_path
    self._undetected = undetected
    self._page_load_timeout = page_load_timeout or self._DEFAULT_PAGE_LOAD_TIMEOUT
    self._script_timeout = script_timeout or self._DEFAULT_SCRIPT_TIMEOUT

    driver = self._get_driver()
    super().__init__(driver)

  def _get_driver(self):
    # 设置CFT driver和chrome路径
    self._set_cft()
    creator = OptionsCreator(self._std_args,self._exp_args,self._cdp_args,self._sel_args,self._ext_args,self._undetected)
    options = creator.create()

    if self._undetected:
      # udc的driver path入参与webdriver不同，不需要Service对象, udc设置了所有常用配置，一般不再需要传入其他options
      driver = udc_driver.Chrome( driver_executable_path = self._executable_path, options = options)
    else:
      service = Service(self._executable_path) 
      driver = webdriver.Chrome( service = service, options = options)

    # cdp must be set after driver created
    creator.set_cdp(driver)
    # set the page load timeout
    driver.set_page_load_timeout(self._page_load_timeout)
    driver.set_script_timeout(self._script_timeout)

    return driver
  
  def _set_cft(self):
    if not self._executable_path:
      cft_result:dict = CFTInstaller.install()
      if cft_result.get('error'):
        raise Exception(f"安装CFT ChromeDriver失败: {cft_result.get('error')}")

      # CFT chrome和driver必须匹配使用
      driver_path = Path(cft_result.get('driver_path')).as_posix()
      chrome_path = Path(cft_result.get('chrome_path')).as_posix()
      self._executable_path = driver_path
      self._sel_args['binary_location'] = chrome_path
  

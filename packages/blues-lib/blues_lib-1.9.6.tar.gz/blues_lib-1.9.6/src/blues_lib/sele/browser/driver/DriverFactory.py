from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from blues_lib.sele.browser.driver.args.ChromeArgsFactory import ChromeArgsFactory
from blues_lib.sele.browser.driver.installer.CFTInstaller import CFTInstaller   

class DriverFactory():
  __page_load_timeout = 20 # 页面加载超时时间
  
  def __init__(self,
    std_args=None,
    exp_args=None,
    cdp_args=None,
    sel_args=None,
    ext_args=None,
    executable_path=None,
    web_driver=None,
    capabilities=None,
    ):
    '''
    @param {dict} std_args
    @param {dict} exp_args
    @param {dict} cdp_args
    @param {dict} sel_args
    @param {dict} ext_args
    @param {dict} grid_capabilities : the grid remote capability dict
    '''
    self._std_args = std_args or {}
    self._exp_args = exp_args or {}
    self._cdp_args = cdp_args or {}
    self._sel_args = sel_args or {}
    self._ext_args = ext_args or {}
    self.__arg_dict = None

    self.__executable_path = executable_path
    self.__web_driver = web_driver if web_driver else webdriver
    self.__capabilities = capabilities
    
  def create(self):
    # 没有指定driver位置，则自动安装并获取CFT安装信息
    if not self.__executable_path:
      cft_result:dict = CFTInstaller.install()
      if cft_result.get('error'):
        raise Exception(f"安装CFT ChromeDriver失败: {cft_result.get('error')}")

      # CFT chrome和driver必须匹配使用
      driver_path = Path(cft_result.get('driver_path'))
      chrome_path = Path(cft_result.get('chrome_path'))

      self.__executable_path = driver_path.as_posix()
      self._sel_args['binary_location'] = chrome_path.as_posix()

    # binary_location不是必须的，不使用CFT时可以不指定，会自动按系统默认chrome路径查找 （或者按环境变量）
    print(f'sel_args: {self._sel_args}')
    self.__arg_dict = ChromeArgsFactory(self._std_args,self._exp_args,self._cdp_args,self._sel_args,self._ext_args).create()
    service = Service(self.__executable_path) 
    return self.__get_driver(service)

  def __get_options(self):
    options = Options()
    self.__set_options(options)
    self.__set_capability(options)
    options.binary_location = self._sel_args.get('binary_location')
    return options
  
  def __set_capability(self,chrome_options):
    if self.__capabilities:
      for key,value in self.__capabilities.items():
        chrome_options.set_capability(key,value)
    
  def __get_driver(self,service=None):
    options = self.__get_options()
    if self.__capabilities:
      return self.__get_remote_driver(options)
    else:
      return self.__get_local_driver(service,options)

  def __get_local_driver(self,service,options):
    # use the UDC first, and use it's all default settings
    if self.__is_udc_driver(self.__web_driver):
      # selenium >= 4.1 use the path
      return self.__web_driver.Chrome(driver_executable_path=service.path)

    if service:
      driver =  self.__web_driver.Chrome( service = service, options = options)
    else:
      driver =  self.__web_driver.Chrome( options = options)

    self.__set_cdp(driver,self.__arg_dict['cdp'])

    driver.set_page_load_timeout(self.__page_load_timeout)

    return driver
  
  def __is_udc_driver(self,driver):
    # 检查类名是否包含 UDC 特征
    class_module = getattr(driver.__class__, '__module__', '')
    driver_name = getattr(driver, '__name__', '')
    name = "undetected_chromedriver"
    return name in class_module or name in driver_name

  def __get_remote_driver(self,options):
    driver = self.__web_driver.Remote(
      command_executor = self.__executable_path,
      options = options
    )

    driver.set_page_load_timeout(self.__page_load_timeout)

    return driver

  def __set_options(self,options):
    self.__set_std(options,self.__arg_dict['std'])
    self.__set_exp(options,self.__arg_dict['exp'])
    self.__set_ext(options,self.__arg_dict['ext'])
    self.__set_sel(options,self.__arg_dict['sel'])
    
  def __set_std(self,options,args):
    if args:
      for value in args:
        options.add_argument(value)

  def __set_exp(self,options,args):
    if args:
      for key,value in args.items():
        options.add_experimental_option(key,value)

  def __set_cdp(self,driver,args):
    if args:
      for key,value in args.items():
        driver.execute_cdp_cmd(key,value)

  def __set_ext(self,options,args):
    if args:
      for value in args:
        options.add_extension(value)

  def __set_sel(self,options,args):
    print(f'sel_args: {args}')
    if args:
      for key,value in args.items():
        # just set as the options's attr
        setattr(options,key,value)
        
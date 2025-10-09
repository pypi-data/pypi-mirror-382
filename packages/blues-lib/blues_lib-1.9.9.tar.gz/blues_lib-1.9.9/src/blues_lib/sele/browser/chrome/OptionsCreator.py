from selenium.webdriver.chrome.options import Options
from blues_lib.sele.browser.driver.args.ChromeArgsFactory import ChromeArgsFactory

class OptionsCreator():
  '''
  创建自定义options
  '''
  
  def __init__(self,
    std_args=None, # {list} standard args
    exp_args=None, # {dict} experimental args
    cdp_args=None, # {dict} chrome devtools protocal args
    sel_args=None, # {dict} selenium args
    ext_args=None, # {dict} extension args
    undetected=True, # {bool} 是否使用 undetected_chromedriver
    ):
    self._std_args = std_args or []
    self._exp_args = exp_args or {}
    self._cdp_args = cdp_args or {}
    self._sel_args = sel_args or {}
    self._ext_args = ext_args or {}
    self._undetected = undetected
    self._arg_dict = None
    
  def create(self):
    factory = ChromeArgsFactory(self._std_args,self._exp_args,self._cdp_args,self._sel_args,self._ext_args)
    self._arg_dict = factory.format() if self._undetected else factory.create()

    options = Options()
    self._set_std(options)
    self._set_exp(options)
    self._set_ext(options)
    self._set_sel(options)
    return options
  
  def is_undetected_driver(self,driver):
    # 检查类名是否包含 UDC 特征
    class_module = getattr(driver.__class__, '__module__', '')
    driver_name = getattr(driver, '__name__', '')
    name = "undetected_chromedriver"
    return name in class_module or name in driver_name

  def _set_std(self,options):
    if args:= self._arg_dict.get('std'):
      for value in args:
        options.add_argument(value)

  def _set_exp(self,options):
    if args:= self._arg_dict.get('exp'):
      for key,value in args.items():
        options.add_experimental_option(key,value)

  def _set_ext(self,options):
    if args:= self._arg_dict.get('ext'):
      for value in args:
        options.add_extension(value)

  def _set_sel(self,options):
    if args:= self._arg_dict.get('sel'):
      for key,value in args.items():
        # just set as the options's attr
        setattr(options,key,value)
        
  def set_cdp(self,driver):
    # 此方法要在driver创建后调用,才能生效
    if args:= self._arg_dict.get('cdp'):
      for key,value in args.items():
        driver.execute_cdp_cmd(key,value)
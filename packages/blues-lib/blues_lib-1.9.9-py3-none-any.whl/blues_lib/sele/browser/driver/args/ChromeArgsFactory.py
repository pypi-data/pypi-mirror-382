from .ChromeStdArgs import ChromeStdArgs   
from .ChromeExpArgs import ChromeExpArgs   
from .ChromeExtArgs import ChromeExtArgs   
from .ChromeCDPArgs import ChromeCDPArgs
from .ChromeSelArgs import ChromeSelArgs

class ChromeArgsFactory:
  
  def __init__(self,std_args=None,exp_args=None,cdp_args=None,sel_args=None,ext_args=None):
    self.__std_args = std_args or []
    self.__exp_args = exp_args or {}
    self.__cdp_args = cdp_args or {}
    self.__sel_args = sel_args or {}
    self.__ext_args = ext_args or {}

  def create(self)->dict:
    std_args = ChromeStdArgs(self.__std_args).get()
    exp_args = ChromeExpArgs(self.__exp_args).get()
    cdp_args = ChromeCDPArgs(self.__cdp_args).get()
    sel_args = ChromeSelArgs(self.__sel_args).get()
    ext_args = ChromeExtArgs(self.__ext_args).get()

    # connet to a exist browser, don't support experimental options setting 需要在Driver创建时设置，此种情况下仅连接 
    if sel_args.get('debugger_address'):
      std_args = None # has no effect
      exp_args = None # must remove

    return {
      'std':std_args,
      'exp':exp_args,
      'cdp':cdp_args,
      'sel':sel_args,
      'ext':ext_args,
    }

  def format(self)->dict:
    # 只返回结构，不设置任何默认配置
    return {
      'std':self.__std_args,
      'exp':self.__exp_args,
      'cdp':self.__cdp_args,
      'sel':self.__sel_args,
      'ext':self.__ext_args,
    }
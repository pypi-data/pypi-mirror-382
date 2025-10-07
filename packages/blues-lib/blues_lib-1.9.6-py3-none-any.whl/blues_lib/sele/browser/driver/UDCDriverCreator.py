import undetected_chromedriver as udc
from .DriverCreator import DriverCreator

class UDCDriverCreator(DriverCreator):
  
  def __init__(self,
      std_args=None,
      exp_args=None,
      cdp_args=None,
      sel_args=None,
      ext_args=None,
      executable_path=None
    ):
    # pass the wire webdriver
    super().__init__(
        std_args,
        exp_args,
        cdp_args,
        sel_args,
        ext_args,
        executable_path,
        udc
      )
    
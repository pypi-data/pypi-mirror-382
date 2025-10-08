from selenium.webdriver.remote.webelement import WebElement
from blues_lib.sele.waiter.EC import EC   
from blues_lib.sele.waiter.deco.QuerierDeco import QuerierDeco
from blues_lib.sele.element.Finder import Finder   

# 提供元素选择功能
class Querier():

  def __init__(self,driver,timeout=8):
    self.__driver = driver
    self.__ec = EC(driver) 
    self.__finder = Finder(driver) 
    self.__timeout = timeout or 5

  def setTimeout(self,timeout=5):
    '''
    Adjust the timeout in runtime
    '''
    self.__timeout = timeout

  @QuerierDeco('query')
  def query(self,target_CS_WE,parent_CS_WE=None,timeout=5)->WebElement|None:
    '''
    Wait and get the element from document or parent element
    Parameter:
      target_CS_WE {str|WebElement} : the target element's css selector or WebElement
      parent_CS_WE {str|WebElement} : the parent element's css selector or WebElement
      timeout {int} : Maximum waiting time (s)
    Returns:
      {WebElement|None} 
    '''
    if not target_CS_WE:
      return None

    if not parent_CS_WE:
      return self.__query(target_CS_WE,timeout)

    parent:WebElement|None = self.__query(parent_CS_WE,timeout) 
    if parent:
      return self.__finder.find(target_CS_WE,parent)
    else:
      return self.__query(target_CS_WE,timeout)

  @QuerierDeco('query_all')
  def query_all(self,target_CS_WE,parent_CS_WE=None,timeout=5)->list[WebElement]|None:
    '''
    Wait and get elements from document or parent element
    Parameter:
      target_CS_WE {str|WebElement} : the target element's css selector or WebElement
      parent_CS_WE {str|WebElement} : the parent element's css selector or WebElement
      timeout {int} : Maximum waiting time (s)
    Returns:
      {list<WebElement>} 
    '''
    if not target_CS_WE:
      return None
    
    if not parent_CS_WE:
      return self.__query_all(target_CS_WE,timeout)

    parent:WebElement|None = self.__query(parent_CS_WE,timeout)
    if parent:
      return self.__finder.find_all(target_CS_WE,parent)
    else:
      return self.__query_all(target_CS_WE,timeout)

  def __query(self,target_CS_WE,timeout=5,parent_CS_WE=None)->WebElement|None:
    '''
    Wait and Get the target WebElement
    Parameter:
      target_CS_WE {str|WebElement} : the target element's css selector or WebElement
      timeout {int} : Maximum waiting time (s)
    Returns:
      {WebElement|None} 
    '''
    if isinstance(target_CS_WE,WebElement):
      return target_CS_WE
    
    wait_time = timeout or self.__timeout
    return self.__ec.to_be_presence(target_CS_WE,wait_time,parent_CS_WE)

  def __query_all(self,target_CS_WE,timeout=5,parent_CS_WE=None)->list[WebElement]|None:
    '''
    Wait and Get the target WebElements
    Parameter:
      target_CS_WE {str|WebElement} : css selector or web element
      timeout {int} : Maximum waiting time (s)
    Returns:
      {list<WebElement>} 
    '''
    if isinstance(target_CS_WE,WebElement):
      return [target_CS_WE]

    wait_time = timeout or self.__timeout
    return self.__ec.all_to_be_presence(target_CS_WE,wait_time,parent_CS_WE)

   

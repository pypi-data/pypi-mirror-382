from .deco.InfoKeyDeco import InfoKeyDeco
from .deco.InfoDeco import InfoDeco

from blues_lib.sele.waiter.Querier import Querier  

class Info():

  def __init__(self,driver):
    self.__driver = driver
    self.__querier = Querier(driver,5) 

  # === part 2:  get element info === # 
  @InfoKeyDeco('get_prop')
  def get_prop(self,target_CS_WE,key,parent_CS_WE=None,timeout=5):
    '''
    与attribute区分，用于获取DOM 对象在内存中的当前属性。它反映的是 **“状态”**
    常用于：value，checked，selected 等。
    一般也会同步到attribute上，所以用get_attribute也可以获取，但部分属性值有所不同
    - prop获取checked状态返回bool，但attr返回字符串checked或者None
    '''
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    if not web_element:
      return None
    return web_element.get_property(key)

  @InfoKeyDeco('get_attr')
  def get_attr(self,target_CS_WE,key,parent_CS_WE=None,timeout=5):
    '''
    Fetching Attributes or Properties ： 获取的是 HTML 标签上的特性（Attribute）。
    Parameter:
      target_CS_WE {str|WebElement} : css selector or web_element
    key {str} : the element's attribute or property key, like:
      - 'innerHTML' 
      - 'innerText'
      - 'name'
    Returns:
      {str}
    '''
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    if not web_element:
      return None
    return web_element.get_attribute(key)

  @InfoDeco('get_value')
  def get_value(self,target_CS_WE,parent_CS_WE=None,timeout=5):
    '''
    Fetching form element's value ： 
    Parameter:
      target_CS_WE {str|WebElement} : css selector or web_element
    Returns:
      {str}
    '''
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    if not web_element:
      return None
    return self.get_attr(web_element,'value')

  @InfoDeco('get_html')
  def get_html(self,target_CS_WE,parent_CS_WE=None,timeout=5):
    '''
    Fetching element's text node value
    Parameter:
      target_CS_WE {str|WebElement} : css selector or web_element
    Returns:
      {str}
    '''
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    if not web_element:
      return None
    return self.get_attr(web_element,'innerHTML')

  @InfoDeco('get_outer_html')
  def get_outer_html(self,target_CS_WE,parent_CS_WE=None,timeout=5):
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    if not web_element:
      return None
    return self.get_attr(web_element,'outerHTML')

  @InfoDeco('get_text')
  def get_text(self,target_CS_WE,parent_CS_WE=None,timeout=5):
    '''
    Fetching element's text node value
    Parameter:
      target_CS_WE {str|WebElement} : css selector or web_element
    Returns:
      {str}
    '''
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    if not web_element:
      return None
    return web_element.text

  @InfoDeco('get_tag_name')
  def get_tag_name(self,target_CS_WE,parent_CS_WE=None,timeout=5):
    '''
    Fetching element's tag name
    Parameter:
      target_CS_WE {str|WebElement} : css selector or web_element
    Returns:
      {str}
    '''
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    if not web_element:
      return None
    return web_element.tag_name

  @InfoKeyDeco('get_css')
  def get_css(self,target_CS_WE,key,parent_CS_WE=None,timeout=5):
    '''
    Fetching element's css attr's value
    Parameter:
      target_CS_WE {str|WebElement} : css selector or web_element
    Returns:
      {str}
    '''
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    if not web_element:
      return None
    return web_element.value_of_css_property(key)

  @InfoDeco('get_size')
  def get_size(self,target_CS_WE,parent_CS_WE=None,timeout=5):
    '''
    Fetching element's size
    Parameter:
      target_CS_WE {str|WebElement} : css selector or web_element
    Returns:
      {dict}
    '''
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    if not web_element:
      return None
    rect = web_element.rect
    return {
        'width':round(rect['width']),
        'height':round(rect['height']),
    }

  @InfoDeco('get_position')
  def get_position(self,target_CS_WE,parent_CS_WE=None,timeout=5):
    '''
    Fetching element's position
    Parameter:
      target_CS_WE {str|WebElement} : css selector or web_element
    Returns:
      {dict}
    '''
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    if not web_element:
      return None
    rect = web_element.rect
    return {
        'x':round(rect['x']),
        'y':round(rect['y']),
    }


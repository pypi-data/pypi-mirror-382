import sys,os,re

from blues_lib.sele.waiter.Querier import Querier  
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin

class Wheel():
  '''
  A representation of a scroll wheel input device for interacting with a web page.
  '''
  def __init__(self,driver):
    self.__driver = driver
    self.__querier = Querier(driver)
    self.__chains = ActionChains(driver)

  def scroll_to_element(self,target_CS_WE,parent_CS_WE=None):
    '''
    The actions class does not automatically scroll the target element into view,
    So this method will need to be used if elements are not already inside the viewport.
    The viewport will be scrolled so the bottom of the element is at the bottom of the screen.
    Parameter:
      target_CS_WE {str | WebElement} : css selector or web element
    '''
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE)
    if not web_element:
      return None

    self.__chains.scroll_to_element(web_element).perform()

  def scroll_to_viewport(self,amount_x=0,amount_y=0):
    '''
    Scroll by given amount
    This is the second most common scenario for scrolling. 
    Pass in an delta x and a delta y value for how much to scroll in the right and down directions. 
    Negative values represent left and up, respectively.
    Parameter:
      amount_x {int} : the movement amount on  x-axis
      amount_y {int} : the movement amount on  y-axis
    '''
    self.__chains.scroll_by_amount(amount_x,amount_y).perform()
    
  def scroll_element_to_center(self,target_CS_WE,parent_CS_WE=None,timeout=None):

    element = self.__querier.query(target_CS_WE,parent_CS_WE)
    if not element:
      return None

    # scroll the element's center to the center of the viewport
    # 1. 获取窗口尺寸及中心点坐标
    window_size = self.__driver.get_window_size()
    window_center_x = window_size['width'] // 2   # 窗口水平中心
    window_center_y = window_size['height'] // 2  # 窗口垂直中心
    
    # 2. 获取元素自身尺寸及中心点坐标（相对于元素左上角的偏移）
    element_rect = element.rect  # 包含width/height/x/y等信息
    element_center_x = element_rect['width'] // 2  # 元素水平中心（相对于自身左上角）
    element_center_y = element_rect['height'] // 2 # 元素垂直中心（相对于自身左上角）
    
    # 3. 计算需要滚动的距离
    # 原理：从元素左上角开始，滚动到「窗口中心 - 元素中心」的位置
    scroll_x = window_center_x - element_center_x
    scroll_y = window_center_y - element_center_y

    self.scroll_from_element_to_offset(target_CS_WE,scroll_x,scroll_y,parent_CS_WE)

  def scroll_from_element_to_offset(self,target_CS_WE,amount_x=0,amount_y=0,parent_CS_WE=None):
    '''
    Scroll from an element by a given amount
    This scenario is effectively a combination of the above two methods.
    If the element is out of the viewport, it will be scrolled to the bottom of the screen, 
      then the page will be scrolled by the provided delta x and delta y values.
    Parameter:
      amount_x {int} : the movement amount on  x-axis
      amount_y {int} : the movement amount on  y-axis
    '''
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE)
    if not web_element:
      return None
    scroll_origin = ScrollOrigin.from_element(web_element)
    self.__chains.scroll_from_origin(scroll_origin,amount_x,amount_y).perform()


  def scroll_from_element_offset_to_offset(self,target_CS_WE,offset_x,offset_y,amount_x,amount_y,parent_CS_WE=None):
    '''
    Scroll from an element with an offset
    This scenario is used when you need to scroll only a portion of the screen, and it is outside the viewport. Or is inside the viewport and the portion of the screen that must be scrolled is a known offset away from a specific element.
    This uses the “Scroll From” method again, and in addition to specifying the element, an offset is specified to indicate the origin point of the scroll. The offset is calculated from the center of the provided element.
    If the element is out of the viewport, it first will be scrolled to the bottom of the screen, then the origin of the scroll will be determined by adding the offset to the coordinates of the center of the element, and finally the page will be scrolled by the provided delta x and delta y values.
    Parameter:
      offset_x {int} : the offset value on  x-axis to the element's cetner point
      offset_y {int} : the offset value on  y-axis to the element's cetner point
      amount_x {int} : the movement amount on  x-axis
      amount_y {int} : the movement amount on  y-axis
    Exception:
      If the offset from the center of the element falls outside of the viewport, it will result in an exception.
    '''
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE)
    if not web_element:
      return None
    
    offset_origin = ScrollOrigin.from_element(web_element,offset_x,offset_y)
    self.__chains.scroll_from_origin(offset_origin,amount_x,amount_y).perform()

  def scroll_from_viewport_offset_to_offset(self,offset_x,offset_y,amount_x,amount_y):
    '''
    Scroll from a offset of origin (viewport) by given amount
    The final scenario is used when you need to scroll only a portion of the screen, and it is already inside the viewport.
    This uses the “Scroll From” method again, but the viewport is designated instead of an element. An offset is specified from the upper left corner of the current viewport. After the origin point is determined, the page will be scrolled by the provided delta x and delta y values.
    Parameter:
      offset_x {int} : the offset value on  x-axis to the element's cetner point
      offset_y {int} : the offset value on  y-axis to the element's cetner point
    Exception:
      If the offset from the upper left corner of the viewport falls outside of the screen, it will result in an exception.
    '''
    offset_origin = ScrollOrigin.from_viewport(offset_x,offset_y)
    self.__chains.scroll_from_origin(offset_origin,amount_x,amount_y).perform()




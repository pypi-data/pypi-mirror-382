from blues_lib.sele.waiter.Querier import Querier  
from blues_lib.sele.element.Info import Info  
from blues_lib.util.BluesFiler import BluesFiler
from blues_lib.util.BluesDateTime import BluesDateTime

class File():

  def __init__(self,driver):
    self.__driver = driver
    self.__querier = Querier(driver,5) 
    self.__info = Info(driver) 

  def write(self,target_CS_WE,value,wait_time=3,parent_CS_WE=None,timeout=5):
    '''
    Add one or multiple files to the file input
    If there are multiple files, the upload mode is controlled based on whether multiple file upload is supported
    '''

    files = value if type(value) == list else [value]
    # Supports uploading multiple images at a time
    exist_files = BluesFiler.filter_exists(files)
    web_element = self.__querier.query(target_CS_WE,parent_CS_WE,timeout)
    if not exist_files or not web_element:
      return

    self._set_element_visible(web_element)

    is_multiple = self.__info.get_attr(web_element,'multiple')
    if is_multiple:
      # must join the file paths by \n
      file_lines = '\n'.join(exist_files)
      web_element.send_keys(file_lines)
      BluesDateTime.count_down({'duration':wait_time,'title':'Wait image upload...'})
    else:
      for exist_file in exist_files:
        web_element.send_keys(exist_file)
        BluesDateTime.count_down({'duration':wait_time,'title':'Wait image upload...'})
        
  def _set_element_visible(self,web_element):
    """
    确保文件输入框可见且具备可交互尺寸
    - 若元素隐藏(display: none)，设置为inline
    - 若元素尺寸为0(width/height=0)，设置为auto
    """
    driver = self.__driver
    
    # 获取当前样式属性
    current_display:bool = web_element.is_displayed()
    # 获取元素尺寸（rect返回字典包含width/height）
    element_rect:dict = web_element.rect
    current_width = element_rect['width']
    current_height = element_rect['height']
    
    # 调整display属性（如果隐藏）
    if not current_display:
      driver.execute_script("arguments[0].style.display = 'inline';", web_element)
    
    # 调整尺寸（如果为0或接近0）
    min_size = 1  # 最小有效尺寸阈值（像素）
    if current_width <= min_size:
      driver.execute_script("arguments[0].style.width = 'auto';", web_element)
    if current_height <= min_size:
      driver.execute_script("arguments[0].style.height = 'auto';", web_element)

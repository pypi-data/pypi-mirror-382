from selenium.webdriver.common.by import By

class Locator:

  bys:dict = {
    'css_selector':By.CSS_SELECTOR,
    'xpath':By.XPATH,
    'id':By.ID,
    'name':By.NAME,
    'class_name':By.CLASS_NAME,
    'tag_name':By.TAG_NAME,
    'link_text':By.LINK_TEXT,
    'partial_link_text':By.PARTIAL_LINK_TEXT,
  }  

  @classmethod
  def get(cls,target_CS_WE,by:str='')->tuple[str,str]|None:
    '''
    Split the by and value from the target_CS_WE,such as:
    'css_selector::id=123' -> (By.CSS_SELECTOR,'id=123')
    'xpath:://div' -> (By.XPATH,'//div')
    if has no found the by_key,return By.CSS_SELECTOR
    
    @param {str} target_CS_WE - The target CS_WE,such as 'css_selector::id=123'
    @param {str} by - The by type,such as 'css selector','xpath', it's the valid value ,not the dict key
    '''
    if not target_CS_WE:
      return None

    by_value:str = ''
    locator_value:str = ''
    default_by_value:str = by or By.CSS_SELECTOR
    # only split the first '::',such as 'css_selector::id=123' -> ['css_selector','id=123']
    locator_list:list[str] = target_CS_WE.split('::',1)
    
    if len(locator_list) == 1:
      by_value = default_by_value
      locator_value = target_CS_WE
    else:
      by_key = locator_list[0] 
      by_value = cls.bys.get(by_key) or default_by_value
      locator_value = locator_list[1]
      
    return (by_value,locator_value)


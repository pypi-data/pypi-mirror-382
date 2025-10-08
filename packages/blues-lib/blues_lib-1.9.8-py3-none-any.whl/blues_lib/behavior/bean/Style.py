import sys,os,re
from typing import Any

from blues_lib.behavior.Bean import Bean

class Style(Bean):

  def _get(self)->str:
    kwargs = self._get_kwargs(['target_CS_WE','parent_CS_WE','timeout'])
    kwargs.update({'key':'style'})
    return self._browser.element.info.get_attr(**kwargs)


  def _set(self):
    selector:str = self._config.get('target_CS_WE')
    if entity := self._get_value_entity():
      attrs = {
        "style":self._get_inline_style(entity),
      }
      if self._to_be_presence():
        return self._browser.script.javascript.attr(selector,attrs)
    
  def _get_inline_style(self,styles: dict) -> str:
    """
    将字典形式的CSS样式转换为字符串形式
    
    参数:
        styles: 包含CSS样式的字典，键可以是驼峰式(如fontWeight)或连字符式(如font-size)
    
    返回:
        转换后的CSS样式字符串，所有键都会转换为连字符形式
    """
    style_items = []
    
    for key, value in styles.items():
      # 将驼峰式命名转换为连字符式 (如fontWeight -> font-weight)
      converted_key = []
      for char in key:
        if char.isupper():
          # 在大写字母前添加连字符，并将大写转为小写
          converted_key.append('-' + char.lower())
        else:
          converted_key.append(char)
      css_key = ''.join(converted_key)
      
      # 添加键值对到列表
      style_items.append(f"{css_key}:{value}")
    
    # 用分号连接所有样式项
    return ';'.join(style_items)
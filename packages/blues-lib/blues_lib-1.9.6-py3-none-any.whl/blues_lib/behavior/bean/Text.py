import sys,os,re
from typing import Any

from blues_lib.behavior.Bean import Bean

class Text(Bean):

  def _get(self)->str:
    kwargs = self._get_kwargs(['target_CS_WE','parent_CS_WE','timeout'])
    return self._browser.element.info.get_text(**kwargs)

  def _set(self):
    selector:str = self._config.get('target_CS_WE')
    parent_selector:str = self._config.get('parent_CS_WE')
    value:str = self._config.get('value','')
    if self._to_be_presence():
      return self._browser.script.javascript.text(selector,value,parent_selector)

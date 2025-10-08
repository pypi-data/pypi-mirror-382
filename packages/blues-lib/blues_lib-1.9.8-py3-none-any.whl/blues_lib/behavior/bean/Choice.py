import sys,os,re
from typing import Any

from blues_lib.behavior.Bean import Bean

class Choice(Bean):

  def _set(self)->Any:
    kwargs = self._get_kwargs(['target_CS_WE','parent_CS_WE','timeout'])
    is_select = self._config.get('value',True)
    if self._to_be_clickable():
      if is_select:
        return self._browser.element.choice.select(**kwargs) 
      else:
        return self._browser.element.choice.deselect(**kwargs)

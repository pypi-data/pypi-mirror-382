import time
from blues_lib.behavior.Bean import Bean
from blues_lib.util.Clipboard import Clipboard

class Copy(Bean):

  def _get(self)->str:
    # clear the clipboard before copy
    Clipboard.clear()
    
    # trigger the copy action
    if self._to_be_clickable():
      self._scroll()
      value:str = self._copy()
      if value:
        return value
      else:
        # retry one time
        return self._copy()
    
  def _copy(self)->str:
    kwargs = self._get_kwargs(['target_CS_WE','parent_CS_WE','timeout'])
    time.sleep(0.5)
    self._browser.action.mouse.click(**kwargs)
    time.sleep(0.5)
    # get the text from the clipboard
    return Clipboard.paste()


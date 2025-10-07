import time
from blues_lib.behavior.Trigger import Trigger

class Click(Trigger):

  def _trigger(self):
    kwargs = self._get_kwargs(['target_CS_WE','parent_CS_WE','timeout'])
    if self._to_be_clickable():
      self._scroll()
      return self._browser.action.mouse.click(**kwargs)
    
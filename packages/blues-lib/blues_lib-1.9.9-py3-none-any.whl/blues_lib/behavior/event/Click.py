import time
from blues_lib.behavior.Trigger import Trigger

class Click(Trigger):

  def _trigger(self):
    kwargs = self._get_kwargs(['target_CS_WE','parent_CS_WE','timeout'])
    if self._to_be_clickable():
      self._scroll()
      time.sleep(0.2) # 有时状态判断成功，但实际还需要等待一些
      return self._browser.action.mouse.click(**kwargs)
    
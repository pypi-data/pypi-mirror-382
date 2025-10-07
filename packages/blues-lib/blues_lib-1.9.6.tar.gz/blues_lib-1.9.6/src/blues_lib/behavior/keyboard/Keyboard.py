import pyautogui
import time
from abc import abstractmethod
from blues_lib.behavior.Trigger import Trigger

class Keyboard(Trigger):

  def _trigger(self):
    self._focus()
    self._do()

  @abstractmethod
  def _do(self):
    pass
  
  def _focus(self):
    # 必须先esc，否则浏览器url会获得焦点
    pyautogui.press('esc')
    time.sleep(0.2)
    selector = self._config.get('target_CS_WE')
    if selector and self._to_be_clickable():
      self._browser.action.mouse.click(selector) 
      time.sleep(0.2)


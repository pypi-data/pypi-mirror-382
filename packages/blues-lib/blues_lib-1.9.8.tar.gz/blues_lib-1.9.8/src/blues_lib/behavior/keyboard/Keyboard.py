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
    # 必须先esc，否则浏览器url会获得焦点，等待0.5秒，避免打开页面第一个执行paste操作，esc没有生效
    time.sleep(0.5)
    pyautogui.press('esc')
    time.sleep(0.5)
    selector = self._config.get('target_CS_WE')
    if selector and self._to_be_clickable():
      self._browser.action.mouse.click(selector) 
      time.sleep(0.5)


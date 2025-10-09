from blues_lib.behavior.keyboard.Keyboard import Keyboard
import pyautogui

class KeyHot(Keyboard):
  
  def _do(self):
    '''
    To make pressing hotkeys or keyboard shortcuts convenient
    can be passed several key strings which will be pressed down in order, and then released in reverse order.
    such as ['ctrl','a']
    '''
    value:str|list[str] = self._config.get('value')
    if not value:
      return 

    args:list[str] = None
    if isinstance(value,list):
      args = value
    else:
      args = [str(value)]

    # one or more str input params
    # 如果在输入后输入法提示还在，必须先执行esc，否则执行比如全选会无效
    pyautogui.hotkey(*args)


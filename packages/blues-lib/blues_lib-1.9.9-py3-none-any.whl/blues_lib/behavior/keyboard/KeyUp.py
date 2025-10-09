from blues_lib.behavior.keyboard.Keyboard import Keyboard
import pyautogui

class KeyUp(Keyboard):
  
  def _do(self):
    '''
    Key up a character
    '''
    if value:= str(self._config.get('value')):
      pyautogui.keyUp(value)

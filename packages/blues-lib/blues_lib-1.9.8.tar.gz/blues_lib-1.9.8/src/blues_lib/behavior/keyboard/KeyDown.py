from blues_lib.behavior.keyboard.Keyboard import Keyboard
import pyautogui

class KeyDown(Keyboard):
  
  def _do(self):
    '''
    Key down a character
    '''
    if value:= str(self._config.get('value')):
      pyautogui.keyDown(value)

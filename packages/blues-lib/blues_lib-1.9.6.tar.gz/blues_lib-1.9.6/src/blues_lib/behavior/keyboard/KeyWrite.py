from blues_lib.behavior.keyboard.Keyboard import Keyboard
import pyautogui

class KeyWrite(Keyboard):
  
  def _do(self):
    '''
    type the characters in the string that is passed. To add a delay interval in between pressing each character key
    '''
    if value:= str(self._config.get('value')):
      interval:int|float = self._config.get('interval',0.1)
      pyautogui.write(value,interval)


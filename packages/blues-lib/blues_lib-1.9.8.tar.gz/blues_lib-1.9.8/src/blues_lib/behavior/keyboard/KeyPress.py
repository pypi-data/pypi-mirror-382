from blues_lib.behavior.keyboard.Keyboard import Keyboard
import pyautogui

class KeyPress(Keyboard):
  
  def _do(self):
    '''
    To press these keys, call the press() function and pass it a string from the pyautogui.KEYBOARD_KEYS 
      such as enter, esc, f1.
    @param {str} key : 'shift'
    @param {list[str]} key : ['left','left','left']
    '''
    value:str|list[str] = self._config.get('value','')
    if value:
      if value == 'esc':
        self._esc()
      else:
        # accept a str or list input
        pyautogui.press(value)

  def _esc(self,key:str):
    if sys.platform == "darwin":
      pyautogui.press('enter')
    else:
      pyautogui.press('esc')

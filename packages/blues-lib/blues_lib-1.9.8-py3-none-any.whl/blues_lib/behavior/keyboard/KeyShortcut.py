from blues_lib.behavior.keyboard.Keyboard import Keyboard
import pyautogui,sys

class KeyShortcut(Keyboard):
  
  def _do(self):
    '''
    execute one or multi shortcut
    '''
    value:str|list[str] = self._config.get('value')
    if not value:
      return 
    
    if isinstance(value,list):
      for item in value:
        self._do_once(item)
    else:
      self._do_once(str(value))
    
  def _do_once(self,value:str):
    
    keys:list[str] = self._get_keys(value)
    if not keys:
      # do as a command hotkey
      pyautogui.press(value)
      return

    if value == 'select':
      self._select()

    elif value == 'copy':
      self._select()
      pyautogui.hotkey(*keys)

    elif value == 'paste':
      pyautogui.hotkey(*keys)

    elif value == 'undo':
      pyautogui.hotkey(*keys)

    elif value == 'redo':
      pyautogui.hotkey(*keys)

    elif value == 'cut':
      pyautogui.hotkey(*keys)

    elif value == 'delete':
      self._select()
      # press accept a list input
      pyautogui.press(keys)

  def _select(self):
    pyautogui.press('esc')
    select_keys:list[str] = self._get_keys('select')
    pyautogui.hotkey(*select_keys)

  def _get_keys(self,name:str)->list[str]|None:
    ctrl:str = 'command' if sys.platform == "darwin" else 'ctrl'
    en_ctrl:str = 'win' if sys.platform == "win32" else 'ctrl'
    names = {
      "select": [ctrl,'a'],
      "copy": [ctrl,'c'],
      "paste": [ctrl,'v'],
      "undo": [ctrl,'z'],
      "redo": [ctrl,'shift','z'],
      "cut": [ctrl,'x'],
      "delete": ['delete'],
      "en": [en_ctrl, 'space'],
    }
    return names.get(name)
  
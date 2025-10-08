import pyautogui,sys
from blues_lib.behavior.keyboard.Keyboard import Keyboard
from blues_lib.util.Clipboard import Clipboard

class KeyPaste(Keyboard):

  def _do(self):
    # have no value, using the clipboard value
    if value:= self._config.get('value'):
      Clipboard.copy(value)

    ctrl:str = 'command' if sys.platform == "darwin" else 'ctrl'
    return pyautogui.hotkey(ctrl,'v')



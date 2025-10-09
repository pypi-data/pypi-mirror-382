from blues_lib.behavior.Trigger import Trigger

class Remove(Trigger):

  def _trigger(self)->any:
    kwargs = self._get_kwargs(['target_CS_WE'])
    return self._browser.element.popup.remove(**kwargs)
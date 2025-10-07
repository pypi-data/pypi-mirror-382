from blues_lib.behavior.Trigger import Trigger

class Frameout(Trigger):

  def _trigger(self)->any:
    return self._browser.interactor.frame.switch_to_default()
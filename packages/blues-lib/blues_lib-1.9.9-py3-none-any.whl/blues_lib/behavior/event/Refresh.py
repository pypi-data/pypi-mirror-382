from blues_lib.behavior.Trigger import Trigger

class Refresh(Trigger):

  def _trigger(self)->any:
    return self._browser.interactor.navi.refresh()
from blues_lib.behavior.Trigger import Trigger

class Framein(Trigger):

  def _trigger(self)->any:
    kwargs = self._get_kwargs(['target_CS_WE'])
    if self._to_be_presence():
      return self._browser.interactor.frame.switch_to(**kwargs)

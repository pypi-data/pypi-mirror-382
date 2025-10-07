from blues_lib.behavior.Trigger import Trigger

class Hover(Trigger):

  def _trigger(self):
    kwargs = self._get_kwargs(['target_CS_WE','parent_CS_WE','timeout'])
    if self._to_be_visible():
      return self._browser.action.mouse.move_in(**kwargs)
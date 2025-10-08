from blues_lib.behavior.Trigger import Trigger

class Scroll(Trigger):

  def _trigger(self)->any:
    kwargs = self._get_kwargs(['target_CS_WE','parent_CS_WE'])
    amount_x = self._config.get('amount_x') or 0
    amount_y = self._config.get('amount_y') or 0

    if amount_x or amount_y:
      kwargs = {**kwargs,'amount_x':amount_x,'amount_y':amount_y}
      return self._browser.action.wheel.scroll_from_element_to_offset(**kwargs)
    else:
      return self._browser.action.wheel.scroll_element_to_center(**kwargs)

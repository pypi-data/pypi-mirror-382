from blues_lib.util.BluesDateTime import BluesDateTime
from blues_lib.behavior.Trigger import Trigger

class Wait(Trigger):

  def _trigger(self)->any:
    kwargs = self._get_kwargs(['duration','title'])
    return BluesDateTime.count_down(kwargs)
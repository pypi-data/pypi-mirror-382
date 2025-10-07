import time
from blues_lib.behavior.Trigger import Trigger

class ToBePresence(Trigger):

  def _trigger(self)->bool:
    '''
    if the current url is equal to the expected url
    @returns {bool}
    '''
    kwargs = self._get_kwargs(['target_CS_WE','timeout','parent_CS_WE'])
    stat:bool = self._browser.waiter.ec.to_be_presence(**kwargs)

    if stat and (post_gurard_time:= self._config.get('post_guard_time',1)):
      time.sleep(post_gurard_time)
    return stat
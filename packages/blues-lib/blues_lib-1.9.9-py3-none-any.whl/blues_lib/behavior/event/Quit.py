from blues_lib.behavior.Trigger import Trigger
from blues_lib.util.BluesDateTime import BluesDateTime

class Quit(Trigger):

  def _trigger(self)->bool:
    '''
    quit the browser after the wait time
    @returns {bool}
    '''
    wait_time:int = self._config.get('wait_time',0)
    try:
      if self._browser:
        if wait_time:
          BluesDateTime.count_down({
            'duration':wait_time,
            'title':'waiting for the browser to quit...'
          })
        self._browser.quit()
      return True
    except Exception as e:
      return False

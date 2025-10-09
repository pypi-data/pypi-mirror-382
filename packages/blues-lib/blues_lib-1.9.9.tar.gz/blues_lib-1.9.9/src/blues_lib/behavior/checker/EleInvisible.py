from blues_lib.behavior.Trigger import Trigger

class EleInvisible(Trigger):

  def _trigger(self)->bool:
    '''
    check if the element is present in the page
    @returns {bool}
    '''
    target_CS_WE:str = self._config.get('target_CS_WE')
    wait_time:int = self._config.get('wait_time',3)
    return self._browser.waiter.ec.to_be_invisible(target_CS_WE,wait_time)

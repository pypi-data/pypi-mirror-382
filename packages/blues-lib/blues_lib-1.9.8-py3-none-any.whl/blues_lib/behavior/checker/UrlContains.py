from blues_lib.behavior.Trigger import Trigger

class UrlContains(Trigger):

  def _trigger(self)->bool:
    '''
    if the url contains the url slice in the wait time
    @returns {bool}
    '''
    url_slice = self._config.get('url_slice')
    wait_time = self._config.get('wait_time',3)
    return self._browser.waiter.ec.url_contains(url_slice,wait_time)

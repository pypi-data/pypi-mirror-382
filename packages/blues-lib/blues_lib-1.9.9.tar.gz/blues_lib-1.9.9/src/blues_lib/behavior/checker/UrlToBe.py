from blues_lib.behavior.Trigger import Trigger

class UrlToBe(Trigger):

  def _trigger(self)->bool:
    '''
    if the current url is equal to the expected url
    @returns {bool}
    '''
    url = self._config.get('url')
    wait_time = self._config.get('wait_time',3)
    return self._browser.waiter.ec.url_to_be(url,wait_time)

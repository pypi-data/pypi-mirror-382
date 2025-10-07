from blues_lib.behavior.Trigger import Trigger

class Open(Trigger):

  def _trigger(self)->any:
    url = self._config.get('url')
    try:
      self._browser.open(url)
      return True
    except Exception as e:
      return False

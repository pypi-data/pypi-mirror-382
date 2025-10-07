from blues_lib.behavior.Trigger import Trigger

class Javascript(Trigger):

  def _trigger(self)->any:
    script = self._config.get('script')
    return self._browser.script.javascript.execute(script)

from blues_lib.behavior.Bean import Bean

class Html(Bean):

  def _get(self)->str:
    selector:str = self._config.get('target_CS_WE')
    parent_selector:str = self._config.get('parent_CS_WE')
    return self._browser.script.javascript.html(selector,parent_selector)

  def _set(self):
    selector:str = self._config.get('target_CS_WE')
    parent_selector:str = self._config.get('parent_CS_WE')
    value:str = self._config.get('value','')
    if self._to_be_presence():
      return self._browser.script.javascript.html(selector,value,parent_selector)
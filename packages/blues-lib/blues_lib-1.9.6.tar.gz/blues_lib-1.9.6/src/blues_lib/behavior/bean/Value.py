from blues_lib.behavior.Bean import Bean

class Value(Bean):

  def _get(self)->str:
    kwargs = self._get_kwargs(['target_CS_WE','parent_CS_WE','timeout'])
    return self._browser.element.info.get_value(**kwargs)
  
  def _set(self):
    selector:str = self._config.get('target_CS_WE')
    value:str = self._config.get('value','')
    entity = {
      'value':value,
    }
    if self._to_be_presence():
      return self._browser.script.javascript.attr(selector,entity)

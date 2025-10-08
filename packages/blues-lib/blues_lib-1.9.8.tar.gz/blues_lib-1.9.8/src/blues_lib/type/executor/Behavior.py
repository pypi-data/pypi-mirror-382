import time
from abc import abstractmethod

from blues_lib.type.executor.Executor import Executor
from blues_lib.type.model.Model import Model
from blues_lib.type.output.STDOut import STDOut
from blues_lib.sele.browser.Browser import Browser

class Behavior(Executor):
  def __init__(self,model:Model,browser:Browser=None)->None:
    super().__init__()
    self._model = model
    self._meta = model.meta
    self._bizdata = model.bizdata
    self._config = model.config
    self._browser = browser
    
  def execute(self)->STDOut:
    key = 'target_CS_WE'
    if key in self._config and not self._config[key]:
      return STDOut(200,f'skip the behavior, the {key} is None')
    return self._invoke()
  
  @abstractmethod
  def _invoke(self):
    pass

  def _get_kwargs(self,keys:list[str],config=None)->dict:
    '''
    Extract specified keys from configuration dictionary
    @param {list[str]} keys: list of keys to extract from config
    @param {dict} config: optional config dict to merge with self._config (config takes precedence)
    @return {dict}: dictionary containing only the specified keys and their values
    '''
    conf = {**self._config,**config} if config else self._config
    # must remove the attr that value is None
    key_conf = {}
    for key in keys:
      if key in conf:
        key_conf[key] = conf.get(key)
    return key_conf

  def _to_be_clickable(self)->bool:
    kwargs = self._get_kwargs(['target_CS_WE','timeout'])
    # scroll the element into view, avoid the element is covered by other elements
    return self._browser.waiter.ec.to_be_clickable(**kwargs)

  def _to_be_visible(self)->bool:
    kwargs = self._get_kwargs(['target_CS_WE','timeout'])
    return self._browser.waiter.ec.to_be_visible(**kwargs)

  def _to_be_presence(self)->bool:
    kwargs = self._get_kwargs(['target_CS_WE','timeout'])
    return self._browser.waiter.ec.to_be_presence(**kwargs)

  def _scroll(self):
    kwargs = self._get_kwargs(['target_CS_WE','parent_CS_WE'])
    scrollable = self._config.get('scrollable',False)
    if scrollable:
      self._browser.action.wheel.scroll_element_to_center(**kwargs)
      time.sleep(0.1)
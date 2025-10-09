from typing import Union
from selenium.webdriver.remote.webelement import WebElement
from blues_lib.type.executor.Behavior import Behavior
from blues_lib.type.output.STDOut import STDOut
from blues_lib.type.model.Model import Model
from blues_lib.sele.browser.Browser import Browser
from blues_lib.behavior.BhvExecutor import BhvExecutor
from blues_lib.behavior.unit.ConfigModifier import ConfigModifier

class Row(Behavior):
  
  def __init__(self,model:Model,browser:Browser=None):
    super().__init__(model,browser)
    self._chidlren:Union[dict,list] = self._config.get('children')

  def _invoke(self)->STDOut:
    try:
      rows = []
      parents:list[WebElement]|None = self._get_parents()
      
      if not parents:
        # single unit
        if value := self._execute_unit():
          rows.append(value)
      else:
        # multi units
        for parent in parents:
          if value := self._execute_unit(parent):
            rows.append(value)

      return STDOut(200,'ok',rows if rows else None)
    except Exception as e:
      return STDOut(500,str(e),None)
    
  def _get_parents(self)->list[WebElement]|None:
    # outer's target 
    target_CS_WE:str = self._config.get('target_CS_WE')
    return self._browser.waiter.querier.query_all(target_CS_WE)

  def _execute_unit(self,parent:WebElement=None)->any:
    model = self._get_model(parent)
    executor = BhvExecutor(model,self._browser)
    stdout = executor.execute()
    return stdout.data
  
  def _get_model(self,parent:WebElement|None=None):
    config_modifier = ConfigModifier(self._chidlren,parent)
    config = config_modifier.get_unit_config()
    return Model(config)

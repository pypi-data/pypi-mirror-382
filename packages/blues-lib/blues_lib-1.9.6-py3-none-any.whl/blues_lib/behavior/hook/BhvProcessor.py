from blues_lib.type.executor.Executor import Executor
from blues_lib.type.model.Model import Model

class BhvProcessor(Executor):
  
  def __init__(self,value:any,proc_conf:dict,bhv_model:Model) -> None:
    '''
    @param {any} value : the value to be processed
    @param {dict} proc_conf : the processor config
    @param {Model} bhv_model : the behavior model
    '''
    super().__init__()
    self._value = value
    self._proc_conf = proc_conf
    self._bhv_model = bhv_model
    
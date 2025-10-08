from blues_lib.type.executor.Executor import Executor
from blues_lib.type.model.Model import Model
from blues_lib.behavior.hook.BhvProcFactory import BhvProcFactory

class BhvHook(Executor):

  def __init__(self,value:any,proc_confs:list[dict],bhv_model:Model):
    self._value = value
    self._proc_confs = proc_confs
    self._bhv_model = bhv_model
    
  def execute(self)->any:
    value = self._value
    # 前一个输出作为后一个输入
    for proc_conf in self._proc_confs:
      value = self._run(value,proc_conf)
    return value
    
  def _run(self,value:any,proc_conf:dict)->any:
    proc_type:str = proc_conf.get('type')  or 'class' # 目前只处理内置类，script类型暂不处理
    proc_name:str = proc_conf.get('value')
    if not proc_name:
      self._logger.error(f'[{self.__class__.__name__}] Failed to get processor name from config {proc_name}')
      return value
    
    proc_inst = BhvProcFactory(value,proc_conf,self._bhv_model).create(proc_name)
    if not proc_inst:
      self._logger.error(f'[{self.__class__.__name__}] Failed to create processor {proc_name}')
      return value

    proc_value:any = proc_inst.execute()
    if not proc_value:
      self._logger.error(f'[{self.__class__.__name__}] Failed to get valid value from processor {proc_name}')

    return proc_value

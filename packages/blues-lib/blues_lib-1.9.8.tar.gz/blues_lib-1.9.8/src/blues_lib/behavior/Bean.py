from blues_lib.type.output.STDOut import STDOut
from blues_lib.type.executor.Behavior import Behavior
from blues_lib.behavior.hook.BhvHook import BhvHook

class Bean(Behavior):

  def _invoke(self)->STDOut:
    value = None
    try:
      if self._action()=='setter':
        value = self._set()
      else:
        value = self._get()
        value = self._after_get(value)
      return STDOut(200,'ok',value)
    except Exception as e:
      return STDOut(500,str(e),value)

  def _get(self)->any:
    # optional
    pass

  def _set(self)->any:
    # optional
    pass

  def _action(self)->str:
    action = 'getter'
    if 'value' in self._config:
      action = 'setter'
    return action
  
  def _after_get(self,value:any)->any:
    # 在getter后调用，用于处理获取到的值
    hook_value = self._config.get('after_get')
    if not hook_value:
      return value

    proc_confs:list[dict] = hook_value if isinstance(hook_value,list) else [hook_value]
    return BhvHook(value,proc_confs,self._model).execute()
  
  def _get_value_entity(self)->dict|None:

    key:str|None = self._config.get('key')
    value:any = self._config.get('value')

    if key:
      return {
        key:value
      }

    if isinstance(value,dict):
      return value
    
    return None
      
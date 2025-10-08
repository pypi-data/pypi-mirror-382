from blues_lib.material.MatHanderChain import MatHanderChain
from blues_lib.behavior.hook.BhvProcessor import BhvProcessor

class MatFormatter(BhvProcessor):
    
  def execute(self)->list[dict]:
    if not isinstance(self._value,list):
      self._logger.error(f'[{self.__class__.__name__}] input value is not list')
      return self._value

    request = {
      'config':self._proc_conf,
      'entities':self._value,
    }
    output:STDOut = MatHanderChain(request).handle()
    # 如果为空，说明格式验证都未通过
    return output.data
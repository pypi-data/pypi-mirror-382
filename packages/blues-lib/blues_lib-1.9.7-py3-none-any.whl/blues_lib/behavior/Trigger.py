from abc import abstractmethod
from blues_lib.type.output.STDOut import STDOut
from blues_lib.type.executor.Behavior import Behavior

class Trigger(Behavior):

  def _invoke(self)->STDOut:
    value = None
    try:
      value = self._trigger()
      return STDOut(200,'ok',value)
    except Exception as e:
      return STDOut(500,str(e),value)

  @abstractmethod
  def _trigger(self)->any:
    pass
  
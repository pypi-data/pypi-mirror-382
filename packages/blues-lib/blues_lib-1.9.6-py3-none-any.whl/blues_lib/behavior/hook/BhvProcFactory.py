from blues_lib.type.factory.Factory import Factory
from blues_lib.type.model.Model import Model
from blues_lib.behavior.hook.BhvProcessor import BhvProcessor
from blues_lib.behavior.hook.llm.AnswerToMats import AnswerToMats
from blues_lib.behavior.hook.llm.AnswerToRevs import AnswerToRevs
from blues_lib.behavior.hook.llm.AnswerToMatsRevs import AnswerToMatsRevs

from blues_lib.behavior.hook.material.MatFormatter import MatFormatter
from blues_lib.behavior.hook.html.HtmlFilter import HtmlFilter

class BhvProcFactory(Factory):

  _proc_classes = {
    AnswerToMats.__name__:AnswerToMats,
    AnswerToRevs.__name__:AnswerToRevs,
    AnswerToMatsRevs.__name__:AnswerToMatsRevs,
    MatFormatter.__name__:MatFormatter,
    HtmlFilter.__name__:HtmlFilter,
  }

  def __init__(self,value:any,proc_conf:dict,bhv_model:Model) -> None:
    self._value = value
    self._proc_conf = proc_conf
    self._bhv_model = bhv_model

  def create(self,proc_name:str)->BhvProcessor|None:
    # overide
    proc_class = self._proc_classes.get(proc_name)
    return proc_class(self._value,self._proc_conf,self._bhv_model) if proc_class else None


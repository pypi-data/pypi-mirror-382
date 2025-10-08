import sys,os,re

from blues_lib.type.factory.Factory import Factory
from blues_lib.type.model.Model import Model
from blues_lib.type.executor.Executor import Executor
from blues_lib.namespace.CommandName import CommandName
from blues_lib.command.hook.processor.prev.TextToAIQuery import TextToAIQuery
from blues_lib.command.hook.processor.prev.HtmlToAIQueries import HtmlToAIQueries



class PrevProcFactory(Factory):

  _proc_classes = {
    TextToAIQuery.__name__:TextToAIQuery,
    HtmlToAIQueries.__name__:HtmlToAIQueries,
  }

  def __init__(self,context:dict,input:Model,proc_conf:dict,name:CommandName) -> None:
    self._context = context
    self._input = input
    self._proc_conf = proc_conf
    self._name = name

  def create(self,proc_name:str)->Executor | None:
    # overide
    proc_class = self._proc_classes.get(proc_name)
    return proc_class(self._context,self._input,self._proc_conf,self._name) if proc_class else None



import sys,os,re

from blues_lib.type.executor.Executor import Executor
from blues_lib.type.output.STDOut import STDOut
from blues_lib.type.model.Model import Model
from blues_lib.namespace.CommandName import CommandName

class AbsPrevProc(Executor):
  
  def __init__(self,context:dict,input:Model,proc_conf:dict,name:CommandName) -> None:
    super().__init__()
    self._context = context
    self._input = input
    self._proc_conf = proc_conf
    self._name = name
  
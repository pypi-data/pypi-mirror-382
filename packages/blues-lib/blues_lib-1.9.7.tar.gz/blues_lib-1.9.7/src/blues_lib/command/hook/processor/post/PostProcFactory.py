import sys,os,re

from blues_lib.type.factory.Factory import Factory
from blues_lib.type.model.Model import Model
from blues_lib.type.executor.Executor import Executor
from blues_lib.type.output.STDOut import STDOut
from blues_lib.namespace.CommandName import CommandName
from blues_lib.command.hook.processor.post.AddMatQuery import AddMatQuery
from blues_lib.command.hook.processor.post.AddRevParas import AddRevParas
from blues_lib.command.hook.processor.post.AIAnswerToMat import AIAnswerToMat
from blues_lib.command.hook.processor.post.AIAnswerToRev import AIAnswerToRev
from blues_lib.command.hook.processor.post.LoginChecker import LoginChecker
from blues_lib.command.hook.processor.post.PublishChecker import PublishChecker
from blues_lib.command.hook.processor.post.LoginInvoker import LoginInvoker


class PostProcFactory(Factory):

  _proc_classes = {
    AddMatQuery.__name__:AddMatQuery,
    AddRevParas.__name__:AddRevParas,
    AIAnswerToMat.__name__:AIAnswerToMat,
    AIAnswerToRev.__name__:AIAnswerToRev,
    LoginChecker.__name__:LoginChecker,
    PublishChecker.__name__:PublishChecker,
    LoginInvoker.__name__:LoginInvoker,
  }

  def __init__(self,context:dict,input:Model,proc_conf:dict,output:STDOut,name:CommandName) -> None:
    self._context = context
    self._input = input # node's input
    self._proc_conf = proc_conf
    self._output = output # node's output
    self._name = name

  def create(self,proc_name:str)->Executor | None:
    # overide
    proc_class = self._proc_classes.get(proc_name)
    return proc_class(self._context,self._input,self._proc_conf,self._output,self._name) if proc_class else None


import sys,os,re

from blues_lib.type.executor.Executor import Executor

class Command(Executor):

  def __init__(self,context:dict):
    super().__init__()
    self._context = context

  @property
  def context(self):
    return self._context


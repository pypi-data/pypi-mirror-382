import sys,os,re
from abc import ABC,abstractmethod

from blues_lib.type.output.STDOut import STDOut
from blues_lib.logger.LoggerFactory import LoggerFactory

class Executor(ABC):

  def __init__(self):
    self._logger = LoggerFactory({'name':f'{self.__class__.__module__}.{self.__class__.__name__}'}).create_file()

  @abstractmethod  
  def execute(self)->STDOut:
    pass


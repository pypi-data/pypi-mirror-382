from abc import ABC,abstractmethod
import sys,os,re

from blues_lib.type.output.STDOut import STDOut
from blues_lib.logger.LoggerFactory import LoggerFactory

class Handler(ABC):

  def __init__(self,request):
    self._next_handler = None
    self._request = request
    self._logger = LoggerFactory({'name':f'{self.__class__.__module__}.{self.__class__.__name__}'}).create_file()
  
  def set_next(self,handler):
    self._next_handler = handler
    return handler

  @abstractmethod
  def handle(self)->STDOut:
    pass

  @abstractmethod
  def resolve(self)->STDOut:
    pass
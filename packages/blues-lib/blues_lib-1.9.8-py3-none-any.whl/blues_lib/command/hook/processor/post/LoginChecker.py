import sys,os,re

from blues_lib.command.hook.processor.post.AbsPostProc import AbsPostProc
from blues_lib.namespace.CrawlerName import CrawlerName

class LoginChecker(AbsPostProc):
  
  def execute(self)->None:
    '''
    @description: check the login status
    @return: None
    '''
    if not self._output.data :
      self._output.code = 500
      self._output.message = f'{self.__class__.__name__} login failed: has no output.data'
    elif self._output.data.get(CrawlerName.Field.LOGGEDIN.value):
      self._output.message = f'{self.__class__.__name__} current loggedin'
    else:
      self._output.code = 500
      self._output.message = f'{self.__class__.__name__} current not loggedin'

    
    
    
    
     

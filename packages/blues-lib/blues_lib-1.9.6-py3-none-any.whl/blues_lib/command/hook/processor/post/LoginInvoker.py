import sys,os,re

from blues_lib.command.hook.processor.post.AbsPostProc import AbsPostProc
from blues_lib.namespace.CrawlerName import CrawlerName

class LoginInvoker(AbsPostProc):
  
  def execute(self)->None:
    '''
    @description: check the login status
    @return: None
    '''
    if not self._output.data :
      self._output.code = 500
      self._output.message = 'valid login failed: has no output.data'
    elif not self._output.data.get(CrawlerName.Field.LOGGEDIN.value):
      self._output.code = 500
      self._output.message = 'valid login failed: loggedin is false'
    elif not (ckfile := self._output.data.get(CrawlerName.Field.CKFILE.value)):
      self._output.code = 500
      self._output.message = 'failed to save the cookies'
    else:
      self._output.message = f'login and save the cookies - {ckfile}'
  
  
  
   

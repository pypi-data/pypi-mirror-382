import sys,os,re

from blues_lib.command.NodeCommand import NodeCommand
from blues_lib.namespace.CommandName import CommandName
from blues_lib.type.output.STDOut import STDOut
from blues_lib.type.exception.FlowRetryException import FlowRetryException

class Retryer(NodeCommand):

  NAME = CommandName.Control.RETRYER

  def _invoke(self)->STDOut:
    retry_code:int = self._summary.get('code',200)
    retry_message:str = self._summary.get('message','')
    if self._output and self._output.code == retry_code:
      self._clean()
      raise FlowRetryException(f'[{self.NAME}] Retry by code {retry_code} - {retry_message}')
    else:
      return STDOut(200,'Skip the retryer')
      
  def _clean(self)->None:
    creator_output:STDOut = self._context.get(CommandName.Browser.CREATOR.value)
    if browser := creator_output.data if creator_output else None:
      browser.quit()
 
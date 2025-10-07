import sys,os,re

from blues_lib.command.NodeCommand import NodeCommand
from blues_lib.namespace.CommandName import CommandName
from blues_lib.type.output.STDOut import STDOut
from blues_lib.type.exception.FlowBlockedException import FlowBlockedException

class Blocker(NodeCommand):

  NAME = CommandName.Control.BLOCKER

  def _invoke(self)->STDOut:
    block_code:int = self._summary.get('code',200)
    block_message:str = self._summary.get('message','')
    block_script:str = self._summary.get('script','') # define a python script
    if self._output and self._output.code == block_code:
      self._clean()
      raise FlowBlockedException(f'[{self.NAME}] Block by code {block_code} - {block_message}')
    else:
      return STDOut(200,'Skip the blocker')
      
  def _clean(self)->None:
    creator_output:STDOut = self._context.get(CommandName.Browser.CREATOR.value)
    if browser := creator_output.data if creator_output else None:
      browser.quit()
 
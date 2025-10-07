import sys,os,re

from blues_lib.command.NodeCommand import NodeCommand
from blues_lib.namespace.CommandName import CommandName
from blues_lib.type.output.STDOut import STDOut
from blues_lib.type.exception.FlowBlockedException import FlowBlockedException

class Printer(NodeCommand):

  NAME = CommandName.Control.PRINTER

  def _invoke(self)->STDOut:
    commands:str = self._summary.get('commands')
    if not commands:
      return STDOut(200,'No commands to print')
    
    for command in commands:
      output:STDOut = self._context.get(command)
      print(f'{command}: {output}')
      
    return STDOut(200,'Print done')


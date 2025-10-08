import sys,os,re

from blues_lib.command.NodeCommand import NodeCommand
from blues_lib.namespace.CommandName import CommandName
from blues_lib.type.output.STDOut import STDOut
from blues_lib.material.sinker.Sinker import Sinker as SinkerHandler

class Sinker(NodeCommand):
  
  NAME = CommandName.Material.SINKER

  def _setup(self):
    super()._setup()
    if not self._output:
      message = f'[{self.NAME}] Failed to check - {self.OUTPUT} is not ok'
      raise Exception(message)

  def _invoke(self)->STDOut:
    entities:list[dict] = self._output.data if isinstance(self._output.data,list) else [self._output.data]
    request = {
      'config':{
        'sinker':self._summary,
      },
      'entities':entities, # must be a list
    } 
    handler = SinkerHandler(request)
    return handler.handle()

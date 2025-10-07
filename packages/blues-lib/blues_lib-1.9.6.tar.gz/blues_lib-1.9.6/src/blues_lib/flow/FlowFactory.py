import sys,os,re

from blues_lib.type.factory.Factory import Factory
from blues_lib.type.executor.Flow import Flow
from blues_lib.namespace.CommandName import CommandName
from blues_lib.command.CommandFactory import CommandFactory

class FlowFactory(Factory):
  
  def __init__(self,queue_maps:list[dict]) -> None:
    self._queue_maps:list[dict] = queue_maps

  def create(self)->Flow | None:
    # override
    flow = Flow()
    for queue_map in self._queue_maps:
      self._add_cmd(flow,queue_map)
    
    return flow if flow.size else None
  
  def _add_cmd(self,flow:Flow,queue_map:dict):
    label:str = queue_map['command']
    input:str = queue_map['input']
    id:str = queue_map.get('id','') # command id
    cmd_name:CommandName = CommandName.from_value(label)
    if command:= CommandFactory(flow.context,input,id).create(cmd_name):
      flow.add(command)

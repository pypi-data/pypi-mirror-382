import sys,os,re

from blues_lib.type.output.STDOut import STDOut
from blues_lib.command.NodeCommand import NodeCommand
from blues_lib.namespace.CommandName import CommandName

class Engine(NodeCommand):

  NAME = CommandName.Flow.ENGINE
  TYPE = CommandName.Type.SETTER
  

  def _invoke(self)->STDOut:
    # lazy to import to avoid circular import
    from blues_lib.flow.FlowFactory import FlowFactory
    
    queue_maps:list[dict] = self._node_input
    sub_flow = FlowFactory(queue_maps).create()
    # 保留一个对父flow context的引用，用于取值
    sub_flow.context[CommandName.IO.PARENT.value] = self._context

    # set the main flow output as the sub flow's init context
    if main_output:=self._context.get(CommandName.IO.OUTPUT.value):
      sub_flow.context[CommandName.IO.OUTPUT.value] = main_output

    sub_output:STDOut = sub_flow.execute()
    # set the sub flow's output as the main flow's node output
    sub_data = sub_flow.context[CommandName.IO.OUTPUT.value].data
    return STDOut(sub_output.code,sub_output.message,sub_data)

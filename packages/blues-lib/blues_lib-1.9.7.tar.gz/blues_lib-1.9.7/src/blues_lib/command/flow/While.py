import sys,os,re

from blues_lib.type.output.STDOut import STDOut
from blues_lib.command.NodeCommand import NodeCommand
from blues_lib.namespace.CommandName import CommandName

class While(NodeCommand):

  NAME = CommandName.Flow.WHILE
  TYPE = CommandName.Type.SETTER
  

  def _invoke(self):
    # lazy to import to avoid circular import
    from blues_lib.flow.FlowFactory import FlowFactory
    prev_output:STDOut = None

    for context in self._node_input:
      # append prev output to current flow
      if prev_output:
        context[CommandName.IO.OUTPUT.value] = prev_output

      flow = FlowFactory(context).create()
      stdout:STDOut = flow.execute()

      if stdout.code == 200:
        self._infos.append(stdout.message)
      else:
        self._errors.append(stdout.message)

      # even the prev flow failed, we should continue
      prev_output = context[CommandName.IO.OUTPUT.value]
      
    # output the last sub flow's stdout
    self._code = prev_output.code
    self._data = prev_output.data
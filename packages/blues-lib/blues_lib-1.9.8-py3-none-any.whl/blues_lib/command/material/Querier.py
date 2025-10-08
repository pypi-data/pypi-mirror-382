import sys,os,re

from blues_lib.namespace.CommandName import CommandName
from blues_lib.command.NodeCommand import NodeCommand
from blues_lib.dao.material.MatQuerier import MatQuerier
from blues_lib.type.output.STDOut import STDOut

class Querier(NodeCommand):

  NAME = CommandName.Material.QUERIER
  TYPE = CommandName.Type.SETTER

  def _invoke(self)->STDOut:
    querier = MatQuerier()
    fields = self._summary.get('fields','*')
    count = self._summary.get('count',1)
    conditions = self._summary.get('conditions')
    output:STDOut = querier.latest(fields,conditions,count)
    if not output.data:
      return STDOut(500,f'{self.NAME} No data found - {conditions}')
    return output



     
import sys,os,re

from blues_lib.namespace.CrawlerName import CrawlerName
from blues_lib.command.hook.processor.Processor import Processor
from blues_lib.command.hook.processor.prev.PrevProcFactory import PrevProcFactory

class PrevProcessor(Processor):
  
  POSITION = CrawlerName.Field.PREV

  def _get_proc_inst(self,class_name:str):
    return PrevProcFactory(self._context,self._input,self._proc_conf,self._name).create(class_name)

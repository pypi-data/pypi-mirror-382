import sys,os,re

from blues_lib.command.hook.processor.Processor import Processor
from blues_lib.command.hook.processor.post.PostProcFactory import PostProcFactory
from blues_lib.type.model.Model import Model
from blues_lib.type.output.STDOut import STDOut
from blues_lib.namespace.CrawlerName import CrawlerName
from blues_lib.namespace.CommandName import CommandName

class PostProcessor(Processor):
  
  POSITION = CrawlerName.Field.POST

  def __init__(self,context:dict,input:Model,output:STDOut,name:CommandName) -> None:
    '''
    @param {dict} context : the flow's context
    @param {Model} input : the basic command node's input
    @param {CommandName} name : the current command's name
    '''
    super().__init__(context,input,name)
    self._output = output

  def _get_proc_inst(self,class_name:str):
    return PostProcFactory(self._context,self._input,self._proc_conf,self._output,self._name).create(class_name)

from blues_lib.type.executor.Executor import Executor
from blues_lib.type.model.Model import Model
from blues_lib.namespace.CrawlerName import CrawlerName
from blues_lib.namespace.CommandName import CommandName
from blues_lib.command.hook.mapping.Mapper import Mapper

class AbsMapping(Executor):
  
  POSITION = None
  
  def __init__(self,context:dict,input:Model,name:CommandName):
    '''
    @param {dict} context : the flow's context
    @param {Model} input : the basic command node's input
    @param {CommandName} name : the current command's name
    '''
    self._context:dict = context
    self._input = input
    self._name = name
    # only model input can have a mapping config
    self._map_conf = self._get_conf()
  
  def _get_conf(self)->dict|None:
    hook_conf = self._input.config.get(self.POSITION.value,{})
    return hook_conf.get(CrawlerName.Field.MAPPING.value)

  def execute(self) -> bool:
    '''
    从指定节点取值设置到另外一个节点，link设置模式如下： command_name[:parent_attr_chain]/attr_chain
    - command_name : command类型或id(id需要手动配置)，节点数据一般为STDOut类型; bizdata表示当前command的bizdata
    - parent_attr_chain : 可选，指定command的输出数据中，取值的父级属性链，多个属性用.分隔
    - attr_chain : 指定command的输出数据中，取值的属性链，多个属性用.分隔
    '''
    return Mapper(self._context,self._input,self._map_conf).execute()
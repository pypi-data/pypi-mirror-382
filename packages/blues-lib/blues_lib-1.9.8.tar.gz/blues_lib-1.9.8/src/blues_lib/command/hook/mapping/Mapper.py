from blues_lib.type.executor.Executor import Executor
from blues_lib.type.model.Model import Model
from blues_lib.type.output.STDOut import STDOut
from blues_lib.util.NestedDataMapping import NestedDataMapping
from blues_lib.util.NestedDataReader import NestedDataReader

class Mapper(Executor):
  
  def __init__(self,context:dict,input:Model,map_conf:dict):
    '''
    @param {dict} context : the flow's context
    @param {Model} input : the basic command nodel input
    @param {dict} map_conf : the mapping config
     - source
     - target
     - method
    '''
    self._context:dict = context
    self._input:Model = input
    # only model input can have a mapping config
    self._map_conf = map_conf

  def execute(self) -> bool:
    '''
    从指定节点取值设置到另外一个节点，link设置模式如下： command_name[:parent_attr_chain]/attr_chain
    - command_name : command类型或id(id需要手动配置)，节点数据一般为STDOut类型; bizdata表示当前command的bizdata
    - parent_attr_chain : 可选，指定command的输出数据中，取值的父级属性链，多个属性用.分隔
    - attr_chain : 指定command的输出数据中，取值的属性链，多个属性用.分隔
    '''
    if not self._map_conf:
      return False

    method:str = self._map_conf.get('method','assign')
    source_data,source_attr_chain = self.get_source()
    target_data,target_attr_chain = self.get_target()

    if not source_data or not target_data:
      return False

    if has_mapped:= NestedDataMapping.map(source_data,source_attr_chain,target_data,target_attr_chain,method):
      self._input.refresh()

    return has_mapped
  
  def get_target(self)->tuple:
    target_link:dict = self._map_conf.get('target')
    if not target_link:
      return (None,None)
    target_command_name,target_parent_attr_chain,target_attr_chain = self._get_format_path(target_link)
    target_data = self._get_node_data(target_command_name,target_parent_attr_chain)
    return (target_data,target_attr_chain)
  
  def get_source(self)->tuple:
    source_link:dict = self._map_conf.get('source')
    if not source_link:
      return (None,None)
    source_command_name,source_parent_attr_chain,source_attr_chain = self._get_format_path(source_link)
    source_data = self._get_node_data(source_command_name,source_parent_attr_chain)
    return (source_data,source_attr_chain)
  
  def _get_node_data(self,command_name:str,parent_attr_chain:str)->any:
    base_data:any = None
    if command_name == 'bizdata':
      base_data = self._input.bizdata
    else:
      base_data = self._context.get(command_name)

    if not base_data:
      return None

    if not parent_attr_chain:
      return base_data.data if isinstance(base_data,STDOut) else base_data

    base_output:any = NestedDataReader.read_by_path(base_data,parent_attr_chain)
    return base_output.data if isinstance(base_output,STDOut) else base_output
  
  def _get_format_path(self,link:str)->tuple:
    link_slices:list[str] = link.split('/')
    base_link:str = link_slices[0]
    attr_chain:str = link_slices[1] if len(link_slices) > 1 else ''
    base_link_slices:list[str] = base_link.split(':')

    command_name:str = base_link_slices[0]
    parent_attr_chain:str = base_link_slices[1] if len(base_link_slices) > 1 else ''
    return (command_name,parent_attr_chain,attr_chain)
    
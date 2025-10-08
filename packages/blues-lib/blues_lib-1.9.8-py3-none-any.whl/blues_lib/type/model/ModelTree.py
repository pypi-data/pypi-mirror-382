import sys,os,re
from typing import Any

from blues_lib.type.model.Model import Model

class ModelTree:
  @classmethod
  def create(cls, tree: Any, alt_bizdata:dict = None):
    '''
    convert model tree to model object
    :param tree: model tree
    :param alt_bizdata: business data, as the alternative data source
    :return: model object
    '''
    cls._move_bizdata_from_parent_flow(tree)
    return cls._process(tree,alt_bizdata)
  
  @classmethod
  def _move_bizdata_from_parent_flow(cls,tree:list[dict]):
    '''
    第一层command如果是 command-flow-engine，并且此节点有bizdata，则将其设置到其子flow的所有command节点上（input的第二个属性如果不存在的话）
    当前只支持一级flow嵌套，后期如果支持任意级，相关结构与转换需相应调整
    '''
    if not tree or not isinstance(tree,list):
      return
    
    for item in tree:
      if item.get('command') == 'command-flow-engine' and item.get('bizdata'):
        bizdata = item.get('bizdata')
        children:list[dict] = item.get('input')
        if not children or not isinstance(children,list):
          continue
        for command in children:
          if command.get('input') :
            # input 至少有2个属性，第3个属性为bizdata
            if len(command['input']) == 2 :
              command['input'].append(bizdata)

            if len(command['input']) > 2 and not command['input'][2]:
              command['input'][2] = bizdata
        
        del item['bizdata']

  @classmethod
  def _process_dict(cls, data: dict, alt_bizdata:dict = None):
    """Process dictionary data"""
    result = {}
    for key, value in data.items():
      result[key] = cls._process(value,alt_bizdata)  # Recursively process values through _process
    return result

  @classmethod
  def _process_list(cls, data: list, alt_bizdata:dict = None):
    """Process list data"""
    return [cls._process(item,alt_bizdata) for item in data]  # Recursively process items through _process

  @classmethod
  def _process(cls, value:Any, alt_bizdata:dict = None):

    """Central processing method that handles all value types"""
    # Check for __model__ pattern first (highest priority)
    if isinstance(value, list) and len(value) >= 2 and value[0] == '__model__':
      meta = value[1]
      # 1. 优先检查 value[2] 是否存在且为非空值
      if len(value) > 2 and value[2]:
        bizdata = value[2]
      # 2. 若 value[2] 不符合，则检查 alt_bizdata 是否为非空值
      elif alt_bizdata:
        bizdata = alt_bizdata
      # 3. 若前两者都为空值，则使用空字典兜底
      else:
        bizdata = {}
      return Model(meta, bizdata)
    
    # Handle dict processing
    elif isinstance(value, dict):
      return cls._process_dict(value,alt_bizdata)
    
    # Handle list processing
    elif isinstance(value, list):
      return cls._process_list(value,alt_bizdata)
    
    # Return all other types as-is
    else:
      return value
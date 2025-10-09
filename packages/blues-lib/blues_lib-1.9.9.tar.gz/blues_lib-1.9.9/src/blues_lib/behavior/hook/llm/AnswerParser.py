import json
from blues_lib.behavior.hook.BhvProcessor import BhvProcessor
from abc import abstractmethod

class AnswerParser(BhvProcessor):
  
  def execute(self)->list[dict]|None:
    f'''
    @description: convert the answer to mat dict
    @return {list[dict]|None} the mat dict list
    '''
    if not self._value:
      self._logger.error(f'[{self.__class__.__name__}] Bhv getter value is None')
      return self._value

    return self._convert(self._value )

  def _convert(self,answer:str)->list[dict]|None:
    '''
    将llm的json输出转为字典数组，如果初始是字典也转为列表(例如detail的提取初始只有单个字典)
    @param {str} answer : the llm answer json string
    @return {list[dict]|None} the mat dict list
    '''
    try:
      data:list[dict]|dict =  json.loads(answer)
      mats:list[dict] = data if isinstance(data,list) else [data]
      self._add_system_fields(mats)
      return self._extend_mat(mats)

    except Exception as error:
      self._logger.error(f'[{self.__class__.__name__}] Failed to load json {error}')
      return None

  @abstractmethod   
  def _add_system_fields(self,mats:list[dict])->None:
    pass
    
  def _extend_mat(self,mats:list[dict])->list[dict]:
    '''
    填充mat字典，添加缺失的字段
    @param {dict} mat : the mat dict
    @return {dict} the extended mat dict
    '''
    extend_mat:dict = self._proc_conf.get('extend',{})
    if not extend_mat:
      return mats
    
    extend_mats:list[dict] = []
    for mat in mats:
      # 合并extend_mat和mat，extend_mat的静态字段优先级更低
      merged_mat = {**extend_mat,**mat}
      extend_mats.append(merged_mat)
    return extend_mats

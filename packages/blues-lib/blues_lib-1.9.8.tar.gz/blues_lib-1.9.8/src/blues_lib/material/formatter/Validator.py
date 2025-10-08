import sys,os,re

from blues_lib.material.MatHandler import MatHandler
from blues_lib.type.output.STDOut import STDOut
from blues_lib.util.BluesType import BluesType

class Validator(MatHandler):
  
  REQUIRED_BRIEF_FIELDS = ['mat_id','mat_title']
  REQUIRED_DETAIL_FIELDS = ['mat_id','mat_title','mat_paras']

  def resolve(self):
    self._setup()
    avail_entities = []

    for entity in self._entities:
      if not self._is_field_satisfied(entity):
        self._mark(entity)
        self._logger.warning(f'[{self.__class__.__name__}] Skip a field-not-satisfied entity')
      elif not self._is_length_valid(entity):
        self._mark(entity)
        self._logger.warning(f'[{self.__class__.__name__}] Skip a content-too-long-or-short entity')
      else:
        avail_entities.append(entity)

    self._request['entities'] = avail_entities
    stdout = STDOut(200,'ok',avail_entities) if avail_entities else STDOut(500,'all are invalid')
    self._log(stdout)
    return stdout
    
  def _is_field_satisfied(self,entity)->bool:
    fields = None
    if entity.get('mat_paras'):
      fields = self.REQUIRED_DETAIL_FIELDS
    else:
      fields = self.REQUIRED_BRIEF_FIELDS
    return BluesType.is_field_satisfied_dict(entity,fields,True)

  def _is_length_valid(self,entity:dict)->bool:
    if not entity.get('mat_title'):
      return False

    if not entity.get('mat_paras'):
      return True

    config = self._config.get('formatter')
    if not config:
      return True

    text_length = self._get_text_length(entity)

    min_text_length:int = int(config.get('min_text_length',0))
    if min_text_length and text_length<min_text_length:
      return False

    max_text_length:int = int(config.get('max_text_length',0))
    if max_text_length and text_length>max_text_length:
      return False

    return True
  
  def _get_text_length(self,entity:dict)->int:
    paras:list[str] = entity.get('mat_paras')
    size = 0

    if not paras:
      return size

    # a error: [{'type': 'text', 'value': None}] 
    for para in paras:
      p_type = para.get('type')
      p_value = para.get('value')  or '' # must be a str
      if p_type == 'text':
        size+=len(p_value)
    return size
    
    



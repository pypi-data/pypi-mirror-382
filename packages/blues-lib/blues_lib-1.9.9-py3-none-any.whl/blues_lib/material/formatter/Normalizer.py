import sys,os,re
from typing import List

from blues_lib.type.output.STDOut import STDOut
from blues_lib.util.BluesAlgorithm import BluesAlgorithm 
from blues_lib.util.BluesURL import BluesURL
from blues_lib.material.MatHandler import MatHandler

class Normalizer(MatHandler):

  def resolve(self)->STDOut:
    self._setup()
    avail_entities = []

    try:
      for entity in self._entities:
        stdout = self._get_entity_error(entity)
        if stdout.code==200:
          self._normalize(entity)
          avail_entities.append(entity)
        else:
          self._mark(entity)
          self._logger.warning(f'[{self.__class__.__name__}] Skip a invalid entity - {entity["mat_title"]} - {stdout.message}')

      self._request['entities'] = avail_entities
      stdout = STDOut(200,'ok',avail_entities) if avail_entities else STDOut(500,'all are invalid')
      self._log(stdout)
      return stdout

    except Exception as e:
      message = f'[{self.__class__.__name__}] Failed to normalized any entities - {e}'
      self._logger.error(message)
      return STDOut(500,message)
    
  def _get_entity_error(self,entity:dict):
    if not entity.get('mat_title'):
      return STDOut(400,'Received an empty mat_title')
    return STDOut(200,'ok')

  def _normalize(self,entity):
    self._set_system_fileds(entity)
    # set for detail only
    self._set_paras(entity)
  
  def _set_system_fileds(self,entity):
    config = self._config.get('formatter',{})
    
    url_site = BluesURL.get_main_domain(entity['mat_url']) if entity.get('mat_url') else ''
    url_id = BluesAlgorithm.md5(entity['mat_url']) if entity.get('mat_url') else ''
    title_id = BluesAlgorithm.md5(entity['mat_title'])
    entity.setdefault('mat_chan',config.get('chan') or 'article')  # article gallery shortvideo qa
    entity.setdefault('mat_lang',config.get('lang') or 'cn') # cn en
    entity.setdefault('mat_site',config.get('site') or url_site)  # cn en
    entity.setdefault('mat_id',url_id or title_id) # md5 优先使用url生成id，避免值变动不一致

  def _set_paras(self,entity:dict):
    rows = entity.get('mat_paras')
    if not rows:
      return
    
    # 如果是llm获取的就是结构化数组无需转换
    if rows[0].get('type'):
      return

    paras:List[dict] = []
    for row in rows: 
      image = row.get('image')
      text = row.get('text')
      if image:
        paras.append({'type':'image','value':image})
      else:
        paras.append({'type':'text','value':text})
    entity['mat_paras'] = paras


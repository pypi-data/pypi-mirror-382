import sys,os,re

from blues_lib.material.MatHandler import MatHandler
from blues_lib.type.output.STDOut import STDOut
from blues_lib.dao.material.MatQuerier import MatQuerier

class Deduplicator(MatHandler):

  def resolve(self):
    self._setup()
    avail_entities = []
    querier = MatQuerier()

    for entity in self._entities:
      if querier.exist(entity['mat_id']):
        self._logger.warning(f'[{self.__class__.__name__}] Skip a existing entity - {entity["mat_title"]}')
      else:
        avail_entities.append(entity)

    self._request['entities'] = avail_entities
    stdout = STDOut(200,'ok',avail_entities) if avail_entities else STDOut(500,'all are duplicated')
    self._log(stdout)
    return stdout